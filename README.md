note: these steps were the results from ChatGPT

###Prerequisites:
1. python 3.10+
2. pip(comes with Python)

###Step 1: Create a virtual environment in vs code (Windows):
type the following:
1. python -m venv venv
2.  venv\Scripts\activate

###Step 2: Install dependencies:
type the following:
pip install -r requirements.txt

###Step 3: Set the database:
type the following:
1. python manage.py makemigrations
2. python manage.py migrate

###Step 4: Create superuser:
type the following:
python manage.py createsuperuser

###Step 5: Collect static file:
type the following:
python manage.py collectstatic

###Step 6: Run the server:
type the following:
python manage.py runserver

