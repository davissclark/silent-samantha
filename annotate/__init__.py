from flask import Blueprint, Response

annotate = Blueprint('annotate', __name__)

from . import views
