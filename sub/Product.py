from bson import ObjectId
from config import products
import math

class Product:

    __cached_products = {}
    TAX = 0.2
    SHIPPING = 0.1
    
    def __new__(cls, product_id, as_dump=False, **kwargs):
        
        if not as_dump:
            # check if product is a string or ObjectId and search the db for it
            product_type = type(product_id)

            if product_type not in (ObjectId, str):
                raise TypeError(f'Product must be objectID or Sting not {product_type}')
            
            # raises error if cannot convert to object id
            if product_type == str:
                product_id = ObjectId(product_id)

        cached = cls.__cached_products.get(product_id)
        if cached:
            return cached
        
        product_instance = super().__new__(cls)
        product_instance._id = product_id
        return product_instance

    def __init__(self,  product_id, as_dump=False, **kwargs):

        if self._id in Product.__cached_products:
            return
        
        if not as_dump:
            product = products.find_one({'_id': self._id})

            print('ID:',self._id ,type(self._id))

            if not product:
                raise ValueError('Product could not be found')
        else:
            product = kwargs  

        for key, val in product.items():
            setattr(self, key.strip(), val)

        self.process()
        Product.__cached_products[self._id] = self

    def process(self):
        
        if getattr(self,'title', None):
            self.title = self.title.title()

        if getattr(self,'price', None):
            try:
                # TODO: use local for prices instead ?*
                self.price_display = int(self.price)
                dec,_= math.modf(float(self.price))
                self.decimal = f"{dec:0.2f}".split('.')[-1]
            except:
                pass

        if getattr(self,'category', None):
            self.category_display = self.category.replace('-', ' ').title()

    def handle_starred(self):
            starred_rating = math.floor(self.rating * 2) / 2
            whole_stars = int(starred_rating)
            dec,_= math.modf(float(starred_rating))
            half_stars = 0
            if dec != 0:
                half_stars = 1
            
            remaining_stars = 5- (whole_stars + half_stars)
            return whole_stars, half_stars, remaining_stars

    def __eq__(self, other):
        assert isinstance(other, Product)
        return self._id == other._id
    
    def __hash__(self):
        
        return int(str(self._id), 16)
    
    def get(self, attr, default=None):
        return getattr(self, attr, default)    
    @staticmethod
    def dump(product: dict, id_field='_id', merge=False):
        """ dumps a product dictionary to a product instance
            merge: if the dict has other attributes, they will be set to the product
            id_field: defuault ._id from mongo db but allows to change it
        """
        id = product.get(id_field)
        if not id:
            raise TypeError('Cannot dump a product without id')
        product.pop(id_field)
        if merge:
            res_product = Product(id) # this might be unnescceary? ***
            for item, value in product.items():
                if not hasattr(res_product, item):
                    setattr(res_product, item, value)
            return res_product

            
        return Product(id, **product, as_dump=True)


    @classmethod
    def clear_cache(cls):
        cls.__cached_products={}
    def update_stock(product_id, qty):
#         update db, if successful update cache
        
    
        pass
            
       