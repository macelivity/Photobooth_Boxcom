from flask import Flask, request, jsonify, send_file, make_response, redirect
from datetime import datetime, timedelta, UTC
import logging
import os
import sys

import ImageLoader

PORT = 8765

logging.basicConfig(filename="printer.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

IMAGE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))

app = Flask(__name__)

@app.before_request
def check_source():
    if request.host_url != "https://fotobox.fbg-bremen.de/"
        abort(401)


@app.route("/printer/order", strict_slashes=False, methods=['POST'])
def print_image(image_id):
    return


@app.route("/printer/ready", strict_slashes=False, methods=['GET'])
def printer_is_ready(image_id):
    return


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
