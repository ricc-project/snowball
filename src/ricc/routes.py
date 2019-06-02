import hashlib, binascii, requests, json
from rest_framework import status
from boogie.router import Router
from django.db import models
from django.http import HttpResponse
from .models import User
from .manager import verify_password
from .data_api import create_user_on_data_api


urlpatterns = Router()

@urlpatterns.route("signup/")
def signup(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(request.method == "POST"):
        if request.POST.keys() >= {"username", "password"}:
            username = request.POST['username']
            password = request.POST['password']
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



@urlpatterns.route("create_station/")
def create_station(request):
    pass
    # user = create_user_on_data_api(user, username, password)
            

