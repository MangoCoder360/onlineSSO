import os
import pathlib
import re

import requests
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask(__name__)
app.secret_key = "4N1rqh4Y^w@SOuKDQ&Jlh^EA!4TnmgDhbbN4fRvA"

USE_PROD_DOMAIN = True

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "107748350992-6cidfs1km016ts31sop66u76dc78nlfr.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "env/client_secret.json")

if USE_PROD_DOMAIN:
    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="https://onlinesso.reuben.zip/googlecallback"
    )
else:
        flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://localhost:8000/googlecallback"
    )

@app.route("/googlecallback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/googleoauth")
def login():
    authorization_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return redirect(authorization_url)

@app.route("/")
def protected_area():
    if "email" in session:
        return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a><br><br>{session['email']}"
    else:
        return redirect("/googleoauth")


if __name__ == "__main__":
  app.run(port=8000,host="0.0.0.0")