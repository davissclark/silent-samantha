from datetime import date
from flask import render_template, redirect, url_for, flash, abort,\
    request, current_app
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from ..models import Entry, Tag, User, Comment, Permission
from ..decorators import permission_required
import keen


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['BLOG_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
def index():
    return render_template('landing.html')


@main.route('/recent')
def entries():
    entries = Entry.query.order_by(Entry.published.desc()).all()
    return render_template('blog.html', entries=entries)


@main.route('/<int:eyear>/<int:emonth>/<url>')
def entry(eyear, emonth, url):
    keen.add_event('popular_content', {
        "entry": url,
        "yearPublished": eyear,
        "monthPublished": emonth
        })
    entry = Entry.query.filter_by(url=url).first()
    tags = entry.tags.all()
    comments = entry.comments.order_by(Comment.timestamp.asc()).all()
    return render_template('entry.html', entries=[entry], comments=comments,
                           tags=tags)


@main.route('/metrics')
def about():
    return render_template('metrics.html')


@main.route('/filter/<tag>')
def topic(tag):
    topic = Tag.query.filter_by(url=tag).first() or Tag.query.filter_by(name=tag).first()
    entries = topic.entries.all()
    return render_template('blog.html', entries=entries, topic=topic)


@main.route('/archive/<int:year>/<int:month>')
def archive(year, month):
    start = date(year, month, 1)
    end = date(year, month+1, 1)
    entries = Entry.query.filter((start<=Entry.published) & (Entry.published<end)).all()
    return render_template('blog.html', entries=entries)