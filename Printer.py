#!/usr/bin/env python
from escpos import printer
from flask import Flask, render_template, request, redirect
import os
from datetime import datetime
import json
from models import db,RawData
import config
from flask_migrate import Migrate

migrate = Migrate()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db.init_app(app)
migrate.init_app(app, db)
db.create_all()

@app.route('/print', methods=["POST"])
def printWrite():
	if request.method == 'POST':
		if request.form:
			printdata = request.form.get("printText")
			p = printer.File("/dev/usb/lp0")
			p.set(align="center", width=2)
			p.text("Pesanan Donut\n")
			p.set(align="center", text_type="B")
			p.text(printdata);
			p.text("\n================\n")
			p.text("\n\n\n")
			saveDataToDb(printdata)

			return redirect("/")

@app.route('/', methods=["GET","POST"])
def index():
	try:
		allhistory = RawData.query.all()
	except Exception as e:
		allhistory =  ""

	if request.method == 'GET':
		return render_template("home.html",allhistory=allhistory,printData="")
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
	app.run(host='0.0.0.0', port =5000)
