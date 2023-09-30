"""
@MultiTool / HTTP-Request-Handler
@Version 1.0
@Python 3.10.12
"""
import requests,fake_headers,random

#
PROXIES:dict = {
    'http': "socks5h://127.0.0.1:9050",
    'https': "socks5h://127.0.0.1:9050",
    'socks5': "socks5h://127.0.0.1:9050"
}
#


def create_new_session(use_proxy:bool=True,fake_header:bool=True) -> object:
    session = requests.Session()
    if use_proxy:
        session.proxies = PROXIES
    if fake_header:
        session.headers = fake_headers.Headers(browser=random.choice(["firefox","chrome"]),os="mac", headers=True).generate()
    return session

def get(session:requests.Session,url:str) -> tuple((bool,object,int)): 
    # return -> (status,response,response-code)
    try:
        resp = session.get(url)
        return (True,resp,resp.status_code)
    except Exception as _error:
        return (False,str(_error),000)
    
def post(session:requests.Session,url:str,payload:dict) -> tuple((bool,object)):
    # return -> (status,response or str(error))
    try:
        resp = session.post(url,data=payload)
        return (True,resp)
    except Exception as _error:
        return (False,str(_error))