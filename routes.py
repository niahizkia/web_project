import datetime
from functools import wraps

from flask import render_template, request, redirect, url_for, session, flash
from hashlib import md5
import pandas as pd
from models import User, Sold
from flask_app import app, database
from flask_paginate import Pagination, get_page_args


@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response


# ==========================================================================================
# ========= HELPER FUNCTION ================================================================
# ==========================================================================================

def auth_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    flash('Login success as '+ session['username'])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def login_fulfill(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('input_product'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================================================================
# ========= ROOTING AUTHENTICATION =========================================================
# ==========================================================================================


@app.route('/login', methods=['GET','POST'])
@login_fulfill
def login():
    if request.method == 'POST' and request.form['username']:
        try:
            hashed_pass = md5(request.form['password'].encode('utf-8')).hexdigest(),
            user        = User.get(
                            (User.username == request.form['username']) &
                            (User.password == hashed_pass))
        except User.DoesNotExist:
            msg = "Username or password is wrong!"
            return render_template('login.html', message=msg)
        else:
            auth_user(user)
            return redirect(url_for('input_product')) 
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@login_fulfill
def register():
    if request.method == 'POST' and request.form['username']:
        try:
            with database.atomic():
                user = User.create(
                    username = request.form['username'],
                    password = md5(request.form['password'].encode('utf-8')).hexdigest(),
                    email    = request.form['email']
                )
            auth_user(user)
            return redirect(url_for('input_product'))

        except IntegrityError:
            flash('Username already exist')
    return render_template('register.html')


@app.route('/', methods=['POST','GET'])
@login_required
def input_product():
    if request.method == 'POST':
        Sold.create(
            buyer_name     = request.form['name'],
            buyer_address  = request.form['alamat'],
            region         = request.form['provinsi'],
            city           = request.form['kota'],
            phone_number   = request.form['phone'],
            bought_product = request.form['product'],
            quantity       = request.form['quantity'],
            total          = request.form['total'],
            sold_at        = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
        )
        return redirect(url_for('input_product'))
    return render_template('index.html')


@app.route('/database/', methods=['GET', 'POST'])
@login_required
def show_data():
    data = Sold.select().order_by(Sold.sold_at.desc())
    total = len(data)

    page, per_page, offset = get_page_args(per_page_parameter="pp", pp=5)

    if per_page:
        users = Sold.select().order_by(Sold.sold_at.desc()).limit(5).offset(offset)
    else:
        users = Sold.select().order_by(Sold.sold_at.desc())
    
    pagination = Pagination(page=page, total=total, record_name='data', 
                            per_page=per_page, format_total=True, format_number=True)

    return render_template('show_data.html', users=users, pagination=pagination)

@app.route('/download', methods = ['GET', 'POST'])
def export():
    con = database
    # cursor = config.cursor()
    sql_query = pd.read_sql_query("""SELECT * FROM Sold""", con)
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    to_date = to_date+' 23:59:59'
    
    df = pd.DataFrame(sql_query)
    filtered_df = df.loc[(df['sold_at'] >= from_date) & (df['sold_at'] <= to_date)]
    filtered_df.to_excel(r'/home/niahizkia/projects/web_project/static/file/export.xlsx', index = False) # place 'r' before the path name
    return redirect(url_for('static', filename='file/export.xlsx'))
    

@app.route('/edit', methods=['POST','GET'])
@login_required
def edit_product():
    user = Sold.get(
        (Sold.id == request.form['user_id'])
    )
    return render_template('edit.html', user=user)


@app.route('/update/<int:user_id>', methods=['POST','GET'])
def update(user_id):    
    if request.method == 'POST':
        user = Sold.select().where(Sold.id == user_id).get()
        user.buyer_name     = request.form['name']
        user.buyer_address  = request.form['alamat']
        user.region         = request.form['provinsi']
        user.city           = request.form['kota']
        user.phone_number   = request.form['phone']
        user.bought_product = request.form['product']
        user.quantity       = request.form['quantity']
        user.total          = request.form['total']
        user.save()
        return redirect(url_for('show_data'))
    else:
        return render_template('show_data.html')


@app.route('/delete/<int:user_id>', methods=['POST','GET'])
def delete(user_id):
    user = Sold.get(Sold.id == user_id)
    user.delete_instance()
    return redirect(url_for('show_data'))


@app.route('/confirmation', methods=['POST','GET'])
def confirmation():
    user_id = request.form['user_id']
    return render_template('delete.html', user_id=user_id)