from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, relationship
from flask_login import UserMixin
from datetime import datetime
from sub.Product import Product


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
 
# USERS
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = mapped_column(db.Integer(), primary_key=True)
    fname = mapped_column(db.String(50), nullable=False)
    lname = mapped_column(db.String(50), nullable=False)
    email = mapped_column(db.String(255), unique =True, nullable=False)
    dob = mapped_column(db.Date(), nullable=False)
    password = mapped_column(db.String(255), nullable=False)
    user_since = mapped_column(db.Date(), nullable=False, default=datetime.today())

    addresses = relationship(
    'Address',
    back_populates='user',
    order_by='Address.is_default.desc()'
    )   


    orders = relationship(
    'Order',
    back_populates='user',
    )   

    favourites = relationship(
    'Favourite',
    back_populates='user',
    ) 

 
    @staticmethod
    def get_by_id(user_id):
        return db.session.scalars(db.select(User).filter_by(id=user_id)).first()
    
    @staticmethod
    def get_by_email(username):
        query = db.select(User).filter_by(email=username)
        return  db.session.scalars(query).first()
    
    
class Address(db.Model):

    __tablename__ = 'addresses'
    id = mapped_column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = mapped_column(db.ForeignKey('users.id'), )
    line1 =  mapped_column(db.String(255), nullable=False)
    city =  mapped_column(db.String(255), nullable=False)
    country =  mapped_column(db.String(255), nullable=False)
    zip_code =  mapped_column(db.Integer(), nullable=False)
    is_default=mapped_column(db.Boolean(), nullable=False, default=False)


    user = relationship(
    'User',
    back_populates='addresses',
    )  

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = mapped_column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = mapped_column(db.ForeignKey('users.id'), nullable=False)
    product_id =  mapped_column(db.String(255), nullable=False)
    ordered_at = mapped_column(db.Date(), nullable=False, default=datetime.today())
    # pending, complete, canceled, refunded
    status = mapped_column(db.String(10), nullable=False)


    user = relationship(
    'User',
    back_populates='orders',
    )   


# FAVOIRTIES
class Favourite(db.Model):
    __tablename__ = 'favourites'
    favourite_user = mapped_column(db.ForeignKey('users.id'), primary_key=True, nullable=False)
    product_id = mapped_column(db.Integer(), primary_key=True, nullable=False)
    favourited_at = mapped_column(db.DateTime(),nullable=False, default=datetime.now())

    user = relationship(
    'User',
    back_populates='favourites',
    )   

    def get_product(self):
    
        if not hasattr(self, 'product'):
            print('mergin producr')
            self.product = Product(self.product_id)

    