import cv2

from module.device.control import Control
from module.device.screenshot import Screenshot

from module.FGOpy.fgoConst import KEYMAP
from module.FGOpy.fgoDetect import Detect
from module.FGOpy.fgoSchedule import schedule


class ControlPoint(Control):
    def click_point(self, x, y):
        getattr(self, f'click_{self.config.Emulator_ControlMethod.lower()}', self.click_adb)(x, y)


class Device(Screenshot, ControlPoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Detect.screenshot = self.screenshot

    @property
    def avalable(self):
        return True

    def press(self, key):
        self.touch(KEYMAP[key])

    def touch(self, pos):
        super().click_point(*pos)

    def swipe(self, rect):
        super().swipe((rect[0], rect[1]), (rect[2], rect[3]))

    def perform(self, pos, wait):
        [(self.press(i), schedule.sleep(j*.001))for i, j in zip(pos, wait)]

    def screenshot(self):
        super().screenshot()
        return self.image[..., ::-1]
