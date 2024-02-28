from bson import ObjectId
from config import products, categories, logging
import requests
import math
import random
from datetime import datetime

class Product:

    _cached_products = {}
    TAX = random.uniform(0.06, 0.15)
    SHIPPING = 0.05
    
    def __new__(cls, product_id, as_dump=False, **kwargs):
        
        
        if not as_dump:

            # check if product is a string or ObjectId and search the db for it
            product_type = type(product_id)

            if product_type not in (ObjectId, str):
                raise TypeError(f'Product must be objectID or Sting not {product_type}')
            
            # raises error if cannot convert to object id
            if product_type == str:
                product_id = ObjectId(product_id)
        

        cached = cls._cached_products.get(product_id)
        if cached:
            
            # return cached producr data instead of creating a new instance/look up in db
            return cached
        
        # set the id as an ObjectID to the instance which will then be used in initialization
        product_instance = super().__new__(cls)
        product_instance._id = product_id

        return product_instance

    def __init__(self,  product_id, as_dump=False, **kwargs):
        
        # do not initialize if is in cache as the product should already be returned    
        if self._id in Product._cached_products:
            return
        
        # if not in cache, initialize the product
        if not as_dump:
            product = products.find_one({'_id': self._id})
    

            if not product:
                raise ValueError('Product could not be found')
        else:
    

            product = kwargs  

        for key, val in product.items():
            setattr(self, key.strip(), val)

        # process the product data
        self.process()

        # add to cache
        Product._cached_products[self._id] = self

    def process(self):
        
        if getattr(self,'title', None):
            self.title = self.title.title()

        if getattr(self,'price', None):
            try:
                self.price_display = int(self.price)
                dec,_= math.modf(float(self.price))

                self.decimal = f"{dec:0.2f}".split('.')[-1]

            except Exception as e:
                logging.info("ERROR in Product.py: price is not a number", e)


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
        try:
            assert isinstance(other, Product)
            return self._id == other._id
        except AssertionError as e:
            logging.info("Testing Prdouct equality incorrectly", e)

    # hash func to store in product cache
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
        
        # remove id from product
        product.pop(id_field)

        # merge the product with the instance
        if merge:
            res_product = Product(id)

            for item, value in product.items():
                setattr(res_product, item, value)
            return res_product

            
        return Product(id, **product, as_dump=True)

    # clear product cache for testing
    @classmethod
    def clear_cache(cls):
        cls.__cached_products={}

    def update_stock(product_id, qty):
#         update db, if successful update cache
        pass

    # run once to set up
    @staticmethod
    def setup(fresh=False):

        if fresh:
            products.drop()
            categories.drop()

        request = requests.get('https://dummyjson.com/products?limit=100')
        api_products = request.json().get('products')
        setup_categories = set()


        if api_products:
            adding = False
            for product in api_products:
                if not products.find_one({'id': product['id']}):
                    adding = True
                    products.insert_one(product)
                    setup_categories.add(product['category'])

            if not adding:
                print('No new products found')
            print('Done')

        else:
            print('No products found')

        

        category_images = {
            'automotive': "https://imagetin.micksgarage.com/images/micksgarage-ie/bbd29567-d/8_2c4448.jpg?size=1x",  
            'fragrances':"https://static01.nyt.com/images/2018/12/20/t-magazine/fashion/20tmag-fragrance/20tmag-fragrance-superJumbo.jpg",
            'home-decoration':"https://images.summitmedia-digital.com/spotph/images/2021/01/21/moon-lamp-1611201965.jpg",
            'furniture': "https://www.ikea.com/global/assets/range-categorisation/images/dining-sets-up-to-2-seats-36209.jpeg?imwidth=400", 
            'groceries': "/static/assets/groceries.jpg",
            'laptops':"https://images.summitmedia-digital.com/spotph/images/2021/10/07/pink-laptops-640-1633601136.jpg",
            "lighting":"https://www.ul.com/sites/g/files/qbfpbp251/files/styles/hero_boxed_width/public/2021-01/iStock-1082558358_lighting-ULcom-1200x900.jpg?itok=IykzAv0X",
            "mens-shirts":"https://cdn.thewirecutter.com/wp-content/media/2022/01/buttonupshirts-2048px-DSCF0788.jpg?auto=webp&quality=100&width=1024", 
            'mens-watches': "https://hips.hearstapps.com/amv-prod-gp.s3.amazonaws.com/gearpatrol/wp-content/uploads/2019/06/50-Best-Watches-For-Men-Gear-Patrol-lead-full.jpg",
            'mens-shoes':"https://www.themodestman.com/wp-content/uploads/2019/07/Mens-shoe-collection.jpg",
            'motorcycle':"https://motofomo.com/wp-content/uploads/2020/12/best-looking-motorcycles-hypersport-se-1024x712.jpg",
            'skincare':"https://i.redd.it/jtvb3c742y941.jpg",
            'sunglasses':"https://cdn.thewirecutter.com/wp-content/media/2021/07/cheapsunglaasses-2048px-6956.jpg?auto=webp&quality=75&crop=2:1&width=1024",
            'tops':"https://img.freepik.com/premium-photo/women-s-aesthetic-minimal-fashion-pastel-clothes-made-washed-linen-stylish-female-blouses-dresses-pants-shirts-hanger-white-background-fashion-blog-website-social-media_408798-9507.jpg?w=360",
            'womens-bags':"https://cdn.thewirecutter.com/wp-content/uploads/2020/03/totebags-lowres-3945.jpg?auto=webp&quality=100&crop=3:2&width=1024",
            'womens-shoes':"https://img.freepik.com/premium-photo/variety-women-s-fashion-comfortable-shoes-all-seasons-light-background-top-view_624178-2267.jpg",
            'womens-watches':"https://www.swisswatchexpo.com/TheWatchClub/wp-content/uploads/2023/05/Cartier-Tortue-Ladies-Watches-Best-Cartier-Watches-for-Ladies.jpg",
            "womens-dresses":"https://www.travelandleisure.com/thmb/CeYNyY08_wXYFyQzfvc2bbatMLk=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/amazon-prairie-dresses-tout-AMZF-DRESS0422-f9db386252f64974bc0ce0b5e868ebd3.jpg",
            'womens-jewellery':"https://images.squarespace-cdn.com/content/v1/547a3834e4b053a861c4874e/a68f8af6-2f86-4b54-92db-3e4bd388d8ab/Sustainably+Chic+%7C+Sustainable+Fashion+Blog+%7C+Best+Sustainable+Ethical+Jewelry+Brands.jpeg",
            'smartphones':"https://m-cdn.phonearena.com/images/article/64576-wide-two_1200/The-Best-Phones-to-buy-in-2023---our-top-10-list.jpg",
            'skincare':"https://i.redd.it/jtvb3c742y941.jpg",
                        

        }
        if len(setup_categories) > 0:
            setup_categories = sorted(list(setup_categories))
            for category in setup_categories:
                category_title = category.replace('-', ' ').title()
                if not categories.find_one({'key': category}):
                    categories.insert_one({'title': category_title, 'key': category, 'image': category_images.get(category, '')})
            
        logging.info(f"{__name__} setup complete @ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
       