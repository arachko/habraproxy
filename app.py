from flask import Flask, request
from flasklib import delegate_app

app = Flask(__name__)

app.debug = True


@app.route('/', methods=['GET'])
@app.route('/<uri>/', methods=['GET'])
@app.route('/<uri>/<uri2>/', methods=['GET'])
@app.route('/<uri>/<uri2>/<uri3>/', methods=['GET'])
@app.route('/<uri>/<uri2>/<uri3>/<uri4>/', methods=['GET'])
@app.route('/<uri>/<uri2>/<uri3>/<uri4>/<uri5>/', methods=['GET'])
@app.route('/<uri>/<uri2>/<uri3>/<uri4>/<uri5>/<uri6>/', methods=['GET'])
def habr(uri=None, uri2=None, uri3=None, uri4=None, uri5=None, uri6=None):
    return delegate_app.habr(request, [uri, uri2, uri3, uri4, uri5, uri6])
