import json

from toast_web import *

SUCCESS_TEXT = 'Invitation was sent successfully'
ALREADY_EXISTS = 'address already exists'


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
    try:
        response = http('/restaurants/users/invite', data, {'restaurantId':restaurant_id})
        if response.find(SUCCESS_TEXT) > -1:
            print '\t\t %s' % SUCCESS_TEXT
        elif response.find(ALREADY_EXISTS) > -1:
            print '\t\t A user with that email already exists'
        else:
            print '\t\t Problem inviting user, check server logs'
    except Exception as e:
        print 'Failed to invite user: %s' % (e)


def load_users():
    file_path = config['users.filepath']
    print "Loading user data from %s\n" % file_path
    with open(file_path, 'r') as users_file:
        return json.load(users_file, encoding='utf-8')


if __name__ == '__main__':
    main()
