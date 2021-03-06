from toast_web import *
import json


processed_sets = []


def main():
    users = {}
    auth_token = login_and_get_auth_token()
    for email in load_emails():
        print 'Loading data for %s' % email
        restaurants = get_restaurants(auth_token, email)
        if len(restaurants) > 0:
            users[email] = {'restaurants': restaurants}
        else:
            print '\tNo restaurants found for that email address'
    output_users(users)


def get_restaurants(auth_token, email):
    restaurants = {}
    restaurant_guids = get_restaurant_guids(auth_token, email)
    if len(restaurant_guids) > 0:
        edit_url = get_edit_url(restaurant_guids[0], email)
        for restaurant_guid in restaurant_guids:
            print '\tLoading permissions for restaurant %s' % restaurant_guid
            switch_restaurant(restaurant_guid)
            permissions = load_permissions(auth_token, edit_url)
            restaurants[restaurant_guid] = {'permissions': permissions}
    return restaurants


def get_restaurant_guids(auth_token, email):
    data = {'authenticityToken': auth_token, 'email': email}
    response = http('/toast/users/lookupuser', data=data)
    parser = RestaurantGuidExtractor()
    parser.feed(response)
    return parser.guids


def get_edit_url(restaurant_guid, email):
    switch_restaurant(restaurant_guid)
    employees = http('/restaurants/users')
    url_extractor = RestaurantEmployeeUrlExtractor(email)
    url_extractor.feed(employees)
    url = url_extractor.url.replace('show', 'edit')
    if debug_mode:  print '\tUsing edit url %s' % (url)
    return url


def load_permissions(auth_token, edit_url):
    response = http(edit_url)
    set_leaf = get_restaurant_data_from_footer(response, SET_LEAF_ID_FOOTER_KEY)
    parser = RestaurantUserPermissionsExtractor()
    parser.feed(response)
    permissions = parser.permissions
    permissioned_group = [set_leaf] + parser.permission_sub_groups

    if len(parser.permission_sub_groups) > 0:
        sub_permissions = load_sub_permissions(auth_token, permissioned_group, parser)
        permissions.update(sub_permissions)
    permissions['permissionedGroup'] = dedupe(permissioned_group)

    return permissions


def load_sub_permissions(auth_token, permissioned_group, parser):
    sub_permissions = {}
    data = {'authenticityToken': auth_token, 'permissionedGroup': permissioned_group}
    data.update(parser.permissions)
    for set_id in parser.permission_sub_groups:
        if set_id not in processed_sets:
            data = {'authenticityToken': auth_token, 'permissionedGroup':permissioned_group}
            data.update(parser.permissions)
            response = http('/restaurants/users/showPermission',data,{'guid':parser.user_guid, 'set_id':set_id})
            sub_parser = RestaurantUserPermissionsExtractor()
            sub_parser.feed(response)
            sub_permissions.update(sub_parser.permissions)
            processed_sets.append(set_id)
    return sub_permissions


def load_emails():
    emails = []
    file_path = config['emails.filepath']
    try:
        print 'Loading users from %s\n' % file_path
        with open(file_path, 'r') as emails_file:
            for line in emails_file.readlines():
                if len(line.strip()) > 0 and line[0] != '#':
                    emails.append(line.strip().lower())
    except IOError as e:
        raise ValueError('Unable to access emails file at %s' % file_path)
    return emails


def output_users(users):
    file_path = config['users.filepath']
    print "\nSaving user data to %s" % file_path
    with open(file_path, 'w') as users_file:
        json.dump(users, users_file, sort_keys=True, indent=2)


if __name__ == '__main__':
    main()
