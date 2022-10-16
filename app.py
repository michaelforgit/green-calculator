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

def calculateCostOverYears(carPrice, gasPrice, electricPrice, mpw, mpg, kWhMile):
    gasYear = []
    electricYear = []
    gas = (gasPrice/mpg)*(mpw*52)
    electric = (kWhMile*(electricPrice/100))*(mpw*52)
    gasYear.append(gas)
    electricYear.append(electric+carPrice)
    for i in range(1, 26):
        gasYear.append(gasYear[i-1]+gas)
        electricYear.append(electricYear[i-1]+electric)
    return electricYear, gasYear

def calculateCO2OverYears(mpg, mpw, CO2lbmi):
    gasYearCO2 = []
    electricYearCO2 = []
    gas = (mpw*19.6*52)/mpg
    electric = mpw*CO2lbmi*52
    gasYearCO2.append(gas)
    electricYearCO2.append(electric)
    for i in range(1, 26):
        gasYearCO2.append(gasYearCO2[i-1]+gas)
        electricYearCO2.append(electricYearCO2[i-1]+electric)
    return electricYearCO2, gasYearCO2
@app.route("/car/result", methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        print("HELLO WORLD")
        print(request.form['mpw'])
        print(request.form['stateSelect'])
        stateSelect = request.form['stateSelect']
        carSelect = request.form['carSelect']
        carPrice = request.form['carCost']
        mpw = request.form['mpw']
        mpg = request.form['mpg']
        gasPriceSelect = mongo.db.State_Gas_Price.find_one({'name':stateSelect})
        electricPriceSelect = mongo.db.State_Electricity_Price.find_one({'State':stateSelect})
        car = mongo.db.EV_Data.find_one({"Model" : carSelect})
        CO2lbmi = car['CO2lb/mi']
        kWhMile = car['kWh/mi']
        gasPrice = gasPriceSelect['gasoline']
        electricPrice = electricPriceSelect['Cents/kWh']
        electricYear, gasYear = calculateCostOverYears(int(carPrice), float(gasPrice), electricPrice,  int(mpw), int(mpg), kWhMile)
        electricYearCO2, gasYearCO2 = calculateCO2OverYears(int(mpg), int(mpw), float(CO2lbmi))
        return render_template('result.html', electricYear=electricYear, gasYear = gasYear, gasYearCO2 = gasYearCO2, electricYearCO2 = electricYearCO2)
    return render_template('result.html')

@app.route("/car/", methods=['GET', 'POST'])
def car():
    return render_template('car.html', form=CarForm())

@app.route("/house/", methods=['GET'])
def house():
    return render_template('house.html')




if __name__ == "__main__":
    app.run()

