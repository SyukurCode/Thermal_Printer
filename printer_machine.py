from tabulate import tabulate
from escpos import printer
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
now = datetime.now()
class Print:
	_printerFile = None

	def __init__(self,printerFile):
		self._printerFile = printerFile

	def jobs(self,data):
		_items = ["Items"]
		_qty = ["Qty"]
		_rm = ["RM"]
		_total_rm = 0
		logger.debug(data)
		title = data['title'].replace(" ","\n")
		for item in data["item"]:
			itemTrim = item[1].replace("&amp;","&")
			_items.append(itemTrim)
			_qty.append(item[0])
			_rm.append(item[2])
			_total_rm = _total_rm + (float(item[2]) * float(item[0]))

		return self.printLayout(title,_qty,_items,_rm,_total_rm)

	def printLayout(self,title,_qty,_items,_rm,_total_rm):
		try:
			# setup printer
			p = printer.File(self._printerFile)

			# Load image
			image_path = "/app/static/img/logo.png"
			p.set(align="center", text_type='B')
			p.image(img_source=image_path,impl="bitImageRaster")

			# setup layout header
			p.set(align="center", width=2)
			p.text(title + "\n") # max 12
			p.set(align="center", text_type='B')
			p.text("Date: " + now.strftime("%d-%b-%Y %I:%M:%S %p") + "\n")
			p.set(align="left", text_type='B')
			p.text("*" * 30 + "\n")

			# setup layout body
			table = zip(_qty, _items, _rm)
			p.text(tabulate(table, colalign=("right",),tablefmt="plain"))
			p.text("\n")

			# setup layout footer
			p.set(align="left", text_type='B')
			p.text("-" * 30 + "\n")
			p.set(align="left", width=2)
			table = [["","TOTAL","",round(_total_rm,2)]]
			p.text(tabulate(table ,colalign=("right",),tablefmt="plain"))
			p.text("\n")
			p.set(align="left", text_type='B')
			p.text("-" * 30 + "\n")
			# p.text("\n\n\n")
			p.cut()
			p.close()

			return True

		except Exception as e:
			logger.error(f"Cannot print, error {str(e)}")
			return False
