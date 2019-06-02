import json
import requests

def create_user_on_data_api(user, username, password):
    data = {
        'username':username,
        'password':password
    }
    
    result = request_data_api('signup/', data)
    result = json.loads(result)
    user.data_token = result['authentication_token']
    user.save()

    return result

def request_data_api(end_point, data={}):
    post_url = "http://localhost:8080/" + end_point

    headers = {"content-type": "application/json"}
    data = json.dumps(data)

    print(data)

    r = requests.post(post_url, data=data, headers=headers)

    return r.text