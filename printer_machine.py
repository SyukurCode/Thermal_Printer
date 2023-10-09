from tabulate import tabulate
from escpos import printer
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
now = datetime.now()
class Print:
	_printerFile = None
	_no = ["no."]
	_items = ["Items"]
	_qty = ["Qty"]
	_rm = ["RM"]
	_total_rm = 0

	def __init__(self,printerFile):
		self._printerFile = printerFile

	def jobs(self,data):
		#logging.debug(data)
		title = data['title'].replace(" ","\n")
		for item in data["item"]:
			self._no.append(item[0] + '.')
			itemTrim = item[1].replace("&amp;","&")
			self._items.append(itemTrim)
			self._qty.append(item[2])
			self._rm.append(item[3])
			self._total_rm = self._total_rm + float(item[3])

		return self.printLayout(title)

	def printLayout(self,title):
		try:
			# setup printer
			p = printer.File(self._printerFile)

			# setup layout header
			p.set(align="center", width=2)
			p.text(title + "\n") # max 12
			p.set(align="center", text_type="B")
			p.text("Date: " + now.strftime("%d-%b-%Y %I:%M:%S %p") + "\n")
			p.set(align="left", text_type="B")
			p.text("*" * 30 + "\n")

			# setup layout body
			table = zip(self._no, self._items, self._qty, self._rm)
			p.text(tabulate(table, colalign=("right",),tablefmt="plain"))
			p.text("\n")

			# setup layout footer
			p.set(align="left", text_type="B")
			p.text("-" * 30 + "\n")
			p.set(align="left", width=2)
			table = [["","TOTAL","","{:.2f}".format(self._total_rm)]]
			p.text(tabulate(table ,colalign=("right",),tablefmt="plain"))
			p.text("\n")
			p.set(align="left", text_type="B")
			p.text("-" * 30 + "\n")
			p.text("\n\n\n")

			return True

		except:
			logging.error("Cannot print")
			return False
