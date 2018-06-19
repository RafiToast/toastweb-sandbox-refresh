import json

from toast_web import *

SUCCESS_TEXT = 'Invitation was sent successfully'


def main():
    users = load_users()
    auth_token = login_and_get_auth_token()
    for email, restaurants in users.items():
        print 'Creating user %s' % email
        for restaurant_guid, data in restaurants['restaurants'].items():
            print '\tSwitching to restaurant %s' % restaurant_guid
            restaurant_id = switch_restaurant(restaurant_guid)
            invite_user(auth_token, email, restaurant_id, data['permissions'])


def invite_user(auth_token, email, restaurant_id, permissions):
    data = {'authenticityToken': auth_token, 'restaurantId': restaurant_id, 'invite': 'true'}
    data['user.email'] = email
    data.update(permissions)
    response = http('/restaurants/users/invite', data)
    if response.find(SUCCESS_TEXT) > -1:
        print '\t\t %s' % SUCCESS_TEXT
    else:
        print '\t\t Problem inviting user, check logs'


def load_users():
    file_path = config['users.filepath']
    print "Loading user data from %s\n" % file_path
    with open(file_path, 'r') as users_file:
        return json.load(users_file, encoding='utf-8')


if __name__ == '__main__':
    main()
