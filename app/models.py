from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from app.exceptions import ValidationError
import simplejson as json
from . import db, login_manager


def gravatar(size=200, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        email = current_app.config['BLOG_ADMIN']
        hash = hashlib.md5(email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class Permission:
    COMMENT = 0x01
    READ_ANNOTATIONS = 0x02
    MODERATE_COMMENTS = 0x04
    PUBLISH = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Reader': (Permission.COMMENT |
                       Permission.READ_ANNOTATIONS, True),
            'Assistant': (Permission.COMMENT |
                          Permission.READ_ANNOTATIONS |
                          Permission.MODERATE_COMMENTS, False),
            'Author': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


savedmap = db.Table('savedmap',
                    db.Column('entry_id', db.Integer, db.ForeignKey('entries.id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    entries = db.relationship('Entry', backref='author', lazy='dynamic')
    favorites = db.relationship('Entry',
                                secondary=savedmap,
                                backref=db.backref('fans', lazy='dynamic'),
                                lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BLOG_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Generates a token with a default validity time of one hour
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # Verifies the token and, if valid, sets the new confirmed attribute to True
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def save_entry(self, entry):
        if not self.is_saved(entry):
            f = Entry.query.get(id=entry.id).first()
            self.favorites.append(f)
            db.session.add(self)

    def unsave_entry(self, entry):
        f = self.favorites.filter_by(entry_id=entry.id).first()
        if f:
            db.session.delete(f)

    def is_saved(self, entry):
        return self.favorites.filter_by(
            id=entry.id).first() is not None

    def to_json(self):
        json_user = {
            'url': url_for('api.get_entry', id=self.id, _external=True),
            'name': self.name,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'entries': url_for('api.get_user_entries', id=self.id,
                               _external=True),
            'favorites': url_for('api.get_user_favorites', id=self.id,
                                 _external=True),
            'entry_count': self.favorites.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.name


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


tagmap = db.Table('tagmap',
                  db.Column('entry_id', db.Integer, db.ForeignKey('entries.id')),
                  db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                  )


class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    published = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    url = db.Column(db.String(120), index=True, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='entry', lazy='dynamic')
    annotations = db.relationship('Annotation', backref='entry', lazy='dynamic')
    tags = db.relationship('Tag',
                           secondary=tagmap,
                           backref=db.backref('entries', lazy='dynamic'),
                           lazy='dynamic')

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.url = self.format_url(title)

    def __repr__(self):
        return '<Entry %r>' % self.title

    @staticmethod
    def format_url(title):
        url = title.replace(' ', '-').lower()
        if url.startswith('the-'):
            url = url[4:]
        url = ''.join(e for e in url if e.isalnum() or e == '-')
        return url

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'img', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'kbd']
        target.body_html = markdown(value, output_format='html')



    def to_json(self):
        share_entry = {
            'content': {
                'title': self.title,
                'description': self.body,
                'submitted_url': url_for('main.entry', eyear=self.published.year, emonth=self.published.month, url=self.url, _external=True)
            },
            'comment': 'Check out this neat entry published by Davis Clark.',
            'visibility': {
                'code': 'anyone'
            }
        }
        return json.dumps(share_entry)

    @staticmethod
    def from_json(json_entry):
        title = json_entry.get('title')
        if title is None or title == '':
            raise ValidationError('entry does not have a title')
        body = json_entry.get('body')
        if body is None or body == '':
            raise ValidationError('entry does not have a body')
        return Entry(title=title, body=body)


db.event.listen(Entry.body, 'set', Entry.on_changed_body)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    url = db.Column(db.String(64), index=True)

    def __init__(self, name):
        self.name = name
        self.url = self.format_url(name)

    def __repr__(self):
        return '<Topic %r>' % self.name

    @staticmethod
    def format_url(name):
        url = name.replace(' ', '-').lower()
        if url.startswith('the-'):
            url = url[4:]
        url = ''.join(e for e in url if e.isalnum() or e == '-')
        return url


class Annotation(db.Model):
    __tablename__ = 'annotations'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    quote = db.Column(db.Text)
    text = db.Column(db.Text)
    uri = db.Column(db.String(120))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start = db.Column(db.String(120))
    end = db.Column(db.String(120))
    startOffset = db.Column(db.Integer)
    endOffset = db.Column(db.Integer)
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))

    def __init__(self, quote, text, start, end, startOffset, endOffset, *args, **kwargs):
        self.created = datetime.utcnow()
        self.quote = quote
        self.text = text
        self.start = start
        self.end = end
        self.startOffset = startOffset
        self.endOffset = endOffset


    def to_json(self):
        json_annotation = {
            "id": self.id,
            "created": str(self.created),
            "updated": str(self.updated),
            "quote": self.quote,
            "text": self.text,
            "uri": url_for('main.index', _external=True),
            "ranges": [
                {
                    "start": self.start,
                    "end": self.end,
                    "startOffset": self.startOffset,
                    "endOffset": self.endOffset
                }
            ],
            "links": [
                {
                    "href": url_for('annotate.read_annotation',
                        id=self.id,
                        _external=True),
                    "type": "text/html",
                    "rel": "alternate"
                }
            ]
        }
        return json_annotation

    @staticmethod
    def from_json(json_string):
        data = json_string
        quote = data['quote']
        if quote is None or quote == '':
            raise ValidationError('annotation does not have a quote')
        text = data['text']
        if text is None or text == '':
            raise ValidationError('annotation does not have a text')
        start = data['ranges'][0]['start']  
        if start is None or start == '':
            raise ValidationError('annotation does not have a start')
        end = data['ranges'][0]['end']
        if end is None or end == '':
            raise ValidationError('annotation does not have an end')
        startOffset = data['ranges'][0]['startOffset']
        if startOffset is None or startOffset == '':
            raise ValidationError('annotation does not have a startOffset')
        endOffset = data['ranges'][0]['endOffset']
        if endOffset is None or endOffset == '':
            raise ValidationError('annotation does not have an endOffset')
        entryUrl = data['entryUrl']
        if entryUrl is None or entryUrl == '':
            raise ValidationError('annotation does not have an entryUrl')
        return Annotation(quote=quote, text=text, start=start, end=end, startOffset=startOffset, endOffset=endOffset, entry=Entry.query.filter_by(url=entryUrl).first())


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))

    def __init__(self, body, entry, *args, **kwargs):
        self.body = body
        self.entry = entry
        self.timestamp = datetime.utcnow()
        self.author = current_user._get_current_object()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)
