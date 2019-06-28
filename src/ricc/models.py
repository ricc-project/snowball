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

    def station_count(self):
        return Station.objects.filter(central=self).count()

    def actuator_count(self):
        return Actuator.objects.filter(central=self).count()

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
    status = models.BooleanField('Network Status', default=True)
    
    def switch(self):
        self.status = not self.status

@rest_api(exclude=['data_token'])
class Actuator(Node):
    objects = ActuatorManager()

@rest_api(exclude=['data_token'])
class Station(Node):
    objects = StationManager()
    sensors = ['soil','wind','air','solar','rain']