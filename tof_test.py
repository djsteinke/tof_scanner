import time
import threading
import VL53L0X as VL53L0X
from logging import getLogger

module_logger = getLogger("main.tof")
max_disp_cnt = 120

out = list()


class TOF(object):
    def __init__(self):
        self._running = False
        self._ranging = False
        self._range = 0
        self._range5 = 0.0
        self._range10 = 0.0
        self._range15 = 0.0
        self._range20 = 0.0
        self._range30 = 0.0
        self._delay = 0.075
        self._sensor = None
        self._cnt = 0

    def low_pass_filter(self, val):
        self._range = val
        self._range5 += ((val - self._range5) * 0.05)
        self._range10 += ((val - self._range10) * 0.10)
        self._range15 += ((val - self._range15) * 0.15)
        self._range20 += ((val - self._range20) * 0.20)
        self._range30 += ((val - self._range30) * 0.30)
        out.append([self._range, self._range5, self._range10, self._range15, self._range20, self._range30])

    def get_range(self):
        if self._running:
            restart = False
            if not self._ranging:
                self._cnt += 1
                self._ranging = True
                distance = self._sensor.get_distance()
                if distance > 0:
                    self.low_pass_filter(distance)
                    if self._cnt % 20 == 0 and self._cnt / 20 < max_disp_cnt:
                        print("Range: %d mm, %0.1f  %0.1f  %0.1f  %0.1f  %0.1f" % (int(self.range),
                                                                                   self._range5 - self._range,
                                                                                   self._range10 - self._range,
                                                                                   self._range15 - self._range,
                                                                                   self._range20 - self._range,
                                                                                   self._range30 - self._range))
                    if self._cnt / 20 >= max_disp_cnt:
                        points = ["%d, %0.1f, %0.1f, %0.1f, %0.1f, %0.1f" % (a, b, c, d, e, f) for a, b, c, d, e, f in out]
                        points = str.join("\n", points)
                        out_f = open('tof_test.txt', "w")
                        out_f.write(points)
                        out_f.close()
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


tof = TOF()
tof.start()
