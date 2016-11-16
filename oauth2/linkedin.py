from datetime import datetime
from flask import request, redirect, session, url_for, current_app, flash
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from . import oauth2
from ..models import Entry
import keen


client_id = '75lkk6j4fyox43'
client_secret = 'nrYmLETLi80XAw2Q'
authorization_base_url = 'https://www.linkedin.com/uas/oauth2/authorization'
token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'
scope = ['r_basicprofile w_share']


@oauth2.route('/callback', methods=["GET"])
def callback():
    redirect_uri = current_app.config['REDIRECT_URI_BASE'] + 'oauth2/callback'
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
    oauth = linkedin_compliance_fix(oauth)
    token = oauth.fetch_token('https://www.linkedin.com/uas/oauth2/accessToken', client_secret=client_secret, code=request.args.get('code',''))
    session['oauth_token'] = token
    return redirect(url_for('.share_entry', url=session['url']))


@oauth2.route('/oauth2/share/<url>', methods=["GET"])
def share_entry(url):
    if 'oauth_token' in session:
        oauth = OAuth2Session(client_id, token=session['oauth_token'])
        entry = Entry.query.filter_by(url=url).first()
        json_entry = entry.to_json()
        api_url = "https://api.linkedin.com/v1/people/~/shares"
        headers = {"Content-Type":"application/json",
                   "x-li-format":"json"}
        r = oauth.post(api_url, data=json_entry, headers=headers)
        keen.add_event("share_requests", {
                "entry": entry.url,
                "medium": "linkedin"
                })
        if r.status_code == 201:
            keen.add_event("linkedin_shares", {
                "entry": entry.url,
                "status": 201
                })
            session.pop('oauth_token',None)
            session.pop('oauth_state', None)
            flash('You successfully shared this entry with your peers -- thanks a lot!')
            return redirect(url_for('main.entry', eyear=entry.published.year, emonth=entry.published.month, url=url))
        elif r.status_code == 400:
            keen.add_event("linkedin_shares", {
                "entry": entry.url,
                "status": 400
                })
            flash('A failure of code for which Davis is to blame.')
        elif r.status_code == 401:
            keen.add_event("linkedin_shares", {
                "entry": entry.url,
                "status": 401
                })
            flash('Authentication is invalid.')
        session.pop('oauth_token',None)
        session.pop('oauth_state', None)
        return redirect(url_for('main.entries'))
    else:
        redirect_uri = current_app.config['REDIRECT_URI_BASE'] + 'oauth2/callback'
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        authorization_url, state = oauth.authorization_url(authorization_base_url)
        session['oauth_state'] = state
        session['url'] = url
        return redirect(authorization_url)
