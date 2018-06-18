import json

from toast_web import *


def main():
    users = load_users()
    auth_token = login_and_get_auth_token()
    for email, restaurants in users.items():
        for restaurant_guid, data in restaurants['restaurants'].items():
            restaurant_id = switch_restaurant(restaurant_guid)
            invite_user(auth_token, email, restaurant_id, data['permissions'])


def invite_user(auth_token, email, restaurant_id, permissions):
    data = {'authenticityToken': auth_token, 'restaurantId': restaurant_id, 'invite': 'true'}
    data['user.email'] = email
    data.update(permissions)
    http('/restaurants/users/invite', data)


def load_users():
    file_path = config['users.filepath']
    print "\nLoading user data from %s" % file_path
    with open(file_path, 'r') as users_file:
        return json.load(users_file)

if __name__ == '__main__':
    main()
