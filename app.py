#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

# https://maps.googleapis.com/maps/api/place/nearbysearch/json?
#location=-34.5988222,-58.4104831&radius=1000&type=restaurant&keyword=cruise&key=AIzaSyCZ8V7Jb7KwHGXMwNRb27U3Lf_nk5Wpc0c



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "showRestoForLocation":
        return {}
    baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    req_query = makeYqlQuery(req)

    print("req_query 1")
    print(req_query)
    if req_query is None:
        return {}
    req_query_final = baseurl + req_query
    print("req_query_final")
    print(req_query_final)
    result = urlopen(req_query_final).read()
    data = json.loads(result)
    print(data)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    location = parameters.get("location")
    radius = "100"
    apiKey = "AIzaSyCZ8V7Jb7KwHGXMwNRb27U3Lf_nk5Wpc0c"
    forType = "restaurant"
    url = "location=" + location + "&radius=" + radius + "&type=" + forType + "&key=" + apiKey
    return url


def makeWebhookResult(data):
    print("makeWebhookResult")

    result = data.get('results')

    item = result[0]

    speech = "Near by resto name is " + item.get('name')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-resto-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
