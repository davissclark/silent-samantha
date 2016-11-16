from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from flask import request, redirect, session, url_for
from flask.json import jsonify
from ..models import Entry
from . import services
import requests
import simplejson as json


client_id = '86z783qtr0ira7'
client_secret = 'VEhRnB454OexhM4y'
authorization_base_url = 'https://www.linkedin.com/uas/oauth2/authorization'
token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'
scope = ['r_basicprofile rw_nus r_network']
redirect_uri = 'http://silentsamantha.com/callback'



@services.route('/authorize')
def authorize():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = oauth.authorization_url(authorization_base_url)

    session['oauth_state'] = state
    return redirect(authorization_url)


@services.route('/callback', methods=["GET"])
def callback():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
    oauth = linkedin_compliance_fix(oauth)
    token = oauth.fetch_token('https://www.linkedin.com/uas/oauth2/accessToken', client_secret=client_secret, code=request.args.get('code',''))
    session['oauth_token'] = token
    return redirect(url_for('.share', url=session['url']))


@services.route('/share/<url>', methods=["GET"])
def share(url):
    if session['oauth_token'] is not None:
        oauth = OAuth2Session(client_id, token=session['oauth_token'])
        share_entry = Entry.query.filter_by(url=url).first()
        json_content = share_entry.to_json()
        api_url = "https://api.linkedin.com/v1/people/~/shares"
        headers = {"Content-Type":"application/json"}
        r = oauth.post(api_url, data=json_content, headers=headers)
        print(r)
        return redirect(url_for('main.entries'))
    session['url'] = url
    return redirect(url_for('.authorize'))
