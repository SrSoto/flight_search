from requests import get
import requests
import json
from requests.exceptions import RequestException
from contextlib import closing

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def simple_post(url,params):
    """
    Attempts to send a post http request with the params given,
    which is a dictionary of pairs variable_name : value.
    Returns the request response, otherwise None.
    """
    try:
        with closing(requests.post(url,params)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def print_req(req):
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def read_params(path):
    params = {}
    with open(path,'r') as f:
        for line in f:
            if(len(line.split())==1):
                key = line.split()[0]
                val = None
            else:
                (key, val) = line.split()
            params[key] = val
    return params
