import hashlib, binascii, requests, json, functools
from rest_framework import status
from boogie.router import Router
from django.db import models
from django.http import HttpResponse
from .models import User, Station, Central, Actuator
from .manager import verify_password
from .data_api import create_user_on_data_api


urlpatterns = Router()

@urlpatterns.route("signup/")
def signup(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(request.method == "POST"):
        data = json.loads(request.body)
        if data.keys() >= {"username", "password"}:
            username = data['username']
            password = data['password']
            # try:
            user = User.objects.create_user(username, password)
            response = {"authentication_token": user.auth_token}
            rstatus = status.HTTP_201_CREATED
            # except:
                # response = {"Unavailable username": "username already taken"}
        else:
            response = {
                "Not enough credencials": "You need to send password and username."}
    else:
        response = {"Wrong method.": "Can't signup with GET method."}

    return HttpResponse(str(response), status=rstatus)


@urlpatterns.route("login/")
def login(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(verify_sent_credentials(request)):
        username = request.POST['username']
        password = request.POST['password']
        user = None
        try:
            user = User.objects.get(username=username)
        except:
            response = response = {"Incorrect Credentials": "Invalid login information."}

        if(verify_password(user, password)):
            response = {"authentication_token": user.auth_token}
            rstatus = status.HTTP_202_ACCEPTED
        else:
            response = {"Incorrect Credentials": "Invalid login information."}
    else:
        response = {
            "Not enough information sent to do this.":
            "No username or Password, maybe not a POST method."}

    return HttpResponse(str(response), status=rstatus)


def verify_sent_credentials(request):
    if(request.method == "POST"):
        if request.POST.keys() >= {"username", "password"}:
            return True
    return False


@urlpatterns.route("create_central/")
def create_central(request):
    user = verify_auth(request)
    if(user):
        mac_address = json.loads(request.body)['mac_address']
        Central.objects.create_central(user, mac_address)
        return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("create_station/")
def create_station(request):
    user = verify_auth(request)
    if(user):
        name = json.loads(request.body)['name']
        central = get_central(request)
        if(central):
            node_authentication = create_user_on_data_api(name, user.auth_token)
            Station.objects.create_station(name, central, node_authentication)
            return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
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
            Actuator.objects.create_actuator(name, central, node_authentication)
            return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
        else:
            return HttpResponse("No central informed", status=status.HTTP_401_UNAUTHORIZED)
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