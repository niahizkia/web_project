import datetime
from flask_app import database
from peewee import *

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

def create_tables():
    with database:
        database.create_tables([Sold])