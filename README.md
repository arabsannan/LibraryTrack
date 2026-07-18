## LibraryTrack

One catalogue shared across a network of libraries. A book is stored once by its
ISBN; each branch tracks its own copies. Members browse the whole network, borrow,
and donate. Branch admins manage their own shelf.

Django 6 · Bootstrap 5 (CDN) · SQLite.

### Run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata catalog/fixtures/catalog_seed.json
python manage.py loaddata accounts/fixtures/demo_accounts.json
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

### What the loaddata lines do

`loaddata` fills the empty database with starter data from a fixture (a JSON file
of rows). You run each one once, after `migrate`:

- `catalog_seed.json` — 40 books, 4 libraries, genres, and per-library stock.
- `demo_accounts.json` — two ready sign-ins so you can try both sides.

You pass the path to the file. `python manage.py loaddata catalog_seed` (no path,
no `.json`) also works only because Django searches every app's `fixtures/`
folder — but passing the full path is clearer and never ambiguous.

The database (`db.sqlite3`) already ships seeded, so if you just want to run it you
can skip the two `loaddata` lines. Run them only when starting from an empty DB.

### Signing in

- Member — `member` / `member12345` -> lands on the catalogue.
- Branch admin — `admin` / `admin12345` -> lands on the library console (manages
  Windsor Central Library).

Password-reset links print to the terminal running the server.

### Running as a library admin

A user becomes a branch admin when a `LibraryAdmin` row links them to one branch.
There is no self-serve admin sign-up — this is deliberate, the same way a real
library wouldn't let anyone make themselves staff. Once linked, that user is sent
straight to the admin console on login and sees a "Manage" link in the nav.

To try it now: log in as `admin` / `admin12345`.

To make one of your own accounts an admin, use the built-in command:

```bash
python manage.py make_admin <username> "<branch name>"
# e.g.
python manage.py make_admin alice "Riverside Library"
```

Library names are: Windsor Central Library, Riverside Library, Sandwich Library,
Fontainebleau Library. Log out and back in, and that account lands on the console.

(You can also do this through Django's own admin site at `/admin/` — create a
superuser with `python manage.py createsuperuser`, log in, open "Library admins",
and add a row linking the user to a branch. The command just saves those clicks.)

### Book covers

Covers load automatically from the Open Library Covers API using each book's
ISBN, no downloads or keys. If Open Library doesn't have a cover for a title, the
card falls back to a coloured cover with the title on it. To pin a specific cover,
upload an image to a book's `cover_image` field in `/admin/`; that always wins.

### Email and notifications

Approvals, rejections, and waitlist openings create an in-app notification and
email the user. Out of the box emails print to the terminal (console backend), so
you can read them without any setup. To send real test emails through Mailtrap's
sandbox, set these before running the server:

```bash
export EMAIL_HOST_USER=<your mailtrap username>
export EMAIL_HOST_PASSWORD=<your mailtrap password>
# EMAIL_HOST defaults to sandbox.smtp.mailtrap.io, EMAIL_PORT to 2525
```

Password-reset links are emailed the same way. Reset links are single use: once
you open one it can't be reused, and the page then offers to send a fresh link.

### Managing a library (admin)

From the admin console an admin can:

- Add a book with full details and a starting number of copies ("Add a book").
- Increase or decrease the copies of any title stocked, from the inventory table.
  Copies on loan can't be removed until they're returned.
- Approve or decline borrow, donation, and purchase requests, each of which
  emails the user with next steps.


### What's inside

Accounts — registration, login, profiles, and password reset.
Catalogue — the public book list, search, filters, and detail pages.
Borrowing — the borrow lifecycle: request, approve, return, overdue, waitlist.
Requests — donations, purchase requests, and the About / Team / Contact pages.
Dashboard — the member view and the library-admin view.

For a full map of the codebase, see `ARCHITECTURE.md`.

### Tests

```bash
python manage.py test
```
