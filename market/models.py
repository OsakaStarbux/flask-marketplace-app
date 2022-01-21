from market import db, login_manager, app
from market import bcrypt
from flask_login import UserMixin
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    def __repr__(self):
        return f'id: {self.id}, username: {self.username}, email: {self.email_address}, password hash: {self.password_hash}'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')


    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_list(self, item_obj):
        return self.id == item_obj.owner



class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    img_filename = db.Column(db.String(length=32), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    listed = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return f'{self.name}'

    @property
    def img_url(self):
        return os.path.join(app.config['UPLOAD_PATH'], self.img_filename)