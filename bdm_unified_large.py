# -*- coding: utf-8 -*-
# !/bin/python3

import sys, json, os, subprocess, datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from libtiff import TIFF
import logging
logger = logging.getLogger(__name__)

from PyQt5 import QtCore, QtWidgets, QAxContainer
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication, QTableWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QTimer, QDir, QObject, QEvent
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QAxContainer import QAxWidget

from bdm_unified_large_form import Ui_BDMUnifiedFormLarge
from set_ui_status import set_ui_status
from bdi_system import BDM
from experiment_plan import BDMSingleLoop
from dispatcher import ExpDispatcher


class UnifiedBDIWindow(QWidget):
    """ preview windows """

    _PLOT_FP_IMAGES = ['hologram', 'fft', 'cropped']
    _PLOT_SETTINGS = {
        'microscopy': {'cmap': 'gray', 'vmin': 0, 'vmax': 4095},
        'hologram': {'cmap': 'gray', 'vmin': 0, 'vmax': 4095},
        'fft': {'cmap': 'jet', 'vmin': 9, 'vmax': 11.8},
        'cropped': {'cmap': 'jet', 'vmin': 8.8, 'vmax': 11.7},

    }
    REFRESH_INTERVAL = 100  # miliseconds
    _CONFIG_FILE = 'bdm_unified_settings.json'
    _FONT_SIZE = 18
    _PATH_TO_NIRCMD = r'nircmdc.exe'
    _DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    _SAVE_SHIFT_BIT = 4  # BE CAREFUL!

    def __init__(self):
        QWidget.__init__(self)

        self.ui = Ui_BDMUnifiedFormLarge()

        self.ui.setupUi(self)

        self.exp_system = BDM(self.ui.mcAxWidget)

        self.aoi_params = self.get_fp_crop_params()

        self.last_frame = None

        with open(self._CONFIG_FILE, 'r') as json_file:
            bdm_params = json.load(json_file)

        self.save_root = bdm_params['CAPTURE_SETTINGS']['SAVE_DIR']

    def set_ui_enabled(self):
        if self.ui.rdBtnIP.isChecked():
            set_ui_status(self.ui, 'enabledIP')
        else:
            set_ui_status(self.ui, 'enabledFP')

    def show_errMsgBox(self, txt):
        msgBox = QMessageBox()
        msgBox.setText(txt)
        msgBox.setIcon(QMessageBox.Icon.Critical)

        msgBox.exec()

    def status_on_off(self, uicomponent, status):
        txt = 'ON' if status else 'OFF'
        font_color = 'green' if status else 'red'

        uicomponent.setText(txt)
        uicomponent.setStyleSheet("color: %s; font-size: %d;" % (font_color, self._FONT_SIZE))

        logger.info("turn monitor %s" + txt)

    def get_current_formatted_time(self):
        return datetime.datetime.now().strftime(self._DATETIME_FORMAT)

    @Slot()
    def on_btnEnableAll_clicked(self):
        try:
            logger.info("enable all")

            self.exp_system.enable()
            self.set_ui_enabled()

            self.exp_system.turn_off_lamp()
            self.exp_system.set_superlum_off()

        except Exception as e:
            logger.exception('enable all failed')
            self.show_errMsgBox(str(e))
            raise

    @Slot()
    def on_btnDisableAll_clicked(self):
        logger.info('disable all')

        self.exp_system.disable()
        set_ui_status(self.ui, 'disabled')


    @Slot(bool)
    def on_rdBtnIP_toggled(self, checked):

        if checked:
            # if self.ui.rdBtnIP.isChecked():
            set_ui_status(self.ui, 'enabledIP')

    @Slot(bool)
    def on_rdBtnFP_toggled(self, checked):
        if checked:
            # if self.ui.rdBtnFP.isChecked():
            set_ui_status(self.ui, 'enabledFP')

    @Slot()
    def on_btnStrt_clicked(self):
        # start preview

        logger.info("start previews")

        if self.ui.rdBtnIP.isChecked():  # imaging plane

            self.exp_system.turn_on_lamp()
            self.exp_system.set_superlum_off()

            self.ui.plotArea.figure.clear()
            self.imshow_axes = [None]
            self.imshow_plots = [None]

            self.timer = self.ui.plotArea.new_timer(self.REFRESH_INTERVAL, [(self.ip_image_grab, (), {})])
            self.timer.start()

        else:  # Fourier plane

            self.exp_system.turn_off_lamp()
            self.exp_system.superlum.set_hi_mode()
            self.exp_system.superlum.set_power_on()

            show_holo = self.ui.showHologramChkbox.isChecked()
            show_fft = self.ui.showFFTChkbox.isChecked()
            show_cropped = self.ui.showCroppedChkbox.isChecked()
            show_checkboxes = [show_holo, show_fft, show_cropped]

            self.show_selected = []

            for idx, val in enumerate(self._PLOT_FP_IMAGES):
                if show_checkboxes[idx]:
                    self.show_selected.append(val)

            if len(self.show_selected) == 0:
                self.show_errMsgBox("You need to show at least one image")

            self.ui.plotArea.figure.clear()
            self.imshow_axes = [None, None, None]
            self.imshow_plots = [None, None, None]

            self.timer = self.ui.plotArea.new_timer(self.REFRESH_INTERVAL, [(self.fp_image_grab, (), {})])
            self.timer.start()

        set_ui_status(self.ui, 'preview')
        
        if self.ui.rdBtnFP.isChecked():
            self.ui.gaussBlurChkbox.setEnabled(True)

    @Slot()
    def on_btnStop_clicked(self):

        logger.info("stop preview")

        self.set_ui_enabled()
        self.timer.stop()

        if self.ui.rdBtnIP.isChecked():
            self.exp_system.turn_off_lamp()
        else:
            self.exp_system.switch_superlum_power()

    @Slot()
    def on_btnSaveImg_clicked(self):

        filename = self.ui.edtSaveFilename.text()
        if filename.strip():
            if self.last_frame is not None:
                try:
                    path_to_file = os.path.join(self.save_root, datetime.datetime.now().strftime('%Y%m%d'), filename + '.tiff')
                    tif = TIFF.open(path_to_file, 'w')
                    tif.write_image(self.last_frame << self._SAVE_SHIFT_BIT)
                except Exception as e:
                    self.show_errMsgBox("Cannot save the image. Reason: \n\n" + repr(e))
                    return
            else:
                self.show_errMsgBox("no frame has been acquired yet")
        else:
            self.show_errMsgBox("filename is empty.")


    @Slot()
    def on_btnCtrlStrt_clicked(self):

        save_dir = os.path.join(self.save_root, datetime.datetime.now().strftime('%Y%m%d'), str(self.ui.ctrlSmpNospinBox.value()))

        if os.path.exists(save_dir):
            
            if len(os.listdir(save_dir)):

                msgBox = QMessageBox()
                msgBox.setText(f"The folder {save_dir} is non-empty. Continue may overwrite existing files.");
                msgBox.setInformativeText("Do you wish to continue?");
                ctnBtn = msgBox.addButton("Continue", QMessageBox.ActionRole)
                noBtn = msgBox.addButton(QMessageBox.Abort)
                msgBox.setDefaultButton(noBtn)
                msgBox.setIcon(QMessageBox.Question)
                
                choice = msgBox.exec()

                if msgBox.clickedButton() == ctnBtn:
                    pass
                else:
                    return

        else:

            msgBox = QMessageBox()
            msgBox.setText(f"The folder {save_dir} does not exist");
            msgBox.setInformativeText("Do you wish to create a new folder?");
            ctnBtn = msgBox.addButton("Create", QMessageBox.ActionRole)
            noBtn = msgBox.addButton(QMessageBox.Abort)
            msgBox.setDefaultButton(ctnBtn)
            msgBox.setIcon(QMessageBox.Question)
            
            choice = msgBox.exec()

            if msgBox.clickedButton() == ctnBtn:
                try:
                    os.mkdir(save_dir)
                except Exception as e:
                    self.show_errMsgBox("Cannot make a new folder. Reason: \n\n" + repr(e))
                    return
            else:
                return

        logger.info("start measure")
       
        params = {'save_dir': save_dir}

        self.exp_plan = BDMSingleLoop(params)

        self.job = ExpDispatcher(self.exp_system, self.exp_plan, params, self.before_exp, self.update_status, self.after_exp)

        self.job.start_exp()

    @Slot()
    def on_btnCtrlHlt_clicked(self):

        logger.warning("halt measure")

        self.set_ui_enabled()
        self.job.terminate()

    @Slot()
    def on_btnLmpOn_clicked(self):

        self.exp_system.turn_on_lamp()

    @Slot()
    def on_btnLmpOff_clicked(self):
        self.exp_system.turn_off_lamp()

    @Slot()
    def on_btnSLDChkSts_clicked(self):
        (on_status, hi_status) = self.exp_system.get_superlum_status()
        self.status_on_off(self.ui.lblSLDPowerTxt, on_status)
        self.status_on_off(self.ui.lblSLDHIOutputTxt, hi_status)

    @Slot()
    def on_btnSLDSwtchHI_clicked(self):
        self.exp_system.switch_superlum_hi()

    @Slot()
    def on_btnSLDSetHION_clicked(self):
        self.exp_system.superlum.set_hi_mode()
        self.exp_system.superlum.set_power_on()

    @Slot()
    def on_btnSLDSwtchPower_clicked(self):
        self.exp_system.switch_superlum_power()

    @Slot()
    def on_btnMCN01_clicked(self):
        self.exp_system.mc.move_n01()

    @Slot()
    def on_btnMCN003_clicked(self):
        self.exp_system.mc.move_n003()

    @Slot()
    def on_btnMCP003_clicked(self):
        self.exp_system.mc.move_p003()

    @Slot()
    def on_btnMCP01_clicked(self):
        self.exp_system.mc.move_p01()

    def update_status(self, state):

        self.ui.lblCtrlStsText.setText(state[0].name)
        self.ui.lblCtrlInfText.setText(state[1])

    def before_exp(self):

        set_ui_status(self.ui, 'measuring')

        if self.ui.monitorOffChkbox.isChecked():
            self.switch_monitor(False)

        self.ui.lblCtrlStrtTimeTxt.setText(datetime.datetime.now().strftime(self._DATETIME_FORMAT))
        self.ui.lblCtrlEndTimeTxt.setText('')

        self.exp_system.turn_off_lamp()
        self.exp_system.set_superlum_on()

    def after_exp(self):

        self.set_ui_enabled()

        # run after exp finishes, whether it naturally ends or is terminated by force
        if self.ui.monitorOffChkbox.isChecked():
            self.switch_monitor(True)
        self.ui.lblCtrlEndTimeTxt.setText(self.get_current_formatted_time())

        self.exp_system.set_superlum_off()

    def switch_monitor(self, state):
        # True = on, False = off
        if state:
            subprocess.Popen([self._PATH_TO_NIRCMD, "monitor", "on"])
        else:
            subprocess.Popen([self._PATH_TO_NIRCMD, "monitor", "off"])

    def get_fp_crop_params(self, gpu=False):
        with open(self._CONFIG_FILE, 'r') as json_file:
            bdm_params = json.load(json_file)
        aoi_params = bdm_params['AOI']

        crop_txt = 'FP_CROP_GPU' if gpu else 'FP_CROP_CPU'
        return {
            'OFFSET_X': aoi_params[crop_txt]['OFFSET_X'],
            'OFFSET_Y': aoi_params[crop_txt]['OFFSET_Y'],
            'SIZE_X': aoi_params[crop_txt]['SIZE_X'],
            'SIZE_Y': aoi_params[crop_txt]['SIZE_Y'],
        }

    def set_img_stats(self, img):
        fpmax = np.amax(np.amax(img))
        fpmin = np.amin(np.amin(img))
        saturation = fpmax / self._PLOT_SETTINGS['hologram']['vmax'] * 100

        self.ui.fpMinValLbl.setText(str(fpmin))
        self.ui.fpMaxValLbl.setText(str(fpmax))
        self.ui.fpSatValLbl.setText('{:.1f} %'.format(saturation))

        if saturation > 99:
            self.ui.fpSatValLbl.setStyleSheet("color: red;")
        else:
            self.ui.fpSatValLbl.setStyleSheet("color: black;")

    def format_plot(self):

        for ax in self.imshow_axes:

            if ax != None:
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                ax.set_axis_off()

        self.ui.plotArea.draw()

        plt.pause(0.001)

    def ip_image_grab(self):

        r = self.exp_system.image_camera.grab_one()

        self.set_img_stats(r)

        self.last_frame = r

        plot_settings = self._PLOT_SETTINGS['microscopy']

        if self.imshow_axes[0] == None:
            self.imshow_axes[0] = self.ui.plotArea.figure.add_subplot(1, 1, 1)
            self.imshow_plots[0] = self.imshow_axes[0].imshow(r, cmap=plot_settings['cmap'],
                                                              vmin=plot_settings['vmin'],
                                                              vmax=plot_settings['vmax'])
        else:
            self.imshow_plots[0].set_data(r)

        self.format_plot()

    def fp_image_grab(self):

        aoi_params = self.aoi_params

        xstrt = aoi_params.get('OFFSET_X', 0)
        ystrt = aoi_params.get('OFFSET_Y', 0)
        xsz = aoi_params.get('SIZE_X', 256)
        ysz = aoi_params.get('SIZE_Y', 256)

        r = self.exp_system.fourier_camera.grab_one()

        self.set_img_stats(r)

        self.last_frame = r

        y = np.fft.fft2(r)
        y = np.fft.fftshift(y)
        yy = y[ystrt:ystrt + ysz, xstrt:xstrt + xsz]
        yy = np.log(np.abs(yy))

        if self.ui.gaussBlurChkbox.isChecked():
            yy = gaussian_filter(yy, 2)

        imshow_data = {'hologram': r, 'fft': np.log(np.abs(y)), 'cropped': yy}
        # print(np.min(np.min(np.log(np.abs(yy)))), np.max(np.max(np.log(np.abs(yy)))))

        if self.imshow_axes[0] == None:

            for idx, val in enumerate(self.show_selected):
                current_plot_settings = self._PLOT_SETTINGS[val]

                self.imshow_axes[idx] = self.ui.plotArea.figure.add_subplot(1, len(self.show_selected), idx + 1)
                self.imshow_plots[idx] = self.imshow_axes[idx].imshow(imshow_data[val],
                                                                      cmap=current_plot_settings['cmap'],
                                                                      vmin=current_plot_settings['vmin'],
                                                                      vmax=current_plot_settings['vmax'])

        else:

            for idx, val in enumerate(self.show_selected):
                self.imshow_plots[idx].set_data(imshow_data[val])

        self.format_plot()

        # for idx, val in enumerate(self.show_selected):

        #     self.imshow_axes[idx].get_xaxis().set_visible(False)
        #     self.imshow_axes[idx].get_yaxis().set_visible(False)
        #     self.imshow_axes[idx].set_axis_off()

        # self.ui.plotArea.draw()

        # plt.pause(0.001)


if __name__ == "__main__":

    import logging.config
    logging.config.fileConfig('py_logging.conf')

    app = QApplication(sys.argv)

    window = UnifiedBDIWindow()
    window.show()

    sys.exit(app.exec_())
