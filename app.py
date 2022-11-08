import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from peewee import *
from hashlib import md5
import pandas as pd


app = Flask(__name__)
app.secret_key = 'jdfjnviuhd87432fdjkfa.kjfj'


DATABASE = 'product.db'
database = SqliteDatabase(DATABASE)




class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    username = CharField(unique = True)
    password = CharField()
    join_at  = DateTimeField(default=datetime.datetime.now())

class Product(BaseModel):
    product_id    = CharField(unique = True)
    product_name  = TextField()
    price         = IntegerField()

class Sold(BaseModel):
    buyer_name     = TextField()
    buyer_address  = TextField()
    region         = TextField()
    city           = TextField()
    phone_number   = TextField()
    sold_at        = DateTimeField(default=datetime.datetime.now())
    bought_product = TextField()
    quantity       = IntegerField()
    total          = IntegerField()



@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response


def create_tables():
    with database:
        database.create_tables([Sold])


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

def export():
    con = database
    # cursor = config.cursor()
    sql_query = pd.read_sql_query("""
    SELECT * FROM Sold
    """, con)


    df = pd.DataFrame(sql_query)
    df = df.to_excel(r'/home/niahizkia/projects/web_project/static/file/export.xlsx', index = False) # place 'r' before the path name
    return render_template('index.html')
    
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
            flash('Username or password is wrong!')

        else:
            auth_user(user)
            # current_user = get_current_user()
            # return current_user.username
            return redirect(url_for('input_product')) 

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Log out success..')
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
        # try:
        # with database.atomic():
        Sold.create(
            buyer_name     = request.form['name'],
            buyer_address  = request.form['alamat'],
            region         = request.form['provinsi'],
            city           = request.form['kota'],
            phone_number   = request.form['phone'],
            bought_product = request.form['product'],
            quantity       = request.form['quantity'],
            total          = request.form['total'],
            sold_at        = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        export()
        flash('Data berhasil di input')
            # auth_user(user)
        return redirect(url_for('input_product'))

        # except IntegrityError:
        #     flash('Username already exist')
    return render_template('index.html')

from flask_paginate import Pagination, get_page_args

@app.route('/database/', methods=['GET'])
@login_required
def show_data():
    data = pd.read_excel('static/file/export.xlsx')
    total = len(data)

    # page = request.args.get(get_page_parameter(), type=int, default=1)
    page, per_page, offset = get_page_args(per_page_parameter="pp", pp=5)

    # g.cur.execute(sql)
    if per_page:
        users = Sold.select().order_by(Sold.sold_at.desc()).limit(5).offset(offset)
    else:
        users = Sold.select().order_by(Sold.sold_at.desc())
    
    pagination = Pagination(page=page, 
                            total=total, 
                            record_name='data', 
                            per_page=per_page,
                            format_total=True,
                            format_number=True,)

    return render_template('show_data.html',
                           users=users,
                           pagination=pagination,
                           )
