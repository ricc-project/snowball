from django.db import models
from .manager import UserManager
from boogie.rest import rest_api

@rest_api(exclude=['hash','auth_token'])
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    hash = models.CharField(max_length=128)
    auth_token = models.CharField(max_length=64)
    objects = UserManager()
    def __str__(self):
        return self.username

@rest_api()
class Central(models.Model):
    owner = models.ForeignKey(User, related_name="centrals", on_delete=models.CASCADE)
    mac_address = models.CharField(max_length=64)
    automatic_irrigation = models.BooleanField('Automatic Irrigation Status')

class Node(models.Model):
    class Meta:
        abstract = True

    central = models.ForeignKey(Central, related_name='%(class)s', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    data_token = models.CharField(max_length=64)

@rest_api(exclude=['data_token'])
class Actuator(Node):
    status = models.BooleanField('Actuator Status')

@rest_api(exclude=['data_token'])
class Station(Node):
    sensors = ['soil','wind','air','solar','rain']