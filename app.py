from flask import Flask, request, redirect, url_for
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)