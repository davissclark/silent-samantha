from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Entry, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/entries/')
def get_entries():
    entries = Entry.query.all()
    return jsonify({ 'entries': [entry.to_json() for entry in entries] })


@api.route('/entries/<int:id>')
def get_entry(id):
    entry = Entry.query.get_or_404(id)
    return jsonify(entry.to_json())


@api.route('/entries/', methods=['POST'])
@permission_required(Permission.PUBLISH)
def new_entry():
    entry = Entry.from_json(request.json)
    entry.author = g.current_user
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_json()), 201, \
        {'Location': url_for('api.get_entry', id=entry.id, _external=True)}


@api.route('/entries/<int:id>', methods=['PUT'])
@permission_required(Permission.PUBLISH)
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    if g.current_user != entry.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    entry.body = request.json.get('body', entry.body)
    db.session.add(entry)
    return jsonify(entry.to_json())