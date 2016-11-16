from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
from ..models import Tag, gravatar


@auth.app_context_processor
def inject_topics():
    topics = Tag.query.order_by(Tag.name.desc()).all()
    return dict(topics=topics)


@auth.app_context_processor
def inject_gravatar():
    grav = gravatar()
    return dict(grav=grav)