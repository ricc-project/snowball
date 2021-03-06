import hashlib, binascii, requests, json, functools
from rest_framework import status
from boogie.router import Router
from django.db import models
from django.http import HttpResponse
from web_socket.actuator import switch
from django.shortcuts import get_object_or_404
from .models import User, Station, Central, Actuator, UnlockedCentral, UserCard
from .manager import verify_password
from .data_api import *
import json

urlpatterns = Router()

@urlpatterns.route("signup/")
def signup(request):
    rstatus = status.HTTP_403_FORBIDDEN
    if(request.method == "POST"):
        data = json.loads(request.body)
        if data.keys() >= {"username", "password", "mac_address"}:
            username = data['username']
            password = data['password']
            mac_address = json.loads(request.body)['mac_address']
            unlockedCentrals = UnlockedCentral.objects.filter(mac_address=mac_address)
            if(unlockedCentrals):
                user = User.objects.create_user(username, password)
                if(user):
                    model = Central.objects.create_central(user, mac_address)
                    print("MEU PIRU")
                    response = {"authentication_token": user.auth_token}
                    response = json.dumps(response)
                    response = json.loads(response)

                    rstatus = status.HTTP_201_CREATED
                else:
                    response = {"message": "username already taken"}
        else:
            response = {
                "message": "You need to send password and username and a mac_address."}
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
                response = {"message": "Invalid login information."}

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
                return HttpResponse(format_for_hugo("Beautiful"), status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(format_for_hugo("Mac already used."), status=status.HTTP_401_UNAUTHORIZED)
        else:
            return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

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
    print("request_data: "+str(json.loads(request.body))+"\n")
    model = UnlockedCentral.objects.create_central(mac_address)
    if(model):
        return HttpResponse("beautiful", status=status.HTTP_201_CREATED)
    else:
        return HttpResponse("Mac in use.", status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("create_station/")
def create_station(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
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
    print("request_data: "+str(json.loads(request.body))+"\n")
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
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    node = get_node(request)
    if user and central and node:
        data = json.loads(request.body)
        print(data)
        if 'data' in data.keys():
            send_data(node, data['data'], data['timestamp'])
            return HttpResponse("beautiful", status=status.HTTP_201_CREATED)

        return HttpResponse("Insuficient information", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized.", status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("central/last_datas/")
def last_data(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        all_data = []
        for station in Station.objects.filter(central=central):
            s_data = get_data(station)

            data = {
                "station" : {
                    "name" : station.name,
                },
                "data" : s_data
            }

            all_data.append(data)
            # print("all", all_data)

        return HttpResponse(json.dumps(all_data), status=status.HTTP_201_CREATED)
    else:
        return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("actuator/last_datas/")
def actuator_last_data(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        all_data = []
        for actuator in Actuator.objects.filter(central=central):
            print(actuator)
            a_data = get_last_activated_switch(actuator)

            data = {
                "actuator" : {
                    "name" : actuator.name,
                },
                "data" : a_data
            }

            all_data.append(data)
            # print("all", all_data)

        return HttpResponse(json.dumps(all_data), status=status.HTTP_201_CREATED)
    else:
        return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("irrigation/")
def get_irrigation(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        return HttpResponse('{"auto_irrigation":"'+str(central.automatic_irrigation)+'"}', status=status.HTTP_201_CREATED)
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("central/stations_count/")
def stations_count(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        return HttpResponse(format_for_hugo(central.station_count()), status=status.HTTP_201_CREATED)
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("central/actuators_count/")
def actuators_count(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        return HttpResponse(format_for_hugo(central.actuator_count()), status=status.HTTP_201_CREATED)
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("node_status/on/")
def turnon_node(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    node = get_node(request)
    if user and central and node:
        node.status = True
        node.save()
        return HttpResponse('{"status":"'+str(node.status)+'"}', status=status.HTTP_200_OK)
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)
        
@urlpatterns.route("node_status/off/")
def turnoff_node(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    node = get_node(request)
    if user and central and node:
        node.status = False
        node.save()
        return HttpResponse('{"status":"'+str(node.status)+'"}', status=status.HTTP_200_OK)
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)


@urlpatterns.route("node/status/")
def status_node(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    node = get_node(request)
    if user and central and node:
        return HttpResponse('{"status":"'+str(node.status)+'"}', status=status.HTTP_200_OK)

    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("actuator/switch/")
def switch_actuator(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        switch(central.mac_address)
        return HttpResponse(format_for_hugo("Beautiful"), status=status.HTTP_200_OK)

    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("central/switch/")
def switch_central(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    user = verify_auth(request)
    central = get_central(request)
    if user and central:
        central.automatic_irrigation = not central.automatic_irrigation
        central.save()
        return HttpResponse(format_for_hugo("Beautiful"), status=status.HTTP_200_OK)

    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

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
            print(actuator)
            if actuator:
                return actuator.first()
            else:
                station = Station.objects.filter(name=data['name'])
                print(station)
                if station:
                    return station.first()
        return None
    else:
        return None


def format_for_hugo(str):
    response = {"message": str}
    response = json.dumps(response)
    return response



# New URLS

@urlpatterns.route("centrals/")
def centrals_by_owner(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            user = verify_auth(request)
            user_centrals = Central.objects.filter(owner=user)
            response_centrals = []

            for central in user_centrals:
                response_centrals.append(
                    {
                        "mac_address": central.mac_address,
                        "automatic_irrigation": central.automatic_irrigation,
                        "amount_stations": central.station_count(),
                        "amount_actuators": central.actuator_count()
                    }
                )
            rstatus = status.HTTP_200_OK            
            response = {"centrals": response_centrals}
        except:
            response = {"centrals": []}
    else:
        response = {"centrals": "No GET function around here"}

    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("stations/")
def stations_by_owner(request):
    print("request_data: "+str(json.loads(request.body))+"\n")

    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            user = verify_auth(request)
            user_centrals = Central.objects.filter(owner=user)
            response_stations = []

            for central in user_centrals:
                user_stations = Station.objects.filter(central=central)  
                for station in user_stations:
                    response_stations.append(
                        {
                            "related_central": station.central.mac_address,
                            "name": station.name,
                            "status": station.status,
                        }
                    )
            rstatus = status.HTTP_200_OK            
            response = {"stations": response_stations}

        except:
            response = {"stations": []}
    else:
        response = {"stations": "No GET function around here"}
    
    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("actuators/")
def actuators_by_owner(request):
    print("request_data: "+str(json.loads(request.body))+"\n")

    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            user = verify_auth(request)
            user_centrals = Central.objects.filter(owner=user)
            response_actuators = []

            for central in user_centrals:
                user_actuators = Actuator.objects.filter(central=central)  
                for actuator in user_actuators:
                    response_actuators.append(
                        {
                            "related_central": actuator.central.mac_address,
                            "name": actuator.name,
                            "status": actuator.status,
                        }
                    )
            rstatus = status.HTTP_200_OK            
            response = {"actuators": response_actuators}

        except:
            response = {"actuators": []}
    else:
        response = {"actuators": "No GET function around here"}
    
    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("user/")
def get_user(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            user = verify_auth(request)
            user_centrals = Central.objects.filter(owner=user)
            user_centrals = user_centrals.first()

            data = {
                "username" : user.username,
                "name" : user.name,
                "ricc_code" : user_centrals.mac_address
            }

            rstatus = status.HTTP_200_OK            
            response = {"user": data}

        except:
            response = {"user": []}
    else:
        response = {"user": "No GET function around here"}

    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("edit_user/")
def edit_user(request):
    print("request_data: "+str(json.loads(request.body))+"\n")
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            user = verify_auth(request)
            data = json.loads(request.body)

            user.name = data['name']
            user.username = data['username']
            user.save()

            rstatus = status.HTTP_200_OK
            response = {"user": "Updated"}

        except:
            response = {"user": ""}
    else:
        response = {"user": "No GET function around here"}

    response = json.dumps(response)
    return HttpResponse(response, status=rstatus)


@urlpatterns.route("measure/last/")
def last_data(request):
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            data = json.loads(request.body)

            user = verify_auth(request)
            central = get_central(request)
            r_station = data['station']
            filters = data['filters']

            if user and central and r_station and filters:
                station = Station.objects.filter(central=central, name=r_station)
                result_data = get_data(station[0])

                category = filters['category']
                measure = filters['measure']

                response = {"value": result_data[category][0][measure]}

                if measure == 'speed':
                    response = {"value": {
                                        "speed" : result_data[category][0]['speed'],
                                        "direction" : result_data[category][0]['direction']
                                        }
                    }

                elif measure == 'moisture1':
                    response = {"value": {
                                        "moisture1" : result_data[category][0]['moisture1'],
                                        "moisture2" : result_data[category][0]['moisture2'],
                                        "moisture3" : result_data[category][0]['moisture3']
                                        }
                    }                    

                return HttpResponse(json.dumps(response), status=status.HTTP_201_CREATED)

        except:
            response = {"value": None}
    else:
        response = {"value": "No GET function around here"}
    
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("measure/period/")
def period_data(request):
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            data = json.loads(request.body)

            user = verify_auth(request)
            central = get_central(request)
            
            filters = data['filters']

            if user and central and filters:
                stations = Station.objects.filter(central=central)
                response = get_period_data(stations, filters)
                
                return HttpResponse(json.dumps(response), status=status.HTTP_201_CREATED)

        except:
            response = {"value": None}
    else:
        response = {"value": "No GET function around here"}
    
    return HttpResponse(format_for_hugo("Unauthorized."), status=status.HTTP_401_UNAUTHORIZED)

@urlpatterns.route("card/save/")
def save_card(request):
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            data = json.loads(request.body)

            user = verify_auth(request)
            central = get_central(request)
            r_station = data['station']
            card_type = data['card_type']

            user_cards_amount_p = UserCard.objects.count()

            user_card = UserCard(owner=user, central=central.mac_address, station=r_station, card_type=card_type)
            user_card.save()

            user_cards_amount_a = UserCard.objects.count()

            if(user_cards_amount_a > user_cards_amount_p):
                return HttpResponse(json.dumps({"status": "beautiful"}), status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(json.dumps({"status": "Got trouble"}), status=status.HTTP_401_UNAUTHORIZED)
        except:
            response = {"value": None}
    else:
        response = {"value": "No GET function around here"}

@urlpatterns.route("card2/save/")
def save_card_t(request):
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            data = json.loads(request.body)

            user = verify_auth(request)
            central = get_central(request)
            card_type = data['card_type']

            user_cards_amount_p = UserCard.objects.count()

            user_card = UserCard(owner=user, central=central.mac_address, card_type=card_type)
            user_card.save()

            user_cards_amount_a = UserCard.objects.count()

            if(user_cards_amount_a > user_cards_amount_p):
                return HttpResponse(json.dumps({"status": "beautiful"}), status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(json.dumps({"status": "Got trouble"}), status=status.HTTP_401_UNAUTHORIZED)
        except:
            response = {"value": None}
    else:
        response = {"value": "No GET function around here"}

@urlpatterns.route("card/get/")
def get_card(request):
    rstatus = status.HTTP_403_FORBIDDEN

    if(request.method == "POST"):
        try:
            response = []

            user = verify_auth(request)

            print("here", user)
            cards = UserCard.objects.filter(owner=user)
            print("cards", cards)
            
            for card in cards:
                response.append({
                    "central" : card.central,
                    "station" : card.station,
                    "card_type" : card.card_type
                })

            return HttpResponse(json.dumps({"cards": response}), status=status.HTTP_201_CREATED)
        except:
            response = {"value": None}
    else:
        return HttpResponse("Got trouble.", status=status.HTTP_401_UNAUTHORIZED)