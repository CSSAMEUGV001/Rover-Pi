import atexit
import pisocket
import json
import threading
from i2c_backend import PyCar

car = PyCar()

@atexit.register
def neutralize():
    car.control(90, 90)

def run():
    client = pisocket.SocketCommunicator.client()

    timer = threading.Timer(1.0, neutralize)
    while True:
        timer.cancel()
        timer = threading.Timer(1.0, neutralize)
        timer.start()
        message = client.read_to_nul()
        timer.cancel()
        controls = json.loads(message.decode())
        steering = int(controls.get('steering', 90))
        throttle = int(controls.get('throttle', 90))
        car.control(steering, throttle)

if __name__ == '__main__':
    import traceback
    import time
    while True:
        try:
            run()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            time.sleep(1)

