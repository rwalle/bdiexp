#!/usr/bin/env python3

from basler import BaslerCamera
from relay_switch import RelaySwitch
from superlum import Superlum
from apt.motor import Motor
from enum import Enum
import json, time

import logging
logger = logging.getLogger(__name__)


class BaslerPIA160035GM(BaslerCamera):

    _PIXEL_FORMAT = "Mono12Packed"
    _EXPOSURE_TIME_ABS = 20 * 1000
    _PACKET_SIZE = 9000
    _MAX_PIXEL_VALUE = 4095

    def set_default_params(self):

        cam = self.get_camera()

        cam.GevSCPSPacketSize.SetValue(self._PACKET_SIZE)
        cam.ExposureTimeAbs.SetValue(self._EXPOSURE_TIME_ABS)
        cam.PixelFormat.SetValue(self._PIXEL_FORMAT)

    def set_framerate(self, fps):
        cam = self.get_camera()
        cam.AcquisitionFrameRateAbs.SetValue(fps)


class BDMMotor(Motor):

    def move_p003(self):
        self.move_relative(0.03)

    def move_n003(self):
        self.move_relative(-0.03)

    def move_p01(self):
        self.move_relative(0.1)

    def move_n01(self):
        self.move_relative(-0.1)


class BDM:

    _IP_CAM = 'IP_CAM'
    _FP_CAM = 'FP_CAM'
    _OFFSET_X = 'OFFSET_X'
    _OFFSET_Y = 'OFFSET_Y'
    _WIDTH = 'WIDTH'
    _HEIGHT = 'HEIGHT'
    _SIZE_X = 'SIZE_X'
    _SIZE_Y = 'SIZE_Y'
    _CONFIG_FILE = 'bdm_unified_settings.json'

    def __init__(self, mc_widget):

        self.IP_CAM_SN = '20717903'
        self.FP_CAM_SN = '21939024'
        self.RELAY_ADDR = 'COM3'
        self.SUPERLUM_ADDR = 'COM4'
        self.MC_SN = '80864431'

        self.image_camera = BaslerPIA160035GM(serial_number=self.IP_CAM_SN)
        self.fourier_camera = BaslerPIA160035GM(serial_number=self.FP_CAM_SN)

        self.relay = RelaySwitch(self.RELAY_ADDR)
        self.superlum = Superlum(self.SUPERLUM_ADDR)
        self.mc = BDMMotor(self.MC_SN)
        self.mc.set_activex_ctrl(mc_widget)

    def enable(self):

        logger.info("enable all instruments")

        self.connect_cameras()
        self.connect_lamp()
        self.connect_mc()
        self.connect_superlum()

    def disable(self):

        logger.info("disable all instruments")

        self.turn_off_lamp()
        self.set_superlum_off()

        self.disconnect_cameras()
        self.disconnect_lamp()
        self.disconnect_mc()
        self.disconnect_superlum()

    # camera

    def connect_cameras(self):

        with open(self._CONFIG_FILE, 'r') as json_file:
            bdm_params = json.load(json_file)

        aoi_params = bdm_params['AOI']
       

        ip_cam_aoi = aoi_params[self._IP_CAM]
        fp_cam_aoi = aoi_params[self._FP_CAM]

        self.image_camera.open()
        self.image_camera.set_default_params()
        self.image_camera.set_aoi(ip_cam_aoi[self._OFFSET_X], ip_cam_aoi[self._OFFSET_Y], 
            ip_cam_aoi[self._WIDTH], ip_cam_aoi[self._HEIGHT])

        self.fourier_camera.open()
        self.fourier_camera.set_default_params()
        self.fourier_camera.set_aoi(fp_cam_aoi[self._OFFSET_X], fp_cam_aoi[self._OFFSET_Y], 
            fp_cam_aoi[self._WIDTH], fp_cam_aoi[self._HEIGHT])

    def disconnect_cameras(self):
        self.image_camera.close()
        self.fourier_camera.close()

    # lamp

    def connect_lamp(self):
        self.relay.init()

    def disconnect_lamp(self):
        self.relay.close()

    def turn_on_lamp(self):
        self.relay.turn_on()

    def turn_off_lamp(self):
        self.relay.turn_off()

    # motion controller

    def connect_mc(self):
        self.mc.create()
        self.mc.enable()

    def disconnect_mc(self):
        self.mc.disable()

    # Superlum

    def connect_superlum(self):
        self.superlum.connect()

    def get_superlum_status(self):
        (_, status, _) = self.superlum.get_current_status()
        return (status[1], status[4]) # ON, HI
    
    def switch_superlum_power(self):
        self.superlum.switch_power()

    def switch_superlum_hi(self):
        self.superlum.switch_hi_mode()

    def set_superlum_on(self):
        self.superlum.set_power_on()
    
    def set_superlum_off(self):
        (_, status, _) = self.superlum.get_current_status()
        if status[1]:
            self.switch_superlum_power()

    def disconnect_superlum(self):
        self.superlum.close()