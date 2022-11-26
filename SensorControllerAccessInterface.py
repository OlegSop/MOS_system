import numpy as np
import time


class SensorControllerAccessInterface:

    @staticmethod
    def receiveSensorDataArray():
        arr = np.array([[35.16605010186468, 18.317066192626957, -126.2061004638672, 969.3536649480908,
                         -191.9640355027481, 77.91515350341797, 27.350014116035787,
                         -87.0339299414562]])

        return arr

    @staticmethod
    def sendTimerRestartSignal():
        print('Timer restart signal was sent')
        time.sleep(1.0)
        print('Sensor Data Estimation')
        time.sleep(3.0)
        print('Sensor Data Received')
