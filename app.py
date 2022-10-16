from flask import Flask, request, redirect, url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, PasswordField, SubmitField, SelectField)
from wtforms.validators import InputRequired, Length
import os
from flask_pymongo import PyMongo
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("DBKEY")
mongo = PyMongo(app)
app.config['SECRET_KEY'] = SECRET_KEY

states=[]
cars = []
def updateGasDB():
    print("Implement later")

def populateStates():
    for document in mongo.db.State_Gas_Price.find({}):
        states.append(document["name"])

def populateCars():
    test = mongo.db.EV_Data.find().sort("Model", 1)
    for document in test:   
        cars.append(document["Model"])
populateCars()
populateStates()

class CarForm(FlaskForm):
    stateSelect = SelectField("Select State", choices=states, validators=[InputRequired()])
    mpg = IntegerField('Miles per gallon', validators=[InputRequired()])
    mpw = IntegerField("Miles per week", validators=[InputRequired()])
    gasPrice = IntegerField("Gas Price", validators=[InputRequired()])
    carSelect = SelectField("Select Car", choices=cars, validators=[InputRequired()])
    carCost = IntegerField("Car Cost", validators=[InputRequired()])
    elecCost = IntegerField("Electricity Cost", validators=[InputRequired()])
    submit = SubmitField('See Results')

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/car/", methods=['GET', 'POST'])
def car():
    if request.method == 'POST':
        print("HELLO WORLD")
        print(request.form['mpw'])
    return render_template('car.html', form=CarForm())

@app.route("/house/", methods=['GET'])
def house():
    return render_template('house.html')

if __name__ == "__main__":
    app.run(debug=True)

