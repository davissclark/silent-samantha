from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views
from ..models import Tag, gravatar

@admin.app_context_processor
def inject_topics():
    topics = Tag.query.order_by(Tag.name.desc()).all()
    return dict(topics=topics)


@admin.app_context_processor
def inject_gravatar():
    grav = gravatar()
    return dict(grav=grav)