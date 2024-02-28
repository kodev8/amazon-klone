from flask_login import current_user
from flask import session
from datetime import datetime
from sub.Product import Product
from config import carts, logging
from bson import ObjectId
from models import db, User

class Cart:

    @staticmethod
    def clear_cart():
        if session.get('cart'):
            session['cart'] = []

    @staticmethod
    def load_cart():
        cart =  session['cart'] if not current_user.is_authenticated else  [Product.dump(product, id_field='product_id', merge=True) for product in carts.find_one({'user_id': current_user.id}, {'products':1})['products']]
        cart.sort(key=lambda x: x.get('date_added'), reverse=True)

        return cart
    
    @staticmethod
    def get_product_by_id(cart, product_id):
        for item in cart:
            # print("=========cart item : ", item.get("_id"), "remove item",product_id)
            if str(item.get('_id')) == str(product_id):
                # print('found!!!!!!', item)
                return item
            
    
    @staticmethod
    def set_product(cart, product: dict, qty: int, how='same'):

        """ sets a product and its data within a cart, products should be passed as a dict 
        if it is a proudct instance, it will be converted to a dict"""
        if qty < 0:
            raise ValueError('qty must be greater than 0')
        
        if type(product) == Product:
            product = product.__dict__
        
        # if the current user is anonymous, they are using a cart of dicts
        if not current_user.is_authenticated:
            id = str(product.get('_id'))

            # check if product is already in cart, if it is found, increment qty
            found = False
            for cart_product in cart:
                if cart_product.get('_id') == id:

                    if how=='same':
                        cart_product['qty'] = int(qty)
                    else:
                        cart_product['qty'] += int(qty)
                    found = True
                    break
            
            # if product is not found, add it to cart with qty and make sure it is selected with a date so that it goes towards selected subcount
            if not found:
                product_dict = {
                    'qty':int(qty), 'date_added':datetime.now(),'selected':True, 
                }

                if type(product) == Product:
                    product_dict |= product.__dict__ 
                else:
                    product_dict |= product

                product_dict['_id'] = id
                cart.append(product_dict)

            return cart

        # if the current user is authenticated, they are using a cart of Product instances
        else:
            
            # check if product is already in cart, if it is found, increment qty
            existing_product = carts.find_one(
                {
                    'user_id': current_user.id,
                    'products.product_id': ObjectId(product.get('_id'))
                },
                {'products.$': 1}
            )

            # if no product is found in the mongo db cart, add it and set the qty
            if not existing_product:

                # print('ITEM NOT FOUND SO ADDING AS NEW')

                # Product does not exist, so add a new product
                # print('adding new')
                new_product = {
                    'product_id': ObjectId(product.get('_id')),
                    'qty':qty,
                    'selected':True,
                    'date_added': datetime.now()
                }

                carts.update_one(
                    {'user_id': current_user.id},
                    {
                        '$push': {
                            'products': new_product
                        }
                    }
                )

        

            else:
            
                # print('ITEM FOUND SO ADDING AS INCREMENTING')

                if how == 'same':

                    update_operation = {
                        '$set': {
                            'products.$[elem].qty': qty
                        }
                    }
                    array_filter = [
                        {
                            'elem.product_id':  ObjectId(product.get('_id'))
                        }
                    ]

                    # Update the document
                    carts.update_one(
                        {'user_id': current_user.id},
                        update_operation,
                        array_filters=array_filter
                    )


                
                else:

                # Product exists, so increment qty
                    carts.update_one(
                        {
                            'user_id': current_user.id,
                            'products.product_id':  ObjectId(product.get('_id'))
                        },
                        {
                            '$inc': {
                                'products.$.qty': qty
                            }
                        }
                        )
                # return the updated care

                # if type (product) == dict:
                #     product['qty']  += qty
                # elif type(product) == Product:
                #     product.qty += qty
                

    @staticmethod
    def remove_product(cart, product):
        
        if current_user.is_anonymous:
            del_item = None
            for item in cart:
                # print('ITEM', item)
                if str(product.get('_id')) == item.get('_id'):
                    del_item = item
                    break

            if del_item:
                cart.remove(del_item)

        else:
            update_operation = {
            '$pull': {
                'products': {
                    'product_id':  ObjectId(product.get('_id'))
                }
            }
            }

            # Update the document to remove the product
            carts.update_one(
                {'user_id': current_user.id},
                update_operation
            ) 

    # @staticmethod      
    # def merge_carts(cart, user: User):
    #     return

    @staticmethod
    def count(cart,):

        if current_user.is_anonymous:
            # print('I AM CART IN CART COUNT', cart)
            # for product in cart:
            #     print('A PRODUCT IS:', product)

            return sum(product.get('qty', 0) for product in cart)
        
        else:

            count = list(carts.aggregate([ {
                    "$match": {"user_id": current_user.id}  # Match documents for the specified user_id
                },
                {
                    "$unwind": "$products"  # Unwind the products array
                },
                {
                    "$group": {
                        "_id": None,  
                        "totalQty": {"$sum": "$products.qty"}  # Sum the qty field for each product
                }
                 }
                 ])
                )
            
            count = 0 if not count else count[0]['totalQty'] 

            return count
        
    @staticmethod
    def update_selected_auth(product, how=True):
        
        update_operation = {
            '$set': {
                'products.$[elem].selected': how
            }
        }

        array_filter = [
            {
                'elem.product_id': product.get('_id')
            }
        ]

        carts.update_one(
            {'user_id': current_user.id},
            update_operation,
            array_filters=array_filter
        )


    @staticmethod
    def sub_total(cart):
        return sum(float(product.get('price')) * int(product.get('qty')) for product in cart if product.get('selected'))
    
    @staticmethod
    def setup():
        adding = False

        # carts normally created on registration
        for user in db.session.scalars(db.select(User)).all():

            if not carts.find_one({'user_id': user.id}):
                adding = True
                carts.insert_one({'user_id': user.id, 'products': []})

        if not adding:
            logging.info(f"{__name__} setup not needed @ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        logging.info(f"{__name__} setup complete @ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            