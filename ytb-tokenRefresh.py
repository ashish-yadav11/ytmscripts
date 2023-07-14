#!/usr/bin/python

import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

oauthfile = "/home/ashish/.config/youtube-oauth.json"
credsfile = "/home/ashish/.config/youtube-creds.json"

SCOPE = ["https://www.googleapis.com/auth/youtube"]


token = None
if os.path.exists(oauthfile):
    token = Credentials.from_authorized_user_file(oauthfile, SCOPE)
flag = token and token.refresh_token
if flag:
    try:
        token.refresh(Request())
    except RefreshError:
        flag = False
if not flag:
    stdout_fileno = sys.stdout.fileno()
    stderr_fileno = sys.stderr.fileno()
    orig_stdout_fileno = os.dup(stdout_fileno)
    os.dup2(stderr_fileno, stdout_fileno)

    flow = InstalledAppFlow.from_client_secrets_file(credsfile, SCOPE)
    token = flow.run_local_server(port=0)

    os.dup2(orig_stdout_fileno, stdout_fileno)
with open(oauthfile, 'w') as file:
    file.write(token.to_json())
