import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from itertools import chain
import joblib


class TemperatureForecastingModel:
    def __init__(self, path_to_model):
        self.sensorDataList = None
        self.estimatedDataList = None
        self.model = self.loadForecastingModel(path_to_model)

    def loadForecastingModel(self, path_to_model):
        self.model = joblib.load(path_to_model)
        print("Temperature Forecasting Model was loaded")
        return self.model

    def getSensorDataList(self, array):
        self.sensorDataList = pd.DataFrame(array, columns=['u_q', 'coolant', 'u_d', 'motor_speed', 'i_d', 'i_q',
                                                           'ambient', 'torque'])

        if {'i_d', 'i_q', 'u_d', 'u_q'}.issubset(set(self.sensorDataList.columns.tolist())):
            extra_feats = {'i_s': lambda x: np.sqrt((x['i_d'] ** 2 + x['i_q'] ** 2)),
                           'u_s': lambda x: np.sqrt((x['u_d'] ** 2 + x['u_q'] ** 2))}
        self.sensorDataList = self.sensorDataList.assign(**extra_feats)
        self.sensorDataList = self.sensorDataList[
            ['coolant', 'ambient', 'i_d', 'i_q', 'i_s', 'u_q', 'u_d', 'u_s', 'motor_speed', 'torque']]

        return self.sensorDataList

    @staticmethod
    def prepareSensorData(SensorData):
        SensorArray = SensorData.to_numpy()
        scaler = StandardScaler()
        scaler.fit(SensorArray)
        SensorArray_scaled = scaler.transform(SensorArray)

        return SensorArray

    def makeTemperaturePrediction(self, ScaledArray):
        predicted_temperature = self.model.predict(ScaledArray)

        return predicted_temperature

    def formEstimatedDataList(self, SensorData, PredictedTemperature):
        self.estimatedDataList = SensorData.assign(pm=PredictedTemperature)
        print(self.estimatedDataList.to_string())
        self.estimatedDataList = self.estimatedDataList.values.tolist()
        self.estimatedDataList = list(chain.from_iterable(self.estimatedDataList))
        self.estimatedDataList = [round(item, 4) for item in self.estimatedDataList]
        return self.estimatedDataList


def main():
    """
    array = SensorControllerAccessInterface.receiveSensorDataArray()
    Forecaster = TemperatureForecastingModel(r'models\XGB_Model.pkl')
    print(Forecaster.model)
    sensorData = Forecaster.getSensorDataList(array)
    print(sensorData)
    scaledArr = Forecaster.prepareSensorData(sensorData)
    print(scaledArr)
    prediction = Forecaster.makeTemperaturePrediction(scaledArr)
    print(prediction)
    estimatedData = Forecaster.formEstimatedDataList(sensorData, prediction)
    print(estimatedData)
    """


if __name__ == '__main__':
    main()
