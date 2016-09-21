# uWSGI serving a django-shop application

This Dockerfile builds the base image for all projects using **djangoSHOP**:

```
docker build -t uwsgi-django-shop .
```

This image requires **fedora-uwsgi-python** and provides a base image for the merchant's
implementation.
