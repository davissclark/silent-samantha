try:
    import httplib  # Python 2
except ImportError:
    import http.client as httplib  # Python 3
try:
    from urllib import urlencode  # Python 2
except ImportError:
    from urllib.parse import urlencode  # Python 3
import json
from flask.ext.babel import gettext
from config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET

def linkedin(text, sourceLang, destLang):
    if MS_TRANSLATOR_CLIENT_ID == "" or MS_TRANSLATOR_CLIENT_SECRET == "":
        return gettext('Error: translation service not configured.')
    try:
        # get access token
        params = urlencode({
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET,
            'scope': 'http://api.linkedin.com',
            'grant_type': 'client_credentials'})
        conn = httplib.HTTPSConnection("datamarket.accesscontrol.windows.net")
        conn.request("POST", "/v1/OAuth2-13", params)
        response = json.loads (conn.getresponse().read())
        token = response[u'access_token']

        # translate
        conn = httplib.HTTPConnection('api.microsofttranslator.com')
        params = {'appId': 'Bearer ' + token,
                  'from': sourceLang,
                  'to': destLang,
                  'text': text.encode("utf-8")}
        conn.request("GET", '/V2/Ajax.svc/Translate?' + urlencode(params))
        response = json.loads("{\"response\":" + conn.getresponse().read().decode('utf-8') + "}")
        return response["response"]
    except:
        return gettext('Error: Unexpected error.')