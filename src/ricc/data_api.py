import json
import requests

def create_user_on_data_api(username, password):
    data = {
        'username':username,
        'password':password
    }
    result = request_data_api('signup/', data)
    result = json.loads(result)

    return result['authentication_token']


def send_data(node, node_data):
    data = {
        "auth_token": node.data_token,
        "data": node_data
    }
    result = request_data_api('send-data/', data)

    print(result)


def request_data_api(end_point, data={}):
    post_url = "http://10.0.0.145/" + end_point

    headers = {"content-type": "application/json"}
    data = json.dumps(data)

    print(data)

    r = requests.post(post_url, data=data, headers=headers)

    return r.text

