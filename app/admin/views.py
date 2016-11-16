from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .. import db
from ..models import Entry, Tag, User, Role, gravatar
from ..decorators import admin_required
from . import admin
from .forms import EntryForm, TagForm, EditProfileAdminForm


def is_topic(name):
    return Tag.query.filter_by(name=name).first() is not None


@admin.route('/publish/article', methods=['GET', 'POST'])
@login_required
@admin_required
def publish():
    form = EntryForm()
    if form.validate_on_submit():
        entry = Entry(title=form.title.data, body=form.body.data)
        db.session.add(entry)
        return redirect(url_for('main.entries'))
    entries = Entry.query.order_by(Entry.published.desc()).all()
    return render_template('admin/publish.html', entries=entries, form=form)


@admin.route('/edit/article/<url>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(url):
    entry = Entry.query.filter_by(url=url).first_or_404()
    form = EntryForm()
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.body = form.body.data
        entry.url = entry.format_url(entry.title)
        db.session.add(entry)
        flash('Entry updated')
        return redirect(url_for('main.entry', eyear=entry.published.year, emonth=entry.published.month, url=entry.url))
    form.title.data = entry.title
    form.body.data = entry.body
    return render_template('admin/edit_entry.html', entries=[entry], form=form)


@admin.route('/delete/article/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    if request.method == 'POST':
        entry = Entry.query.get_or_404(id)
        db.session.delete(entry)
        flash('Entry successfully deleted')
        return redirect(url_for('main.entries'))


@admin.route('/tag/article/<url>', methods=['GET', 'POST'])
@login_required
@admin_required
def tag(url):
    entry = Entry.query.filter_by(url=url).first_or_404()
    tags = entry.tags.all()
    name = None
    form = TagForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        if not is_topic(name):
            tag = Tag(name)
            db.session.add(tag)
        t = Tag.query.filter_by(name=name).first()
        entry.tags.append(t)
        db.session.add(entry)
        return redirect(url_for('main.entry', eyear=entry.published.year, emonth=entry.published.month, url=entry.url))
    return render_template('admin/tag.html', entries=[entry], tags=tags,
                           id=id, form=form, name=name)


@admin.route('/delete/<tag>', methods=['GET'])
@login_required
@admin_required
def deleteTopic(tag):
    tag = Tag.query.filter_by(name=tag).first()
    db.session.delete(tag)
    flash('Topic successfully deleted')
    return redirect(url_for('main.entries'))


@admin.route('/delete/<int:entry>/<int:tag>', methods=['GET'])
@login_required
@admin_required
def deleteTag(entry, tag):
    entry = Entry.query.get_or_404(entry)
    tag = Tag.query.get_or_404(tag)
    entry.tags.remove(tag)
    db.session.add(entry)
    return redirect(url_for('main.entry', eyear=entry.published.year, emonth=entry.published.month, url=entry.url))



@admin.route('/edit/profile/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(email):
    user = User.query.filter_by(email=current_user.email).first()
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('main.entries'))
    form.name.data = user.name
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/edit_profile.html', form=form, user=user)