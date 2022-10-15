from flask import Flask, request, redirect, url_for
from flask import render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'