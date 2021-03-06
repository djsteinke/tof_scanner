from time import sleep
from threading import Timer
import VL53L0X as VL53L0X
from logging import getLogger
import RPi.GPIO as GPIO

module_logger = getLogger("main.tof")
max_disp_cnt = 60


class TOF(object):
    def __init__(self, log=False):
        self._running = False
        self._ranging = False
        self._range = 0
        self._delay = 0.02
        self._sensor = None
        self._cnt = 0
        self._log = log

    def low_pass_filter(self, val):
        a = 0.60
        self._range += (val - self._range) * a

    def get_range(self):
        while self._running:
            restart = False
            if not self._ranging:
                self._cnt += 1
                self._ranging = True
                distance = self._sensor.get_distance()
                if distance > 0:
                    self.low_pass_filter(distance)
                    if self._cnt % 20 == 0 and (self._cnt / 20 < max_disp_cnt or self._log):
                        module_logger.debug("Range: %d mm, %0.1f mm" % (distance, self.range))
                else:
                    restart = True
                self._ranging = False
            if restart:
                self.stop()
                self.start()
            else:
                sleep(self._delay)

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
            Timer(0.1, self.get_range).start()

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
