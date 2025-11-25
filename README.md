# Graduation Ceremony System (Django)

Features:

- Grad Admin dashboard (default home page)
  - Total students
  - Checked in count
  - Gown collected count
  - Ordered for stage count
  - Full list of students with click-through detail
- Student detail page
  - Shows booking info
  - Edit attendance, gown status, and stage order in one place
- Mobile-friendly check-in screen
- Mobile-friendly gown desk screen
- Stage control page to step through students in order
- Stage display page for the big screen
- CSV import command for loading data from your Excel bookings

## Quick start

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

Run the server:

```bash
python manage.py runserver
```

Main URLs:

- Grad Admin dashboard (default): http://127.0.0.1:8000/
- Student detail: http://127.0.0.1:8000/students/<id>/
- Check-in: http://127.0.0.1:8000/check-in/
- Gown desk: http://127.0.0.1:8000/gowns/
- Stage control: http://127.0.0.1:8000/stage/control/
- Stage display: http://127.0.0.1:8000/stage/display/

## Importing your CSV

Export your Excel sheet to CSV and run:

```bash
python manage.py import_graduates "path/to/your/bookings.csv"
```

Rows are matched by **Unique ID** and updated if they already exist, or created if new.
