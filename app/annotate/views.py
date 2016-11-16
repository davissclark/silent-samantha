"""
This module implements a Flask-based JSON API to talk with the annotation store via the
Annotation model.
It defines these routes:
  * Root
  * Index
  * Create
  * Read
  * Update
  * Delete
See their descriptions in `root`'s definition for more detail.
"""
from __future__ import absolute_import
import json
from flask import Response, current_app, g, request, url_for
from flask_login import login_required, current_user
from .. import db
from . import annotate
from ..decorators import admin_required
from ..models import Annotation, Entry, User


# We define our own jsonify rather than using flask.jsonify because we wish
# to jsonify arbitrary objects (e.g. index returns a list) rather than kwargs.
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)


@annotate.before_request
def before_request():
    if not hasattr(g, 'annotation_class'):
        g.annotation_class = Annotation
    if current_user.is_authenticated():
        if current_user is not None:
            g.user = current_user
        elif not hasattr(g, 'user'):
            g.user = None


@annotate.after_request
def after_request(response):
    ac = 'Access-Control-'
    rh = response.headers
    rh[ac + 'Allow-Origin'] = request.headers.get('origin', '*')
    rh[ac + 'Expose-Headers'] = 'Content-Length, Content-Type, Location'
    if request.method == 'OPTIONS':
        rh[ac + 'Allow-Headers'] = ('Content-Length, Content-Type, '
                                    'X-Requested-With')
        rh[ac + 'Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        rh[ac + 'Max-Age'] = '86400'
    return response


# ROOT
@annotate.route('/')
def root():
    return jsonify({
        'message': "Annotator Store API",
        'links': {
            'annotation': {
                'create': {
                    'method': 'POST',
                    'url': url_for('.create_annotation', _external=True),
                    'query': {
                        'refresh': {
                            'type': 'bool',
                            'desc': ("Force an index refresh after create "
                                     "(default: true)")
                        }
                    },
                    'desc': "Create a new annotation"
                },
                'read': {
                    'method': 'GET',
                    'url': url_for('.read_annotation',
                                   id=':id',
                                   _external=True),
                    'desc': "Get an existing annotation"
                },
                'update': {
                    'method': 'PUT',
                    'url':
                    url_for(
                        '.update_annotation',
                        id=':id',
                        _external=True),
                    'query': {
                        'refresh': {
                            'type': 'bool',
                            'desc': ("Force an index refresh after update "
                                     "(default: true)")
                        }
                    },
                    'desc': "Update an existing annotation"
                },
                'delete': {
                    'method': 'DELETE',
                    'url': url_for('.delete_annotation',
                                   id=':id',
                                   _external=True),
                    'desc': "Delete an annotation"
                }
            }
        }
    })


# INDEX
@annotate.route('/annotations/<url>')
def index(url):
    entry = Entry.query.filter_by(url=url).first()
    annotations = entry.annotations.all()
    data = []
    for e in annotations: 
        ann = e.to_json()
        data.append(ann)
    return jsonify(data)


# CREATE
@annotate.route('/annotations', methods=['POST'])
@login_required
@admin_required
def create_annotation():
    # Only registered users can create annotations
    if not current_user.is_administrator():
        return _failed_authz_response('create annotation')
    if request.json is not None:
        entry = Entry.query.order_by(Entry.id.desc()).first()
        annotation = Annotation.from_json(request.json)
        if hasattr(g, 'before_annotation_create'):
            g.before_annotation_create(annotation)
        db.session.add(annotation)
        annotation = Annotation.query.order_by(Annotation.id.desc()).first()
        entry.annotations.append(annotation)
        db.session.add(entry)
        if hasattr(g, 'after_annotation_create'):            
            g.after_annotation_create(annotation)        
        location = url_for('.read_annotation', id=annotation.id, _external=True)
        return jsonify(Annotation.to_json(annotation)), 201, {'Location': location}
    else:
        return jsonify('No JSON payload sent. Annotation not created.',
                       status=400)


# READ
@annotate.route('/annotations/<int:id>')
def read_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    return jsonify(annotation.to_json())


# UPDATE
@annotate.route('/annotations/<id>', methods=['POST', 'PUT'])
def update_annotation(id):
    annotation = Annotation.query.get(id)
    if not annotation:
        return jsonify('Annotation not found! No update performed.',
                       status=404)
    if request.json is not None:
        updated = Annotation.from_json(request.json)
        updated['id'] = annotation.id
        db.session.add(annotation)
    return jsonify(annotation)


# DELETE
@annotate.route('/annotations/<id>', methods=['DELETE'])
def delete_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    db.session.delete(annotation)
    return '', 204