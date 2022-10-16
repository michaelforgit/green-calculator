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

tiles = ["0-1000", "1000-1500", "1500-2000","2000-2500", "2500-3000", "3000+"]
costTiles = [4400, 6693, 9371, 12048, 14726, 17850]
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


class HouseForm(FlaskForm):
    squareFT = SelectField("Select Square Footage", choices=tiles, validators=[InputRequired()])
    stateSelect = SelectField("Select State", choices=states, validators=[InputRequired()])
    submit = SubmitField('See Results')



@app.route('/')
def index():
    return render_template('index.html')

def calculateSolarCost(taxBreak, kWhMonth, electricityPrice, initialCostTiles):
    withoutSolar = []
    withSolar = []
    electricityPrice=float(electricityPrice)/100
    woSolari = kWhMonth * electricityPrice * 12
    wSolari = ((((kWhMonth-750)*electricityPrice)*12)+((initialCostTiles)*(1-(taxBreak/100))))
    withoutSolar.append(woSolari)
    withSolar.append(wSolari)
    for i in range(1, 26):
        withSolar.append(withSolar[i-1]+(((kWhMonth-750)*electricityPrice)*12))
        withoutSolar.append(withoutSolar[i-1]+woSolari)
    print(withoutSolar)
    return withSolar, withoutSolar



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
        stateSelect = request.form['stateSelect']
        carSelect = request.form['carSelect']
        carPrice = request.form['carCost']
        mpw = request.form['mpw']
        mpg = request.form['mpg']
        gasPriceSelect = mongo.db.State_Gas_Price.find_one({'name':stateSelect})
        if (stateSelect != "Minnesota" and stateSelect != "Iowa"):
            stateSelect = "Iowa"
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

@app.route("/house/", methods=['GET', 'POST'])
def house():
    return render_template('house.html', form=HouseForm())

@app.route('/house/result', methods=['GET', 'POST'])
def result2():
    if request.method == 'POST':
        tileDict = {"0-1000":4400, "1000-1500":6693, "1500-2000":9371,"2000-2500":12048, "2500-3000":14726, "3000+":17850}

        stateSelect = request.form['stateSelect']
        squareFT = request.form['squareFT']
        solarState = mongo.db.Solar_House.find_one({'State':"Iowa"})
        taxBreak = solarState['TaxBreak']
        kWh = solarState['kWh']
        electricityPrice = solarState['ElectricityPrice']
        initialCostTiles = tileDict[squareFT]
        withSolar, withoutSolar = calculateSolarCost(taxBreak, kWh, electricityPrice, initialCostTiles)
        return render_template('result2.html', withSolar=withSolar, withoutSolar=withoutSolar)
    return render_template('result2.html')

@app.route("/about/", methods=['GET'])
def about():
    return render_template('about.html')

@app.route("/aboutUs/", methods=['GET'])
def aboutUs():
    return render_template('about-us.html')




if __name__ == "__main__":
    app.run()

