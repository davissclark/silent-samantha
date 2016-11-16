from __future__ import unicode_literals

from functools import partial

from flask.ext.dance.consumer import OAuth1ConsumerBlueprint
from flask.globals import LocalProxy, _lookup_app_object

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


__maintainer__ = "Davis Clark <davissclark@gmail.com>"


def make_linkedin_blueprint(api_key, api_secret,
                            redirect_url=None, redirect_to=None,
                            login_url=None, authorized_url=None):
    """
    Make a blueprint for authenticating with Linkedin using OAuth 1.

    Args:
        api_key (str): The API key for your Linkedin application
        api_secret (str): The API secret for your Linkedin application
        redirect_url (str): the URL to redirect to after the authentication
         dance is complete
        redirect_to (str): if "redirect_url" is not defined, the neame of the
         view to redirect to after the authentication dance is complete.
         The actual URL will be determined by :func:'flask.url_for'
        login_url (str, optional): the URL path for the "login" view.
         Defaults to "/linkedin"
        authorized_url (str, optional): the URL path for the "authorized" view.
         Defaults to "/linked/authorized".

    :rtype: :class:'~flask_dance.consumer.OAuth1ConsumerBlueprint'
    :returns: A :ref:'blueprint <flask:blueprints>' to attach to your Flask app.
    """
    linkedin_bp = OAuth1ConsumerBlueprint("linkedin", __name__,
                                          client_key=api_key,
                                          client_secret=api_secret,
                                          base_url="https://api.linkedin.com/v1",
                                          request_token_url='https://api.linkedin.com/uas/oauth/requestToken',
                                          access_token_url='https://api.linkedin.com/uas/oauth/accessToken',
                                          authorization_url='https://www.linkedin.com/uas/oauth/authenticate',
                                          redirect_url=redirect_url,
                                          redirect_to=redirect_to,
                                          login_url=login_url,
                                          authorized_url=authorized_url,
                                          )

    @linkedin_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.linkedin_oauth = linkedin_bp.session

    return linkedin_bp

linkedin = LocalProxy(partial(_lookup_app_object, "linkedin_oauth"))