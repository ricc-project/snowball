import json
import requests

def create_user_on_data_api(username, password):
    data = {
        'username':username,
        'password':password
    }
    result = request_data_api('signup/', data)
    result = json.loads(result)
    print(result)
    try:
        return result['authentication_token']
    except:
        return None

def send_data(node, node_data, timestamp):
    data = {
        "auth_token": node.data_token,
        "data": node_data,
        "timestamp": timestamp
    }
    result = request_data_api('send-data/', data)

    print(result)


def get_data(node):
    data = {
        "auth_token": node.data_token,
        "central": node.central.mac_address,
        "name": node.name
    }
    result = request_data_api('get_last/', data)
    result = json.loads(result)
    
    return result

def get_period_data(nodes, filters):
    results = []

    print("FILTERS", filters)

    for node in nodes:
        args = {
            "auth_token": node.data_token,
            "central": node.central.mac_address,
            "filters" : filters
        }
         
        data = request_data_api('get_period_data/', args)
        
        result = {
            "station" : node.name,
            "data" : json.loads(data)
        }

        results.append(result)

    return results


def get_last_activated_switch(node):
    data = {
        "auth_token": node.data_token,
        "central": node.central.mac_address,
        "name": node.name
    }
    result = request_data_api('get_last_switch_activated/', data)
    result = json.loads(result)
    
    return result

def request_data_api(end_point, data={}):
    post_url = "http://10.0.0.145/" + end_point

    headers = {"content-type": "application/json"}
    data = json.dumps(data)

    print("DATA", data)

    r = requests.post(post_url, data=data, headers=headers)

    return r.text

