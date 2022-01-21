from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, BuyForm, SellForm, CreateForm, UnlistForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import uuid
import os

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
def market_page():
    available_items = Item.query.filter(Item.listed).all()
    return render_template('market.html', available_items=available_items)

@app.route('/myitems')
@login_required
def myitems_page():
    my_items = Item.query.filter_by(owner=current_user.id).all()
    return render_template('myitems.html', my_items=my_items)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_page():
    form = CreateForm()
    if form.validate_on_submit():
         # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_extension = filename.split('.')[1]
            unique_id = uuid.uuid4().hex
            unique_filename = unique_id + '.' + file_extension
            file.save(os.path.join(app.config['UPLOAD_PATH'], unique_filename))
            item_to_create = Item(name=form.name.data,
                            price=form.price.data,
                            description=form.description.data,
                            owner=current_user.id,
                            img_filename=unique_filename)
            db.session.add(item_to_create)
            db.session.commit()
            flash('Item created.', category='success')
            return redirect(url_for('myitems_page'))
    return render_template('create.html', form=form)


@app.route('/detail/<int:item_id>', methods=['GET','POST'])
@login_required
def detail_page(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if current_user.can_purchase(item):
            seller = item.owned_user
            current_user.budget -= item.price
            seller.budget += item.price
            item.owner = current_user.id
            item.listed = False
            db.session.commit()
            flash(f'Purchase complete. You bought {item.name} for {item.price} coins.', category='success')
        else:
            flash(f'Purchase rejected. Insufficient funds. You need at least {item.price} coins.', category='danger')
        return redirect(url_for('market_page'))

    if request.method == "GET":
        buy_form = BuyForm()
        sell_form = SellForm()
        unlist_form = UnlistForm()
    return render_template('detail.html', item=item, buy_form=buy_form, sell_form=sell_form, unlist_form=unlist_form)

@app.route('/relist/<int:item_id>', methods=['GET','POST'])
@login_required
def relist_page(item_id):
    item = Item.query.filter_by(id=item_id).first()
    form = SellForm()
    if request.method == "POST":
        if not item.listed and current_user.can_list(item):
            item.listed = True
            item.name = form.name.data
            item.price = form.price.data
            item.description = form.description.data
            db.session.commit()
            flash(f'Listing complete. You listed {item.name} for {item.price} coins.', category='success')
        else:
            flash('There was a problem listing this item.', category='danger')
        return redirect(url_for('myitems_page'))

    if request.method == "GET":
        form.name.data = item.name
        form.price.data = item.price
        form.description.data = item.description
        return render_template('relist.html', form=form)

@app.route('/unlist/<int:item_id>', methods=['POST'])
@login_required
def unlist_page(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if item.listed and current_user.can_list(item):
        item.listed = False
        db.session.commit()
        flash(f'Complete. You unlisted {item.name}.', category='success')
    else:
        flash('There was a problem unlisting this item.', category='danger')
    return redirect(url_for('myitems_page'))

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data
                            )
        db.session.add(user_to_create)
        db.session.commit()
        # before redirect, log the new user in so they can see the market page immediately
        login_user(user_to_create)
        flash(f'Account created successfully. Logged in as {user_to_create.username}', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #if there are validation errors, iterate through them and feedback to user
        for err_msg in form.errors.values():
            flash(f'The was an error creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Successful login. Logged in as {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Incoreect username or password. Please try again.', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out', category='info')
    return redirect(url_for('home_page'))

@app.route('/user/<username>')
@login_required
def user_profile(username):
    return f'<h1>Profile page for user: {username}</h1>'