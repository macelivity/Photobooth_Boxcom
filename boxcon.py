import camera.camera_controller as camera
import printer.printer_controller as printer
from threading import Thread

def start_printer_controller():
    printer.start_server()

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
