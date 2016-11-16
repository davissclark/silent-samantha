from flask import Blueprint

main = Blueprint('main', __name__)

from datetime import date
from . import views, errors
from .forms import SubscribeForm
from ..models import Permission, Entry, Tag, gravatar


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_context_processor
def inject_topics():
    topics = Tag.query.order_by(Tag.name.desc()).all()
    return dict(topics=topics)


@main.app_context_processor
def inject_gravatar():
    grav = gravatar()
    return dict(grav=grav)

@main.app_context_processor
def inject_subscribe():
    subform = SubscribeForm()
    return dict(subform=subform)