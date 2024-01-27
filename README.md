### run postgres for local purposes 
 `docker run -d -p 5432:5432 --name mycars -e POSTGRES_PASSWORD=postgres postgres`
to run  app locally setup proper postgres host

```
# python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --email admin@example.com --username admin
```

## run
`docker-compose up`

# warning
project in development stage, reset and make confidential db config, use production server


#### todo:
- external e2e tests, unit tests
- authorization


 
