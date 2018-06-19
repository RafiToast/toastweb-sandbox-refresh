import urllib
import urllib2
import cookielib
import ssl
from HTMLParser import HTMLParser


def load_config():
    config = {}
    with open("config.txt", 'r') as config_file:
        for line in config_file.readlines():
            if len(line.strip()) > 0 and line[0] != '#':
                split = line.split('=')
                config[split[0].strip()] = split[1].strip()
    return config


config = load_config()

START_AUTH_TOKEN = 'authenticityToken" value="'
END_AUTH_TOKEN = '"'

RESTAURANT_ID_FOOTER_KEY = 'Restaurant Id'
SET_LEAF_ID_FOOTER_KEY = 'Set Leaf Id'

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
    try:
        body = http('/login')
    except:
        raise ValueError('Unable to access login page, check URL in config file is correct')
    return get_text_snip(body, START_AUTH_TOKEN, END_AUTH_TOKEN)


def auth(auth_token):
    data = {'authenticityToken': auth_token, 'password': config['admin.password'], 'email': config['admin.email']}
    body = http('/authenticate', data)
    if body.find('logged-in') == -1:
        raise ValueError('Authentication failed, check admin email and password in config is correct')


def switch_restaurant(guid):
    body = http('/account/switchrestaurant', query_params={'guid': guid})
    return get_restaurant_data_from_footer(body, RESTAURANT_ID_FOOTER_KEY)


def http(url_path, data=None, query_params=None):
    url = config['toastweb.url'] + url_path
    if query_params:
        url = url + '?' + urllib.urlencode(query_params, doseq=True)
    if data:
        response = opener.open(url, urllib.urlencode(data, doseq=True))
    else:
        response = opener.open(url)
    assert response.code == 200
    return response.fp.read()


def get_text_snip(body, start, end):
    start = body.index(start) + len(start)
    end = body.index(end, start)
    return body[start:end]


def get_restaurant_data_from_footer(body, key):
    footer_start = body.index('footer-row')
    row_start = body.index(key, footer_start)
    value_start = body.index('<b>', row_start) + 3
    value_end = body.index('<', value_start)
    return body[value_start:value_end]


class RestaurantGuidExtractor(HTMLParser):

    def __init__(self):
        self.reset()
        self.guids = []

    def handle_starttag(self, startTag, attrs):
        if startTag == 'input':
            attrs_map = dict((x, y) for x, y in attrs)
            if (attrs_map.get('name') == 'rGuids' and attrs_map.get('checked') == 'checked'):
                self.guids.append(attrs_map['value'])


class RestaurantEmployeeUrlExtractor(HTMLParser):

    def __init__(self, email):
        self.reset()
        self.email = email
        self.url = None
        self._last_url = None

    def handle_starttag(self, startTag, attrs):
        if startTag == 'a':
            attrs_map = dict((x, y) for x, y in attrs)
            self._last_url = attrs_map.get('href')

    def handle_data(self, data):
        if data == self.email:
            self.url = self._last_url


class RestaurantUserPermissionsExtractor(HTMLParser):

    def __init__(self):
        self.reset()
        self.permissions = {}

    def handle_starttag(self, startTag, attrs):
        if startTag == 'input':
            attrs_map = dict((x, y) for x, y in attrs)
            name = attrs_map.get('name', '')
            if self.should_include(name) and (
                    attrs_map.get('checked') == 'checked' or attrs_map.get('type') == 'hidden'):
                values = self.permissions.get(name, [])
                values.append(str(attrs_map['value']))
                self.permissions[name] = sorted(values)

    def should_include(self, name):
        return len(filter(lambda x: name.lower().find(x) > -1, ['permissions', 'job', 'state'])) > 0
