# Student Main Portal

A Flask web application for capturing student applications and managing admission decisions. Students submit personal and academic details through a form, staff browse and filter the resulting records, and admission status can be changed from a student's profile page without a page reload.

Capstone project for the Startocode Fullstack Python Developer track.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create the database. This builds `instance/portal.db` from `schema.sql`:

```bash
python3 -c "import database; database.init_db()"
```

Running that command again drops and rebuilds the `students` table, so only use it for a first setup or a deliberate reset.

Start the app:

```bash
flask --app app run --debug
```

It serves at `http://127.0.0.1:5000`.

## Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Landing page with the call to action |
| `/apply` | GET | Renders the application form |
| `/apply` | POST | Validates, saves the photo, inserts the record |
| `/students` | GET | Table of all students, with search and filters |
| `/students/<id>` | GET | Full profile for one student |
| `/students/<id>/status` | POST | Updates admission status, returns JSON |

## Project structure

```
app.py           Routes only
database.py      Every SQL query in the project
validators.py    Server-side form validation
schema.sql       Table definition
templates/       Jinja2 templates, all extending base.html
static/css/      style.css
static/js/       states.js, form-validate.js, status-update.js
static/data/     states-lgas.json, fetched at runtime by states.js
static/uploads/  Where submitted photos are written
static/images/   classroom.svg for the landing page
```

Each Python module has one job. `app.py` reads the request, calls a named function, and renders or redirects. It contains no SQL and no validation logic. `database.py` holds every query, so changing how data is stored means editing one file. `validators.py` returns a dict of field names to error messages, which the form template renders inline.

`base.html` carries the navbar and footer, and the four page templates extend it. The shared header and footer requirement is handled by template inheritance rather than by repeating markup.

## Asynchronous behaviour

Two parts of the app work without a page reload.

**State and local government selects.** `states.js` fetches `static/data/states-lgas.json` on page load and fills the state dropdown from it. Picking a state repopulates the local government dropdown with only that state's LGAs. Nothing is hardcoded into the HTML, so updating the data file is enough to change the options.

**Admission status changes.** On a student's profile, choosing a new status sends a POST to `/students/<id>/status` with a JSON body. The route validates the value against the allowed list, updates the row, and returns JSON. `status-update.js` then rewrites the badge and status text in place and reports success or failure next to the select.

## Validation

Every field is checked twice, in two different places, for two different reasons.

`form-validate.js` runs on submit and blocks the request if something is missing or malformed. This exists for the person filling in the form, so they get feedback without a round trip.

`validators.py` re-checks everything after the request arrives. This exists because the client cannot be trusted. Disabling JavaScript, editing the DOM, or POSTing directly with curl all bypass the browser checks, and none of them bypass the server ones. If validation fails, the form re-renders with the submitted values still in place and the errors shown per field, so nothing has to be retyped.

Checks applied: required fields, email format, date of birth not in the future, gender restricted to the allowed values, JAMB score numeric and within 0 to 400, and an uploaded image with a permitted extension.

## Image uploads

Photos are saved to `static/uploads/` under a generated UUID filename, and only that filename is stored in the database. Keeping the original name would mean two students who both upload `photo.jpg` overwrite each other, and it would put user-controlled text into a filesystem path. Uploads are capped at 5 MB and restricted to PNG, JPG, JPEG, GIF and WEBP.

## Database

One table. `admission_status` defaults to `undecided` and is constrained at the database level to `admitted`, `rejected` or `undecided`, so an invalid value cannot be written even if a bug in the application layer tries. Gender is constrained the same way.

Search on the students page builds its query from whichever filters were actually supplied, skipping the empty ones, so the same function handles an unfiltered listing and a four-filter search.

## Known limitations

- There is no authentication. Anyone who can reach `/students` can read every record and change admission decisions. A real deployment needs a login and a staff role before it goes anywhere near real applicant data.
- `app.secret_key` is a hardcoded development value and must be replaced with an environment variable in production.
- The dev server is Flask's built-in one, which is not meant for production. A real deployment would run behind Gunicorn or similar.
- Uploaded files are served straight from the static directory with no access control, so anyone with the URL can view any photo.
- There is no pagination on the students table, so it will get slow once the record count grows.
