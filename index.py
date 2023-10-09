#!/usr/bin/env python
from escpos import printer
from flask import Flask, render_template, request, redirect, jsonify
import os
from datetime import datetime
import json
from models import db,RawData,JenisPerniagaan
import config
from flask_migrate import Migrate
import logging
import printer_machine

migrate = Migrate()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.app_context().push()
db.init_app(app)
migrate.init_app(app, db)
db.create_all()

machine = printer_machine.Print("/dev/usb/lp0")

@app.route('/print', methods=["POST"])
def printWrite():
	if request.method == 'POST':
		if not os.path.exists("/dev/usb/lp0"):
                        return jsonify({'status': 500, 'text': 'Printer not available'})

		printdata = request.get_json()
		strPrintData = json.dumps(printdata)
		response = machine.jobs(printdata)

		if response == False:
			return jsonify({'status': 500, 'text': 'Data unsucces to print'})

		saveDataToDb(strPrintData)
		return jsonify({'status': 200, 'text': 'Receipt has been printed'})

@app.route('/', methods=["GET","POST"])
def index():
	try:
		allhistory = RawData.query.all()
		jenisPerniagaan = JenisPerniagaan.query.all()
	except Exception as e:
		allhistory =  ""

	if request.method == 'GET':
		return render_template("index.html",allhistory=allhistory,printData="",jenisPerniagaan=jenisPerniagaan)
	if request.method == 'POST':
		if request.form:
			historyID = request.form.get('id')
			try:
				Data = RawData.query.filter_by(id=historyID).first()
			except Exception as e:
				Data = RawData(id=0,tarikh="",data="")

			printData = Data.data
			print(printData)
			return render_template("home.html",allhistory=allhistory,printData=printData)

def saveDataToDb(text):
	if not text == "":
		now = datetime.now()
		today = now.strftime("%d-%b-%Y %I:%M:%S %p")
		try:
			newData = RawData(tarikh=today,data=text)
			db.session.add(newData)
			db.session.commit()
			writeLogs(today + ":Data saved\n")
		except Exception as e:
			writeLogs(today + ":Db not found\n")

def writeLogs(text):
	file = open("app.log", "a")  # append mode
	file.write(text)
	file.close()

# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
	app.run(host='0.0.0.0', port=5000, debug=True)
