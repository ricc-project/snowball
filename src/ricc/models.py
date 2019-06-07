from django.db import models
from .manager import UserManager, CentralManager, ActuatorManager, StationManager, UnlockedCentralManager
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
    mac_address = models.CharField(max_length=64, unique=True)
    automatic_irrigation = models.BooleanField('Automatic Irrigation Status')
    objects = CentralManager()

@rest_api()
class UnlockedCentral(models.Model):
    mac_address = models.CharField(max_length=64, unique=True)
    objects = UnlockedCentralManager()

class Node(models.Model):
    class Meta:
        abstract = True
    central = models.ForeignKey(Central, related_name='%(class)s', on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True)
    data_token = models.CharField(max_length=64)

@rest_api(exclude=['data_token'])
class Actuator(Node):
    status = models.BooleanField('Actuator Status')
    objects = ActuatorManager()

@rest_api(exclude=['data_token'])
class Station(Node):
    objects = StationManager()
    sensors = ['soil','wind','air','solar','rain']