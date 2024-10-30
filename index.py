from flask import Flask, render_template, request, redirect, jsonify, send_from_directory, url_for
import os
from datetime import datetime
import json
from models import db,RawData,JenisPerniagaan
import config
from flask_migrate import Migrate
import logging
import printer_machine
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
			logger.error("printer not available at /dev/usb/lp0")
			return jsonify({'status': 500, 'text': 'Printer not available'}),500

		printdata = request.get_json()
		strPrintData = json.dumps(printdata)
		response = machine.jobs(printdata)

		if response == False:
			logger.error("printer fail to print")
			return jsonify({'status': 500, 'text': 'Data unsucces to print'}),400

		saveDataToDb(strPrintData)
		logger.info("Receipt succesfully printed")
		return jsonify({'status': 200, 'text': 'Receipt has been printed'}),200

@app.route('/reprint', methods=["POST"])
def rePrintWrite():
	if request.method == 'POST':
		if not os.path.exists("/dev/usb/lp0"):
			logger.error("printer not available at /dev/usb/lp0")
			return jsonify({'status': 500, 'text': 'Printer not available'}),500
		printdata = request.get_json()
		response = machine.jobs(printdata)

		if response == False:
			logger.error("printer fail to print")
			return jsonify({'status': 500, 'text': 'Data unsucces to print'}),500

		logger.info("Receipt succesfully re-printed")
		return jsonify({'status': 200, 'text': 'Receipt has been printed'}),200
@app.route('/save', methods=["POST"])
def save():
	if request.method == 'POST':
		savedata = request.get_json()
		strSaveData = json.dumps(savedata)

		isOk = saveDataToDb(strSaveData)
		if not isOk:
			return jsonify({'status': 500, 'text': 'Data was not saved.'}),500
		logger.info("Receipt succesfully saved to database")
		return jsonify({'status': 200, 'text': 'Data was saved.'}),201

@app.route('/', methods=["GET"])
def index():
	try:
		jenisPerniagaan = JenisPerniagaan.query.all()
	except Exception as e:
		logger.error("fail to get data " + e)

	if request.method == 'GET':
		return render_template("index.html",jenisPerniagaan=jenisPerniagaan)

@app.route('/history', methods=["GET"])
def history():
	try:
		allhistory = RawData.query.all()
	except Exception as e:
		allhistory = ""
		logger.error("fail to get data " + e)

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
			logger.info(today + ":Data saved\n")
			return True
		except Exception as e:
			logger.error(today + ":Db not found\n")
	return False

# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
	from waitress import serve # type: ignore
	serve(app, host="0.0.0.0", port=5000)
	#app.run(host='0.0.0.0', port=5000, debug=False)
