from RemoteInput import RemoteInput
import threading
import logging
import gphoto2 as gp


logging.basicConfig(filename="enterprise.log", level=logging.DEBUG)

global schedule_capture
schedule_capture = False


global camera
camera = gp.check_result(gp.gp_camera_new())
gp.check_result(gp.gp_camera_init(camera))

def print_events():
    global camera
    global schedule_capture
    while True:
        if schedule_capture:
            print("Shoot!")
            global camera
            try:
                camera.trigger_capture()
                time
            except Exception as e:
                print(e)
            finally:
                schedule_capture = False
        event_type, event_data = camera.wait_for_event(5000)
        print("Event captured: " + str(event_type) + "; <> " + str(event_data))


event_printer = threading.Thread(target=print_events)
event_printer.start()


print("########################################################################################################################")

def shoot():
    global schedule_capture
    schedule_capture = True

rem = RemoteInput(logging)
rem.connect()
rem.set_action("*", shoot)
rem.start_listen()