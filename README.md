# Sandbox Refresh Scripts

## Before you start

Ensure all the properties in *config.txt* are set correctly.
In the file *emails.txt* put a list of the emails for all users that should be persisted across refreshes.

## Before a refresh

Run the command `python load_users.py`.

This will output data for the emails configured in the above step to *users.json*

## After a refresh

Run the command `python create_users.py`.

This will take the data from the above and use it to recreate all the users.
