from flask import redirect, url_for, session, request, jsonify, g
from .. import oauth
from . import api
from ..models import Entry
from werkzeug import security



linkedin = oauth.remote_app(
        'linkedin',
        consumer_key='75lkk6j4fyox43',
        consumer_secret='nrYmLETLi80XAw2Q',
        request_token_params={
            'scope': 'r_fullprofile',
            'state': lambda: security.gen_salt(10)
        },
        base_url='https://api.linkedin.com/v1/',
        authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    )


@api.route('/share/<url>')
def share(url):
    entry = Entry.query.filter_by(url=url).first()
    if 'linkedin_oauth' in session:
        api_url = linkedin.post('people/~/shares')
        json_entry = entry.to_json()
        return jsonify(api_url.json_entry)
    g.entry = entry
    return linkedin.authorize(
        callback=url_for('.authorized', _external=True)
    )


@api.route('/authorized')
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print(resp)
    session['linkedin_oauth'] = (resp['access_token'], '')
    api_url = linkedin.post('people/~/shares')
    json_entry = g.entry.to_json
    return jsonify(api_url.json_entry)



@linkedin.tokengetter
def get_oauth_token():
    return session.get('linkedin_oauth')


@api.route('/logout')
def logout():
    session.pop('linkedin_token', None)
    return redirect(url_for('main.entries'))