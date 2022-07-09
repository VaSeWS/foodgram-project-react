# Foodgram

Site for sharing recipes, backend written on Django and Django REST Framework.
Backend part of the project was written as Yandex Practicum graduation project.

Python 3.9, Django 4.0, DRF 3.13.1

### Launching
To launch the project docker is requered. Use `docker-compose up` command. Project will be available at `localhost`.
You might also want to load test data via `docker-compose exec backend python manage.py loaddata dbdump.json`.
To populate ingredients only use `docker-compose exec backend python manage.py populate_ingredients ingredients.csv`.


### Backend endpoints
Documentation for backend's endpoints can be accessed at `http://localhost/api/docs/redoc.html` after launching project in docker.

### Functionality 
| Unauthorized users | Authorized users | Admin |
|--|--|--|
| Browse recipes | Browse recipes | All that authorized users can do |
Register | Create and edit own recipes | Access to admin panel |
Login  | Add recipes to favorite/shopping list | |
| | Export shopping list to txt | |
| | Subscribe to other users | |
