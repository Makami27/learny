# LessonHub — Private Lesson Teacher Hiring & Scheduling Platform

LessonHub is a Django web app that connects **parents/guardians** with **private
lesson teachers** (music, sports, tutoring, art, etc.) for their children. Parents
can browse teacher profiles, book lesson slots, and manage their children's
schedules. Teachers can create a profile, set their hourly rate and weekly
availability, and accept/decline booking requests. Admins can verify (background
check) teachers before they go live, keeping the platform safe for kids.

## Core features

- **Custom user model** with three roles: `parent`, `teacher`, `admin`.
- **Teacher profiles**: subject taught, bio, hourly rate, years of experience,
  a `is_verified` flag (only verified teachers are publicly bookable), and a
  photo.
- **Availability slots**: teachers publish recurring weekly time slots they're
  free to teach.
- **Children**: parents register their children (name, age, notes e.g.
  allergies/learning needs).
- **Bookings**: parents request a lesson for a child with a teacher at a
  specific available slot/date. Status flow:
  `pending → confirmed → completed` or `pending → declined` /
  `confirmed → cancelled`.
- **Reviews**: parents can rate & review a teacher after a completed lesson.
- **Dashboards**: separate dashboards for parents (their children & bookings)
  and teachers (their schedule & requests), plus Django admin for staff.
- **Search/browse**: filter teachers by subject and verification status.

## Tech stack

- Python 3.10+
- Django 5.x
- SQLite (default, zero-config — swap for Postgres in production)
- Bootstrap 5 (via CDN) for quick, clean styling

## Project layout

```
lessonhub/
├── manage.py
├── requirements.txt
├── lessonhub/          # project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
└── booking/             # the single app holding all logic
    ├── models.py        # User, TeacherProfile, Availability, Child, Booking, Review
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── signals.py
    └── templates/booking/*.html
```

## Setup

```bash
cd lessonhub
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # create an admin account

python manage.py runserver
```

Visit:
- `http://127.0.0.1:8000/` — public home / teacher browse
- `http://127.0.0.1:8000/accounts/signup/` — register as parent or teacher
- `http://127.0.0.1:8000/admin/` — Django admin (verify teachers here)

## How the hiring flow works

1. A **teacher** signs up, fills out their `TeacherProfile` (subject, rate,
   bio) and adds weekly `Availability` slots.
2. An **admin** reviews and marks the teacher `is_verified=True` in the
   admin panel (simulating a background-check/vetting step).
3. A **parent** signs up, adds one or more `Child` records, browses verified
   teachers by subject, and submits a `Booking` request against an open
   availability slot.
4. The **teacher** sees the pending request on their dashboard and accepts
   or declines it. Accepting marks the slot booked for that date.
5. After the lesson date passes, either side can mark it `completed`, and
   the parent can leave a `Review` (star rating + comment) for the teacher.

This file is also included as `README.md` inside the project zip.
