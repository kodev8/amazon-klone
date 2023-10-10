from flask import url_for, Response, request, redirect
import requests
from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType
from config import LOCATION_API

def htmx_redirect(endpoint):
    response = Response()
    response.headers["HX-Redirect"] = endpoint
    response.status_code = 200

    return response

def htmx_request(view_func): 
    def wrapper_func(*args, **kwargs): 
        if 'hx-request' in request.headers: 
            return view_func(*args, **kwargs) 
        else: 
            return redirect(url_for('index')) 

    # renames wrapper for unique name to avoid: AssertionError: View function mapping is overwriting an existing endpoint function: wrapper_func
    wrapper_func.__name__ = view_func.__name__
    return wrapper_func

def get_location(ip):
    try:
        # expected error if .json() does not work
        response = requests.get(f'{LOCATION_API}{ip}/jsony/').json()
        location_data = {
            "ip": ip,
            "city": response.get("city"),
            "region": response.get("region"),
            "country": response.get("country_name")
        }
    except:
        # log that default data was used
        print('defualt data used ')
        location_data= {
            'ip': None,
            'city':'Paris',
            'region':'ILE-DE-FRANCE',
            'country':'France'
        }
    
    return location_data
