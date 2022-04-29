from RpiMotorLib.RpiMotorLib import BYJMotor
from threading import Timer


def wait_from_rpm(rpm):
    return 60.0 / (rpm * 1.0) / 4.0 / 512.0


class Stepper(object):
    def __init__(self, pins=None):
        if pins is None:
            pins = [14, 15, 18, 23]
        self._pins = pins
        self._motor = BYJMotor()
        self._steps = 0
        self._step = 0
        self._running = False
        self._ccwise = False
        self._wait = 0.005

    def start_step(self, steps, wait=0.005, ccwise=False, rpm=None):
        self._steps = steps
        self._running = True
        self._ccwise = ccwise
        if rpm is not None:
            self._wait = wait_from_rpm(rpm)
        self._wait = wait if wait >= 0.005 else 0.005
        Timer(0.001, self.run).start()

    def run(self):
        while self._running:
            self._motor.motor_run(self._pins, steps=1, ccwise=self._ccwise, steptype="full", wait=self._wait)
            self._step += 1

    def stop(self):
        self._running = False

    @property
    def step(self):
        return self._step

    @property
    def steps(self):
        return self._steps
