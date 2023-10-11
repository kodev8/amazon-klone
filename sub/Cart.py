from itertools import zip_longest
from flask_login import current_user
from flask import session
from datetime import datetime
from sub.Product import Product
from config import products, carts

class Cart:

    @staticmethod
    def clear_cart():
        if session.get('cart'):
            session['cart'] = []

    @staticmethod
    def load_cart():
        cart =  session['cart'] if not current_user.is_authenticated else  [Product.dump(product, id_field='product_id', merge=True) for product in carts.find_one({'user_id': current_user.id}, {'products':1})['products']]
        if current_user.is_anonymous:
            cart.sort(key=lambda x: x.get('date_added'), reverse=True)
        else:
            cart.sort(key=lambda x: x.date_added, reverse=True)
        return cart
    
    @staticmethod
    def add_product(cart, product: Product, qty: int, how='same'):
        if qty <= 0:
            return 
        if not current_user.is_authenticated:
            id = str(product.get('_id'))

            found = False
            for cart_product in cart:
                if cart_product.get('_id') == id:
                    if how=='same':
                        print('only sameinf\n')
                        cart_product['qty'] = int(qty)
                    else:
                        cart_product['qty'] += int(qty)
                    found=True
                    break

            if not found:
                product_dict = {
                    'qty':int(qty), 'date_added':datetime.now(),'selected':True, 
                }
               
                product_dict |= product.__dict__ 
                product_dict['_id'] = id
                print('I WAS JUST ADDED:',product_dict)
                cart.append(product_dict)
        else:

            print('in cart add how: ', how, '\n')
            existing_product = carts.find_one(
                {
                    'user_id': current_user.id,
                    'products.product_id': product._id
                },
                {'products.$': 1}
            )

            if existing_product:
                if how == 'same':
                    update_operation = {
                            '$set': {
                                'products.$[elem].qty': qty
                            }
                        }
                    array_filter = [
                        {
                            'elem.product_id': product._id
                        }
                    ]

                    # Update the document
                    carts.update_one(
                        {'user_id': current_user.id},
                        update_operation,
                        array_filters=array_filter
                    )

                    product.qty = qty
                else:

                # Product exists, so increment qty
                    carts.update_one(
                        {
                            'user_id': current_user.id,
                            'products.product_id': product._id
                        },
                        {
                            '$inc': {
                                'products.$.qty': qty
                            }
                        }
                    )
                    product.qty += qty

            else:
                # Product does not exist, so add a new product
                print('adding new')
                new_product = {
                    'product_id':product._id,
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

    @staticmethod
    def remove_product(cart, product, ):
        
        if current_user.is_anonymous:
            del_item = None
            for item in cart:
                print('ITEM', item)
                if str(product.get('_id')) == item.get('_id'):
                    del_item = item
                    break
            if del_item:
                cart.remove(del_item)

        else:
            update_operation = {
            '$pull': {
                'products': {
                    'product_id': product._id
                }
            }
            }

            # Update the document to remove the product
            result = carts.update_one(
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
                'elem.product_id': product._id
            }
        ]

        result = carts.update_one(
            {'user_id': current_user.id},
            update_operation,
            array_filters=array_filter
        )


    @staticmethod
    def sub_total(cart):
        sub_total = sum(float(product.get('price')) * int(product.get('qty')) for product in cart if product.get('selected'))
        if sub_total != 0:
            return f'{sub_total:0.2f}'
        return 0




