

from PyQt5.QtCore import pyqtSlot

from Keithley.Keithley2182 import Keithley2182

from copy import deepcopy

# from util import AbstractThread
from util import AbstractLoopThread
from util import ExceptionHandling

from datetime import datetime
import logging


class Keithley2182_Updater(AbstractLoopThread):
    """This is the worker thread, which updates all instrument data of one Keithley 2182 device.

        For each device function, there is a wrapping method,
        which we can call by a signal, from the main thread. This wrapper sends
        the corresponding value to the device.

        The information from the device is collected in regular intervals (method "running"),
        and subsequently sent to the main thread. It is packed in a dict,
        the keys of which are displayed in the "sensors" dict in this class.
    """

    sensors = dict(Voltage_V=None)

    def __init__(self, comLock, InstrumentAddress='', log=None, **kwargs):
        super().__init__(**kwargs)
        self.instr = InstrumentAddress
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        self.save_InstrumentAddress = InstrumentAddress
        self.save_comLock = comLock
        # global Keithley
        # K_2182 = reload(Keithley.Keithley2182)

        self.Keithley2182 = Keithley2182(
            InstrumentAddress=InstrumentAddress, comLock=comLock)
        self.__name__ = 'Keithley2182_Updater ' + InstrumentAddress

    # @control_checks
    @ExceptionHandling
    def running(self):
        """Measure Voltage, send the data"""
        self.sensors['Voltage_V'] = self.Keithley2182.measureVoltage()

        self.sensors['realtime'] = datetime.now()

        self.sig_Infodata.emit(deepcopy(self.sensors))

        error = self.Keithley2182.query_error()
        if error[0] != '0':
            self.logger.error('code:{}, message:{}'.format(
                error[0], error[1].strip('"')))
            if error[0] == '-213':
                self.Keithley2182 = Keithley2182(
                    InstrumentAddress=self.save_InstrumentAddress, comLock=self.save_comLock)

    @pyqtSlot()
    @ExceptionHandling
    def read_Voltage(self):
        """read a Voltage from instrument. return value should be float"""
        return self.Keithley2182.measureVoltage()

    @pyqtSlot()
    @ExceptionHandling
    def speed_up(self):
        """increase measurement speed
        """
        self.Keithley2182.setRate('FAS')

    @pyqtSlot()
    @ExceptionHandling
    def ToggleDisplay(self, bools):
        if bools:
            self.Keithley2182.DisplayOn()
        else:
            self.Keithley2182.DisplayOff()

    @pyqtSlot()
    @ExceptionHandling
    def ToggleFrontAutozero(self, bools):
        if bools:
            self.Keithley2182.FrontAutozeroOn()
        else:
            self.Keithley2182.FrontAutozeroOff()

    @pyqtSlot()
    @ExceptionHandling
    def ToggleAutozero(self, bools):
        if bools:
            self.Keithley2182.AutozeroOn()
        else:
            self.Keithley2182.AutozeroOff()

    @pyqtSlot()
    @ExceptionHandling
    def ToggleAutorange(self, bools):
        if bools:
            self.Keithley2182.AutorangeOn()
        else:
            self.Keithley2182.AutorangeOff()