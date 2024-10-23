from flask import Flask, request, jsonify
import os
import datetime
import logging
import subprocess

app = Flask(__name__)

# Globale Variablen
PORT = 5050
IMAGE_DIRECTORY = "/home/photobooth/boxcom/images"
ORDER_TIMEOUT = 55

global paperStock
paperStock = 18
global printCount
printCount = 0
global lastPrintOrder
lastPrintOrder = datetime.datetime.fromtimestamp(0)

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)

@app.route('/printer/is_ready', methods=['GET'])
def is_ready():
    logging.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{request.remote_addr}>: GET /printer/is_ready")
    return "Printer is ready", 200

@app.route('/printer/order', methods=['GET'])
def get_last_order():
    return jsonify("{ timestmap: " + str(lastPrintOrder) + " }"), 200

@app.route('/printer/order', methods=['POST'])
def print_order():
    global printCount
    global paperStock
    global lastPrintOrder

    # Image ID aus Anfrage auslesen
    image_id = request.json.get("image_id")

    logging.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{request.remote_addr}>: POST /printer/order")

    if paperStock == 0:
        logging.warn(f"Printing image {image_id} failed due to missing paper")
        return "Paper stock depleted", 503
    if (datetime.datetime.now() - lastPrintOrder).seconds < ORDER_TIMEOUT:
        logging.warn(f"Printing image {image_id} was canceled, because printer is still in timeout")
        return "Printer busy", 429

    image_path = os.path.join(IMAGE_DIRECTORY, f"img{image_id}.jpg")

    logging.info(f"Printing image {image_id}")
    subprocess.run("lp " + image_path)

    printCount += 1
    paperStock -= 1
    lastPrintOrder = datetime.datetime.now()

    return "OK", 200

@app.route('/printer/stock', methods=['GET'])
def get_stock():
    logging.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{request.remote_addr}>: GET /printer/stock")
    return jsonify({"stock": paperStock}), 200

@app.route('/printer/stock', methods=['POST'])
def update_stock():
    global paperStock
    logging.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{request.remote_addr}>: POST /printer/stock")

    stock = request.json.get('stock')
    if stock is None:
        return "Stock cannot be undefined", 400

    paperStock = stock
    logging.info(f"New stock: {paperStock}")
    return "OK", 200

@app.route('/printer/print_count', methods=['GET'])
def get_print_count():
    logging.info(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{request.remote_addr}>: GET /printer/print_count")
    return jsonify({"count": printCount}), 200


def start_server():
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    start_server()
