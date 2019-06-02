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


def verify_password(user=None, provided_password=None):
    """Verify a stored password against one provided by user"""
    if user is None or provided_password is None:
        return False

    salt = user.hash[:64]
    stored_password = user.hash[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def create_user_on_data_api(user, username, password):
    data = {
        'username':username,
        'password':password
    }
    
    result = request_data_api('signup/', data)
    result = json.loads(result)

    user.data_token = result['authentication_token']
    user.save()


def request_data_api(end_point, data={}):
    post_url = "http://localhost:8080/" + end_point

    headers = {"content-type": "application/json"}
    data = json.dumps(data)

    print(data)

    r = requests.post(post_url, data=data, headers=headers)

    return r.text