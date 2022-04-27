import logging
import math
import optparse
import os
from stepper import Stepper
from tof import TOF
from time import strftime


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


v_pins = [14, 15, 18, 23]
r_pins = [24, 25, 8, 7]


def scan():
    points = []
    v_steps = 512 / 2
    for h in range(0, int(height), 2):              # height in mm
        r_steps = 2
        for i in range(0, 512, r_steps):            # steps / rot,
            avg_a = tof.avg
            if len(avg_a) > 0:
                rad = center - (sum(avg_a) / len(avg_a))
                angle = math.radians(360.0 / 512.0 * (i * 1.0))
                points.append([
                    rad * math.sin(angle), rad * math.cos(angle), h
                ])
            r_stepper.step(r_steps, wait=0.010)
        v_stepper.step(v_steps)

    points = ["%0.1f %0.1f %0.1f" % (x, y, z) for x, y, z in points]
    points = str.join("\n", points)

    timestamp = strftime('%Y%m%d_%H%M%S')
    out = open(f'{timestamp}.xyz', "w")
    out.write(points)
    out.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-s", "--scan", action="store", type="bool", default=True, dest="scan",
                      help="")
    parser.add_option("-c", "--center", action="store", type="int", default=0, dest="center",
                      help="")
    parser.add_option("-v", "--height", action="store", type="int", default=100, dest="height",
                      help="")
    args, _ = parser.parse_args()

    scan = args.scan
    center = args.center
    height = args.height

    path = os.path.join(os.getcwd(), "scans")  # create scans dir
    if not os.path.isdir(path):
        os.makedirs(path)

    tof = TOF()
    tof.start()

    if scan:
        v_stepper = Stepper(v_pins)
        r_stepper = Stepper(r_pins)
        scan()
