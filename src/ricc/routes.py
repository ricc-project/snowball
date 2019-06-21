import hashlib, binascii, requests, json, functools
from rest_framework import status
from boogie.router import Router
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import User, Station, Central, Actuator, UnlockedCentral
from .manager import verify_password
from .data_api import create_user_on_data_api, send_data
import json

urlpatterns = Router()

@urlpatterns.route("signup/")
def signup(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(request.method == "POST"):
        data = json.loads(request.body)
        if data.keys() >= {"username", "password"}:
            username = data['username']
            password = data['password']
            user = User.objects.create_user(username, password)
            if(user):
                response = {"authentication_token": user.auth_token}
                response = json.dumps(response)
                response = json.loads(response)

                rstatus = status.HTTP_201_CREATED
            else:
                response = {"message": "username already taken"}
        else:
            response = {
                "message": "You need to send password and username."}
    else:
        response = {"message": "Can't signup with GET method."}

    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("login/")
def login(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(request.method == "POST"):
        data = json.loads(request.body)
        if data.keys() >= {"username", "password"}:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            user = None
            try:
                user = User.objects.get(username=username)
            except:
                response = response = {"message": "Invalid login information."}

            if(verify_password(user, password)):
                response = {"authentication_token": user.auth_token}
                rstatus = status.HTTP_202_ACCEPTED
            else:
                response = {"message": "Invalid login information."}
    else:
        response = {
            "message":
            "No username or Password, maybe not a POST method."}

    response = json.dumps(response)
    return HttpResponse(str(response), status=rstatus)

@urlpatterns.route("create_central/")
def create_central(request):
    user = verify_auth(request)
    if(user):
        mac_address = json.loads(request.body)['mac_address']
        unlockedCentrals = UnlockedCentral.objects.filter(mac_address=mac_address)
        if(unlockedCentrals):
            model = Central.objects.create_central(user, mac_address)
            if(model):
                return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
            else:
                return HttpResponse("Mac already used.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("call/")
def socket_call(request):
    mac_address = request.GET.get('mac','LIXODEFAULT')
    mac_address = mac_address.replace('-',':')
    centrals = Central.objects.filter(mac_address=mac_address)
    if centrals:
        token = centrals.first().owner.auth_token
        return HttpResponse('{"auth_token":' + '"' + token + '"}', status=status.HTTP_200_OK)    
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("sign_central/")
def sign_central(request):
    # user = verify_auth(request)
    # if(user):
    mac_address = json.loads(request.body)['mac_address']
    model = UnlockedCentral.objects.create_central(mac_address)
    if(model):
        return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
    else:
        return HttpResponse("Mac in use.", status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("create_station/")
def create_station(request):
    user = verify_auth(request)
    if(user):
        name = json.loads(request.body)['name']
        central = get_central(request)
        if(central):
            node_authentication = create_user_on_data_api(name, user.auth_token)
            model = Station.objects.create_station(name, central, node_authentication)
            if(model):
                return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
            else:
                return HttpResponse("Station already exists.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return HttpResponse("No central informed", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("create_actuator/")
def create_actuator(request):
    user = verify_auth(request)
    if(user):
        name = json.loads(request.body)['name']
        central = get_central(request)
        if(central):
            node_authentication = create_user_on_data_api(name, user.auth_token)
            model = Actuator.objects.create_actuator(name, central, node_authentication)
            if(model):
                return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
            else:
                return HttpResponse("Actuator already exists.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return HttpResponse("No central informed", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("send_data/")
def receive_data(request):
    user = verify_auth(request)
    central = get_central(request)
    node = get_node(request)
    if user and central and node:
        data = json.loads(request.body)
        if 'data' in data.keys():
            send_data(node, data['data'])
            return HttpResponse("beautiful", status=status.HTTP_201_CREATED)

        return HttpResponse("Insuficient information", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)


def verify_auth(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        if 'auth_token' in data.keys():
            user = User.objects.filter(auth_token=data['auth_token'])
            print(user)
            if user:
                return user.first()
        return None
    else:
        return None

def get_central(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        if 'central' in data.keys():
            central = Central.objects.filter(mac_address=data['central'])
            print(central)
            if central:
                return central.first()
        return None
    else:
        return None

def get_node(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        if 'name' in data.keys():
            actuator = Actuator.objects.filter(name=data['name'])
            if actuator:
                return actuator.first()
            else:
                station = Station.objects.filter(name=data['name'])
                if station:
                    return station.first()
        return None
    else:
        return None