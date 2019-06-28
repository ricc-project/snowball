from .models import Station, Actuator, Central
from boogie.rest import rest_api

@rest_api.property('ricc.models.Central')
def station_count(central):
    return central.station_count

@rest_api.property('ricc.models.Central')
def actuator_count(central):
    return central.actuator_count()
