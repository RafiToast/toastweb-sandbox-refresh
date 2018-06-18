import uuid

from toast_web import *

BLACK_SHEEP = '000001ce-21a7-1825-0000-012d75ebda80'
ROBOELECTRIC_NIGHTCLUB = '8133cc6f-fea1-4e52-992a-2b25d0bf4931'


def main():
    auth_token = login_and_get_auth_token()
    restaurant_id = switch_restaurant(ROBOELECTRIC_NIGHTCLUB)
    invite_user(auth_token, restaurant_id)


def invite_user(auth_token, restaurant_id):
    data = {'authenticityToken': auth_token, 'restaurantId': restaurant_id, 'invite': 'true'}
    data['user.email'] = 'adambarnes5000+%s@gmail.com' % str(uuid.uuid4()).split('-')[0]
    http('restaurants/users/invite', data)


if __name__ == '__main__':
    main()
