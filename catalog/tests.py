from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Book, BookInventory, Genre, Library


class GenreModelTests(TestCase):
    def test_str_returns_name(self):
        genre = Genre.objects.create(name="Fantasy")
        self.assertEqual(str(genre), "Fantasy")

    def test_name_must_be_unique(self):
        Genre.objects.create(name="Sci-Fi")
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name="Sci-Fi")


class BookModelTests(TestCase):
    def test_str_includes_title_and_isbn(self):
        book = Book.objects.create(isbn="123", title="Dune", author="Herbert")
        self.assertEqual(str(book), "Dune (123)")

    def test_isbn_must_be_unique(self):
        Book.objects.create(isbn="123", title="Dune", author="Herbert")
        with self.assertRaises(IntegrityError):
            Book.objects.create(isbn="123", title="Different Book", author="Someone")

    def test_book_can_have_multiple_genres(self):
        book = Book.objects.create(isbn="123", title="Dune", author="Herbert")
        scifi = Genre.objects.create(name="Sci-Fi")
        adventure = Genre.objects.create(name="Adventure")
        book.genres.set([scifi, adventure])
        self.assertEqual(book.genres.count(), 2)


class BookInventoryModelTests(TestCase):
    def setUp(self):
        self.library = Library.objects.create(name="Central")
        self.book = Book.objects.create(isbn="123", title="Dune", author="Herbert")

    def test_unique_book_per_library(self):
        BookInventory.objects.create(book=self.book, library=self.library, total_copies=3, available_copies=3)
        with self.assertRaises(IntegrityError):
            BookInventory.objects.create(book=self.book, library=self.library, total_copies=1, available_copies=1)

    def test_available_copies_clamped_to_total(self):
        inv = BookInventory.objects.create(
            book=self.book, library=self.library, total_copies=2, available_copies=10
        )
        inv.refresh_from_db()
        self.assertEqual(inv.available_copies, 2)


class HomeViewSearchTests(TestCase):
    def setUp(self):
        self.lib_a = Library.objects.create(name="Downtown")
        self.lib_b = Library.objects.create(name="Uptown")

        self.scifi = Genre.objects.create(name="Sci-Fi")
        self.fantasy = Genre.objects.create(name="Fantasy")
        self.adventure = Genre.objects.create(name="Adventure")

        self.dune = Book.objects.create(isbn="111", title="Dune", author="Frank Herbert")
        self.dune.genres.set([self.scifi, self.adventure])
        self.hobbit = Book.objects.create(isbn="222", title="The Hobbit", author="Tolkien")
        self.hobbit.genres.set([self.fantasy, self.adventure])

        BookInventory.objects.create(book=self.dune, library=self.lib_a, total_copies=3, available_copies=3)
        BookInventory.objects.create(book=self.dune, library=self.lib_b, total_copies=2, available_copies=0)
        BookInventory.objects.create(book=self.hobbit, library=self.lib_a, total_copies=1, available_copies=1)

        self.url = reverse("catalog:home")

    def _titles(self, response):
        return sorted(b.title for b in response.context["books"])

    def test_no_query_returns_all_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._titles(response), ["Dune", "The Hobbit"])

    def test_search_by_title(self):
        response = self.client.get(self.url, {"q": "dune"})
        self.assertEqual(self._titles(response), ["Dune"])

    def test_search_by_author(self):
        response = self.client.get(self.url, {"q": "tolkien"})
        self.assertEqual(self._titles(response), ["The Hobbit"])

    def test_search_by_isbn(self):
        response = self.client.get(self.url, {"q": "111"})
        self.assertEqual(self._titles(response), ["Dune"])

    def test_filter_by_genre_matches_multiple_books(self):
        response = self.client.get(self.url, {"genre": "Adventure"})
        self.assertEqual(self._titles(response), ["Dune", "The Hobbit"])

    def test_filter_by_genre_matches_single_book(self):
        response = self.client.get(self.url, {"genre": "Fantasy"})
        self.assertEqual(self._titles(response), ["The Hobbit"])

    def test_filter_by_library(self):
        response = self.client.get(self.url, {"library": "Uptown"})
        self.assertEqual(self._titles(response), ["Dune"])

    def test_filter_by_availability(self):
        response = self.client.get(self.url, {"availability": "available"})
        self.assertEqual(self._titles(response), ["Dune", "The Hobbit"])

    def test_results_are_deduplicated(self):
        response = self.client.get(self.url, {"q": "e"})
        titles = [b.title for b in response.context["books"]]
        self.assertEqual(len(titles), len(set(titles)))

    def test_genre_dropdown_lists_all_genres(self):
        response = self.client.get(self.url)
        self.assertEqual(sorted(response.context["genres"]), ["Adventure", "Fantasy", "Sci-Fi"])


class BookDetailViewTests(TestCase):
    def setUp(self):
        self.library = Library.objects.create(name="Central")
        self.scifi = Genre.objects.create(name="Sci-Fi")
        self.dune = Book.objects.create(isbn="111", title="Dune", author="Frank Herbert")
        self.dune.genres.add(self.scifi)
        self.hobbit = Book.objects.create(isbn="222", title="The Hobbit", author="Tolkien")
        BookInventory.objects.create(book=self.dune, library=self.library, total_copies=3, available_copies=3)

    def test_detail_page_loads(self):
        response = self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["book"], self.dune)

    def test_detail_shows_inventory(self):
        response = self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        inventories = list(response.context["inventories"])
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].library.name, "Central")

    def test_recently_viewed_tracks_visited_books(self):
        self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        response = self.client.get(reverse("catalog:book_detail", args=[self.hobbit.isbn]))
        recent = [b.isbn for b in response.context["recently_viewed_books"]]
        self.assertIn("111", recent)
        self.assertIn("222", recent)

    def test_recently_viewed_has_no_duplicates(self):
        self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        response = self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        recent = [b.isbn for b in response.context["recently_viewed_books"]]
        self.assertEqual(recent.count("111"), 1)


class PaginationTests(TestCase):
    def setUp(self):
        self.library = Library.objects.create(name="Central")
        for i in range(30):
            book = Book.objects.create(isbn=f"isbn-{i:03d}", title=f"Book {i:03d}", author="Author")
            BookInventory.objects.create(
                book=book, library=self.library, total_copies=2, available_copies=2
            )
        self.url = reverse("catalog:home")

    def test_first_page_is_capped(self):
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["books"]), 12)
        self.assertEqual(response.context["paginator"].count, 30)
        self.assertEqual(response.context["paginator"].num_pages, 3)

    def test_last_page_has_remainder(self):
        response = self.client.get(self.url, {"page": 3})
        self.assertEqual(len(response.context["books"]), 6)

    def test_first_page_renders_without_previous_link(self):
        # Guards against EmptyPage being raised by previous_page_number on page 1.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_last_page_renders_without_next_link(self):
        response = self.client.get(self.url, {"page": 3})
        self.assertEqual(response.status_code, 200)

    def test_out_of_range_page_returns_404(self):
        response = self.client.get(self.url, {"page": 99})
        self.assertEqual(response.status_code, 404)

    def test_filters_survive_pagination(self):
        response = self.client.get(self.url, {"q": "Book 0", "page": 1})
        self.assertContains(response, "q=Book+0")


class TemplateRenderingTests(TestCase):
    """Assert on rendered HTML, not just context.

    The view context can be correct while the template reads a field that no
    longer exists -- Django templates fail silently, so only rendering catches it.
    """

    def setUp(self):
        self.library = Library.objects.create(name="Central")
        self.scifi = Genre.objects.create(name="Sci-Fi")
        self.adventure = Genre.objects.create(name="Adventure")
        self.dune = Book.objects.create(isbn="111", title="Dune", author="Frank Herbert")
        self.dune.genres.set([self.scifi, self.adventure])
        BookInventory.objects.create(
            book=self.dune, library=self.library, total_copies=3, available_copies=3
        )

    def test_detail_page_renders_every_genre(self):
        response = self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        self.assertContains(response, "Sci-Fi")
        self.assertContains(response, "Adventure")

    def test_detail_page_does_not_claim_genres_are_unset(self):
        response = self.client.get(reverse("catalog:book_detail", args=[self.dune.isbn]))
        self.assertNotContains(response, "No genres set")

    def test_book_with_no_genres_shows_placeholder(self):
        bare = Book.objects.create(isbn="999", title="Untagged", author="Nobody")
        response = self.client.get(reverse("catalog:book_detail", args=[bare.isbn]))
        self.assertContains(response, "No genres set")

    def test_list_page_renders_genre_badges(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, "Sci-Fi")
        self.assertContains(response, "Adventure")

    def test_list_page_renders_availability(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, "Central")
        self.assertContains(response, "3/3 available")