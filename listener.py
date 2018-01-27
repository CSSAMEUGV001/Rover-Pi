import atexit
import threading
import logging
from socketIO_client import SocketIO, BaseNamespace
from i2c_backend import PyCar

KEY = b'0kXMZqwpoAgRUqOXk2Tjsubd1qndPyGR'
HOST = '192.168.1.87'
PORT = 5000

logging.getLogger('socketIO-client').setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

car = PyCar()


@atexit.register
def neutralize():
    car.control(90, 90)

class RoverNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        BaseNamespace.__init__(self, *args, **kwargs)
        self.timer = threading.Timer(1.0, neutralize)
        self.timer.start()

    def on_connect(self):
        logger.info('connected')

    def on_reconnect(self):
        logger.info('reconnected')

    def on_disconnect(self):
        logger.info('disconnected')
        neutralize()

    def on_control(self, message):
        self.timer.cancel()
        steering = message.get('steering', 90)
        throttle = message.get('throttle', 90)
        car.control(steering, throttle)
        self.timer = threading.Timer(1.0, neutralize)
        self.timer.start()

socketIO = SocketIO(HOST, PORT)
rover_namespace = socketIO.define(RoverNamespace, '/rover')

if __name__ == '__main__':
    socketIO.wait()

