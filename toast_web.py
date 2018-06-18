import urllib
import urllib2
import cookielib
import ssl
from HTMLParser import HTMLParser


def load_config():
    config = {}
    with open("config.txt", 'r') as config_file:
        for line in config_file.readlines():
            if len(line.strip())>0 and line[0] != '#':
                split = line.split('=')
                config[split[0].strip()] = split[1].strip()
    return config


config=load_config()


START_AUTH_TOKEN = 'authenticityToken" value="'
END_AUTH_TOKEN = '"'

START_RESTAURANT_ID = 'Restaurant Id: <span class="auto-select"><b>'
END_RESTAURANT_ID = '<'

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

cookieJar = cookielib.CookieJar()

handlers = [urllib2.HTTPSHandler(context=context), urllib2.HTTPCookieProcessor(cookieJar)]
opener = urllib2.build_opener(*handlers)




def login_and_get_auth_token():
    auth_token = login_page()
    auth(auth_token)
    return auth_token


def login_page():
    body = http('login')
    return get_text_snip(body, START_AUTH_TOKEN, END_AUTH_TOKEN)


def auth(auth_token):
    data = {'authenticityToken': auth_token, 'password': config['admin.password'], 'email': config['admin.email']}
    body = http('authenticate', data)
    body.index('logged-in')


def switch_restaurant(guid):
    body = http('account/switchrestaurant', query_params={'guid': guid})
    return get_text_snip(body, START_RESTAURANT_ID, END_RESTAURANT_ID)


def http(url_path, data=None, query_params=None):
    url = config['toastweb.url'] + url_path
    if query_params:
        url = url + '?' + urllib.urlencode(query_params)
    if data:
        response = opener.open(url, urllib.urlencode(data))
    else:
        response = opener.open(url)
    assert response.code == 200
    return response.fp.read()


def get_text_snip(body, start, end):
    start = body.index(start) + len(start)
    end = body.index(end, start)
    return body[start:end]


class RestaurantGuidExtractor(HTMLParser):

    def __init__(self):
        self.reset()
        self.guids = []

    def handle_starttag(self, startTag, attrs):
        if startTag == 'input':
            attrs_map = dict((x, y) for x, y in attrs)
            if (attrs_map.get('name') == 'rGuids' and attrs_map.get('checked') == 'checked'):
                self.guids.append(attrs_map['value'])
