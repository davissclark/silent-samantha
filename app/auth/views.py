from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Entry, Comment, Tag, gravatar
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangeEmailForm, PasswordResetForm, \
    PasswordResetRequestForm, ChangePasswordForm
from ..admin.forms import EditProfileAdminForm
import mailchimp
import keen


def get_mailchimp_api():
    return mailchimp.Mailchimp('14bf0532b4abb7328670965deed30986-us9')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.entries'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember_me)
            return redirect(url_for('main.entries'))
        flash('Invalid username or password')
        form.email.data = ''
    entries = Entry.query.order_by(Entry.published.desc()).all()
    return render_template('auth/login.html', form=form, entries=entries)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.entries'))


@auth.route('/subscribe', methods=['POST'])
def subscribe():
    m = get_mailchimp_api()
    lid = '3c734f704d'
    if request.method == 'POST' and request.form['EMAIL']:
        m.lists.subscribe(lid,{'email':request.form['EMAIL']})
        keen.add_event("subscribed", {
            
            })
        flash("Awesome! You'll receive an email to confirm your subscription.")
    else: 
        flash("Enter your email address to subscribe!")
    return redirect(url_for('main.entries'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    name=form.name.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    entries = Entry.query.order_by(Entry.published.desc()).all()
    form.email.data = ''
    form.name.data = ''
    return render_template('auth/register.html', form=form, entries=entries)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.entries'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.entries'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.entries'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.entries'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.entries'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.entries'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.entries'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.entries'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    user = User.query.filter_by(email=current_user.email).first()
    form = EditProfileAdminForm(user=user)
    base = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.entries'))
        else:
            flash('Invalid email or password.')
    form.name.data = user.name
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("auth/change_email.html", form=form, user=user, base=base)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.entries'))


@auth.route('/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def comment(id):
    entry = Entry.query.get_or_404(id)
    comments = entry.comments.all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          entry=entry,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('main.entry', eyear=entry.published.year, emonth=entry.published.month, url=entry.url))
    return render_template('auth/comment.html', entries=[entry], comments=comments, form=form)