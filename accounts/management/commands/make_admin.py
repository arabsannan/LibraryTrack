from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from accounts.models import LibraryAdmin
from catalog.models import Library


class Command(BaseCommand):
    help = "Make an existing user the admin of a library branch."

    def add_arguments(self, parser):
        parser.add_argument("username", help="The user to promote.")
        parser.add_argument("library", help="The exact branch name, in quotes.")

    def handle(self, *args, **options):
        username = options["username"]
        library_name = options["library"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'No user named "{username}". Create the account first.')

        try:
            library = Library.objects.get(name=library_name)
        except Library.DoesNotExist:
            names = ", ".join(Library.objects.values_list("name", flat=True))
            raise CommandError(f'No branch named "{library_name}". Available: {names}')

        admin, created = LibraryAdmin.objects.get_or_create(
            user=user, defaults={"library": library}
        )
        if not created:
            admin.library = library
            admin.save()

        verb = "is now" if created else "was updated to be"
        self.stdout.write(self.style.SUCCESS(f'"{username}" {verb} the admin of {library.name}.'))
