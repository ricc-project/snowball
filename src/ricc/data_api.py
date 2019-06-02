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
    
def request_data_api(end_point, data={}):
    post_url = "http://localhost:8080/" + end_point

    headers = {"content-type": "application/json"}
    data = json.dumps(data)

    print(data)

    r = requests.post(post_url, data=data, headers=headers)

    return r.text