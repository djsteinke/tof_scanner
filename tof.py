import time
import threading
import VL53L0X as VL53L0X
from logging import getLogger

module_logger = getLogger("main.tof")


class TOF(object):
    def __init__(self):
        self._running = False
        self._ranging = False
        self._range = 0
        self._delay = 15
        self._sensor = None

    def get_range(self):
        if self._running:
            if not self._ranging:
                self._ranging = True
                distance = self._sensor.get_distance()
                module_logger.debug("Range: %0.2f mm" % distance)
                self._range = distance
                self._ranging = False
            timer = threading.Timer(self._delay, self.get_range)
            timer.start()

    def get_status(self):
        if self._running:
            return "running"
        else:
            return "stopped"

    def start(self):
        if not self._running:
            module_logger.debug("start()")
            self._running = True
            self._sensor = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
            self._sensor.open()
            self._sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)
            timer = threading.Timer(1, self.get_range)
            timer.start()

    def stop(self):
        module_logger.debug("stop()")
        self._sensor.stop_ranging()
        self._sensor.close()
        self._running = False

    @property
    def range(self):
        return self._range

    @property
    def running(self):
        return self._running
