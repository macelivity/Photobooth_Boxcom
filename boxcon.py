import camera.camera_controller as ctrl
import subprocess
from threading import Thread

def start_printer_controller():
    subprocess.run("node printer/printer_controller.js")

def start_camera_controller():
    ctrl.startup()

def start_admin_web():
    return


if __name__ == "__main__":
    camera = Thread(target = start_camera_controller)
    camera.start()

    printer = Thread(target = start_printer_controller)
    printer.start()

    web_admin = Thread(target = start_admin_web)
    web_admin.start()
