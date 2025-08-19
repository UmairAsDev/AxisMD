uvicorn main:app --host localhost --port 8000 --reload

{
  "username": "@johndoe",
  "first_name": "umair",
  "last_name": "ashraf",
  "email": "johndoe@gmail.com",
  "phone_number": "string",
  "password": "okbye0312@",
  "confirm_password": "okbye0312@"
}

SELECT u.* FROM "AxisMD".users AS u

alembic init migrations
alembic revision --autogenerate -m "create tables in AxisMD"
alembic upgrade head