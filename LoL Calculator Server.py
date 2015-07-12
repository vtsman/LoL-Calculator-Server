from flask import Flask
from flask import request
import os
import json
import requests

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

api_url = "https://na.api.pvp.net/"

max_calls = 100

app = Flask(__name__)

def call_api(url, args):
    global api_key
    req_url = api_url + url
    send_args = dict(args)
    send_args["api_key"] = api_key
    return requests.get(req_url, params=send_args)

def get_json(response):
    return json.dumps(response.json())

#hacked together request limiter
#change at some point

@app.route('/' , defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    global cached_calls
    global ip_req_count
    split_path = path.split("/")
    addr = str(request.remote_addr)
    if len(split_path) >= 3:
        if split_path[2] == "static-data":
            if not (path in cached_calls.keys()):
                cached_calls[path] = get_json(call_api(path, request.args))
                print("cached call for " + path)
            return cached_calls[path]
    if not (addr in ip_req_count.keys()):
        ip_req_count[addr] = 0
    if ip_req_count[addr] < max_calls:
        ip_req_count[addr] += 1
        return get_json(call_api(path, request.args))
    return "Error: Too many api calls", 401

if __name__ == '__main__':
    global api_key
    global cached_calls
    global ip_req_count
    cached_calls = dict()
    ip_req_count = dict()
    api_key = open(os.path.join(__location__, "api.key")).read()
    print(api_key)
    app.run()
