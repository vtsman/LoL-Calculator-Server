from flask import Flask
from flask import request
import os
import json
import requests
from crossdomain import crossdomain
import time
import thread
import logging

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
    global calls
    split_path = path.split("/")
    addr = str(request.remote_addr)
    if len(split_path) >= 3:
        if split_path[2] == "static-data":
            if not (request.url in cached_calls.keys()):
                cached_calls[request.url] = get_json(call_api(path, request.args))
                logger.info("cached call for " + request.url)
            return cached_calls[request.url]
    if calls > 2000:
        return "Error: Too many api calls", 401
    calls += 1
    print(calls)
    return get_json(call_api(path, request.args))


def reset_cache(tName):
    global cached_calls
    while True:
        time.sleep(86400)
        cached_calls = []
        logger.info("flushed cache")


def reset_call_count(tName):
    global calls
    while True:
        time.sleep(1)
        calls = 0


if __name__ == '__main__':
    global api_key
    global cached_calls
    global calls
    global logger

    logger = logging.getLogger('riot_api_server')
    logger.setLevel(logging.INFO)
    hdlr = logging.FileHandler('/var/tmp/riot.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    cached_calls = dict()
    calls = 0
    api_key = open(os.path.join(__location__, "api.key")).read()
    print(api_key)

    thread.start_new_thread(reset_cache, ("Cache reset", ))
    thread.start_new_thread(reset_call_count, ("Call count reset", ))

    app.run(host='0.0.0.0', port=1081)
