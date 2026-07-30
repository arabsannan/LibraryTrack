from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Book, Genre, Library

class HomeView(ListView):
	model = Book
	template_name = "catalog/home.html"
	context_object_name = "books"
	paginate_by = 12

	def dispatch(self, request, *args, **kwargs):
		# Session visit tracking is a personalised feature, so we only count
		# visits for signed-in users.
		if request.user.is_authenticated:
			request.session["visit_count"] = request.session.get("visit_count", 0) + 1
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		queryset = Book.objects.prefetch_related("genres", "inventories__library")
		query = self.request.GET.get("q", "").strip()
		genre = self.request.GET.get("genre", "").strip()
		library = self.request.GET.get("library", "").strip()
		availability = self.request.GET.get("availability", "").strip()

		if query:
			queryset = queryset.filter(
				Q(title__icontains=query)
				| Q(author__icontains=query)
				| Q(isbn__icontains=query)
				| Q(genres__name__icontains=query)
				| Q(inventories__library__name__icontains=query)
			)
		if genre:
			queryset = queryset.filter(genres__name__icontains=genre)
		if library:
			queryset = queryset.filter(inventories__library__name__icontains=library)
		if availability == "available":
			queryset = queryset.filter(inventories__available_copies__gt=0)

		return queryset.distinct()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["libraries"] = Library.objects.all()
		context["genres"] = Genre.objects.values_list("name", flat=True)
		context["query_params"] = self.request.GET
		# Preserve active filters across pagination links (drops the page param).
		params = self.request.GET.copy()
		params.pop("page", None)
		context["querystring"] = params.urlencode()
		return context


class BookDetailView(DetailView):
	model = Book
	template_name = "catalog/book_detail.html"
	context_object_name = "book"
	slug_field = "isbn"
	slug_url_kwarg = "isbn"

	def get_object(self, queryset=None):
		return Book.objects.prefetch_related("genres", "inventories__library").get(isbn=self.kwargs["isbn"])

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["inventories"] = self.object.inventories.select_related("library")

		# Which of this book's inventories is the current user already waitlisted on,
		# and which do they already have an active request for? Used to show
		# "Joined" / "Pending" states instead of the action buttons.
		if self.request.user.is_authenticated:
			from borrowing.models import BorrowRecord, WaitlistEntry
			context["waitlisted_ids"] = set(
				WaitlistEntry.objects.filter(
					user=self.request.user,
					book_inventory__book=self.object,
				).values_list("book_inventory_id", flat=True)
			)
			context["borrow_status"] = dict(
				BorrowRecord.objects.filter(
					user=self.request.user,
					book_inventory__book=self.object,
					status__in=["pending", "approved", "overdue"],
				).values_list("book_inventory_id", "status")
			)
		else:
			context["waitlisted_ids"] = set()
			context["borrow_status"] = {}

		recently_viewed = self.request.session.get("recently_viewed_books", [])
		recently_viewed = [isbn for isbn in recently_viewed if isbn != self.object.isbn]
		recently_viewed.insert(0, self.object.isbn)
		recent_isbns = recently_viewed[:5]

		self.request.session["recently_viewed_books"] = recent_isbns

		#Tells Django the session list was changed
		self.request.session.modified = True

		# Fetch matching records from the database
		book_query = Book.objects.filter(isbn__in=recent_isbns)

		# Map books to preserve exact user timeline ordering
		book_map = {book.isbn: book for book in book_query}
		context["recently_viewed_books"] = [
			book_map[isbn] for isbn in recent_isbns if isbn in book_map
		]

		return context