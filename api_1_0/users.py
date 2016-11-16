from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Entry


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/entries/')
def get_user_entries(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.entries.order_by(Entry.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_ENTRIES_PER_PAGE'],
        error_out=False)
    entries = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_entries', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_entries', page=page+1, _external=True)
    return jsonify({
        'entries': [entry.to_json() for entry in entries],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_entries.order_by(Entry.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_ENTRIES_PER_PAGE'],
        error_out=False)
    entries = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_entries', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_entries', page=page+1, _external=True)
    return jsonify({
        'entries': [entry.to_json() for entry in entries],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })