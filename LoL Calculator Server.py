from flask import Flask
from flask import request
import os
import json
import requests
from crossdomain import crossdomain
import time
import thread

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
@crossdomain(origin='*')
def catch_all(path):
    global cached_calls
    global ip_req_count
    split_path = path.split("/")
    addr = str(request.remote_addr)
    if len(split_path) >= 3:
        if split_path[2] == "static-data":
            if not (request.url in cached_calls.keys()):
                cached_calls[request.url] = get_json(call_api(path, request.args))
                print("cached call for " + request.url)
            return cached_calls[request.url]
    if not (addr in ip_req_count.keys()):
        ip_req_count[addr] = 0
    if ip_req_count[addr] < max_calls:
        ip_req_count[addr] += 1
        return get_json(call_api(path, request.args))
    return "Error: Too many api calls", 401


def reset_cache(tName):
    global cached_calls
    global ip_req_count
    while True:
        time.sleep(86400)
        cached_calls = []
        ip_req_count = []
        print("flushed cache")


if __name__ == '__main__':
    global api_key
    global cached_calls
    global ip_req_count
    cached_calls = dict()
    ip_req_count = dict()
    api_key = open(os.path.join(__location__, "api.key")).read()
    print(api_key)

    thread.start_new_thread(reset_cache, ("Cache reset", ))

    app.run(host='0.0.0.0', port=1081)
