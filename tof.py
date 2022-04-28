import time
import threading
import VL53L0X as VL53L0X
from logging import getLogger

module_logger = getLogger("main.tof")
max_disp_cnt = 60


class TOF(object):
    def __init__(self):
        self._running = False
        self._ranging = False
        self._range = 0
        self._delay = 0.070
        self._sensor = None
        self._avg = []
        self._cnt = 0

    def low_pass_filter(self, val):
        a = 0.05
        self._range += (self._range - val) * a

    def get_range(self):
        if self._running:
            restart = False
            if not self._ranging:
                self._cnt += 1
                self._ranging = True
                distance = self._sensor.get_distance()
                if distance > 0:
                    self.low_pass_filter(distance)
                    self._avg.append(distance)
                    c = int(4 / self._delay)
                    while len(self._avg) > c:
                        self._avg.pop(0)
                    a = 0.0
                    if len(self._avg) > 0:
                        a = sum(self._avg)/len(self._avg)
                    if self._cnt % 20 == 0 and self._cnt / 20 < max_disp_cnt:
                        module_logger.debug("Range: %d mm, %0.1f mm" % (int(distance), a))
                else:
                    restart = True
                self._ranging = False
            if restart:
                self.stop()
                self.start()
            else:
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
            self._sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
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

    @property
    def avg(self):
        return self._avg
