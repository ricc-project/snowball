from django.db import models
from .manager import UserManager
from boogie.rest import rest_api

@rest_api(exclude=['hash','auth_token'])
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    hash = models.CharField(max_length=128)
    auth_token = models.CharField(max_length=64)
    objects = UserManager()
