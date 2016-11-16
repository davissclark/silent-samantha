from flask.ext.dance.contrib.linkedin import make_linkedin_blueprint


linkedin_blueprint = make_linkedin_blueprint(
    client_id="75lkk6j4fyox43",
    client_secret="nrYmLETLi80XAw2Q",
    scope="r_basicprofile",
    redirect_to="main.share_entry",
 )