from toast_web import *


def main():
    auth_token = login_and_get_auth_token()
    for email in load_emails():
        get_user_data(auth_token, email)


def get_user_data(auth_token, email):
    restaurant_guids = get_restaurant_guids(auth_token, email)
    for restaurant_guid in restaurant_guids:
        print restaurant_guid

def get_restaurant_guids(auth_token, email):
    data = {'authenticityToken': auth_token, 'email': email}
    response = http('toast/users/lookupuser', data=data)
    parser = RestaurantGuidExtractor()
    parser.feed(response)
    return parser.guids

def load_emails():
    return ['adambarnes5000@gmail.com']


if __name__ == '__main__':
    main()
