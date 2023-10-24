#!/usr/bin/env python
from escpos import printer
from flask import Flask, render_template, request, redirect, jsonify, url_for
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
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

@app.route('/reprint', methods=["POST"])
def rePrintWrite():
        if request.method == 'POST':
                if not os.path.exists("/dev/usb/lp0"):
                        return jsonify({'status': 500, 'text': 'Printer not available'})

                printdata = request.get_json()
                response = machine.jobs(printdata)

                if response == False:
                        return jsonify({'status': 500, 'text': 'Data unsucces to print'})

                return jsonify({'status': 200, 'text': 'Receipt has been printed'})
@app.route('/save', methods=["POST"])
def save():
	if request.method == 'POST':
		savedata = request.get_json()
		strSaveData = json.dumps(savedata)

		saveDataToDb(strSaveData)
		return jsonify({'status': 200, 'text': 'Data was saved.'})

@app.route('/', methods=["GET"])
def index():
	try:
		jenisPerniagaan = JenisPerniagaan.query.all()
	except Exception as e:
		write("Error: " + e)

	if request.method == 'GET':
		return render_template("index.html",jenisPerniagaan=jenisPerniagaan)

@app.route('/history', methods=["GET"])
def history():
	try:
		allhistory = RawData.query.all()
	except Exception as e:
		allhistory = ""
		writeLogs("Error: " + e)

	if request.method == 'GET':
		return render_template("history.html",allhistory=allhistory)

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
