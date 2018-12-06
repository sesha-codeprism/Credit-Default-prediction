#Importing dependencies
import numpy as np
import pandas as pd
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine
from flask import Flask,render_template, jsonify, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
import pickle

#loaded my random forest Model
loaded_model = pickle.load(open('models/RandomForest_model.sav', 'rb'))

app = Flask(__name__)

#create engine or connect to existing engine
engine = create_engine('sqlite:///creditcarddefault.sqlite', echo=True)
Base = automap_base()
session = Session(bind=engine)

#reflection and map table , if there is a table in the database drop it
Base.prepare(engine, reflect=True)
# Base.metadata.create_all(engine)
Base.metadata.drop_all(engine)

#first route to homepage
@app.route('/')
def home():
    return render_template('index.html', prediction=None, probability=None)

#second route does the predictions and creates table
@app.route('/predict', methods=['POST'])
def predict(prediction=None):
    Base.metadata.drop_all(engine)
    class CreditDefault(Base):
        __tablename__ = "credit_default"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key = "True")
        default = Column(Integer)
        prob = Column(Integer)
    Base.prepare(engine, reflect=True)
    Base.metadata.create_all(engine)

##### Inputs from HTML ######
    age = request.form['Age']
    gender = request.form['Gender']
    education = request.form['education']
    marriage = request.form['marriage']
    credit_score = request.form['credit_score']
    creditA = request.form['Credit']
    creditB = request.form['CreditBalance']
    credit_bill = request.form['Credit Bill']
    bill_payment = request.form['Bill Payment']
    print (creditB)
#
#     #These are the features that need to be past in the model from our dataset
#     # prediction = loaded_model.predict([[ LIMIT_BAL_US, SEX , EDUCATION , MARRIAGE, AGE, PAY_SCORE_AVG, BILL_AVG_US, PAY_AMT_AVG_US
#     #                                      PAY_TO_BILL, CREDIT_UTILIZATION]])
#
#     #this is the format how the values in model.predict should look like
#     # prediction = loaded_model.predict([[ 2.17714286e+03, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.20000000e+01,
#     #                                      2.17000000e+00, 1.70386829e+03, 4.67360000e+01, 3.00000000e-02, 1.02596667e+00]])
#
#
    #convert inputs into intergers before placing in random forest model
    new_age = int(age)
    new_sex = int(gender)
    new_education = int(education)
    new_marriage = int(marriage)
    new_credit_score =int(credit_score)
    new_pay_to_bill = int(bill_payment)/int(creditB)
    new_credit_utilization = int(creditB)/int(creditA)


    prediction = loaded_model.predict([[ creditA, new_sex , new_education , new_marriage, new_age,
                                     new_credit_score, credit_bill, bill_payment, new_pay_to_bill, new_credit_utilization]])
    
    probability = loaded_model.predict_proba([[ creditA, new_sex , new_education , new_marriage, 
                                    new_age,new_credit_score, credit_bill, bill_payment, new_pay_to_bill, new_credit_utilization]])

    # variable prediction returns [1] or [0]
    # so we grab the element inside the list and convert it to a integer
    # then insert that integer into default column in credit_default table
    # add and commit
    prediction = int(prediction[0])
    probability = float(probability[0][1])
    # prob = CreditDefault(prob=probability)
    # default = CreditDefault(default=prediction)
    entry = CreditDefault(default=prediction,prob=probability)
    session.add(entry)
    # session.add(default)
    # session.add(prob)

    session.commit()
    # print(probability)
    # print(prediction)

    # Now query the database to retrieve the prediction and render the data into the index2.html
    prediction = engine.execute('SELECT * FROM credit_default LIMIT 5').fetchall()[0][1]
    # probability = engine.execute('SELECT * FROM credit_default LIMIT 5').fetchall()[1][2]
    probability = engine.execute('SELECT * FROM credit_default LIMIT 5').fetchall()[0][2]


    # print(probability)
    # print(prediction)
    return render_template('index.html', prediction=prediction, probability=probability )


if __name__ == '__main__':
	app.run(debug=True)
