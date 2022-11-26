from itertools import chain
import joblib
from datetime import datetime
import DataAccessInterface


class RecommendationModel:
    def __init__(self, path_to_model):
        self.estimatedDataList = None
        self.motorStateClasses = None
        self.model = self.loadClassificationModel(path_to_model)

    def loadClassificationModel(self, path_to_model):
        self.model = joblib.load(path_to_model)
        print("Condition Classification Model was loaded")
        return self.model

    def getEstimatedDataList(self, estimatedDataList):
        self.estimatedDataList = estimatedDataList.drop(['measurment_ID', 'indicator_ID', 'voltage_q_axis',
                                                         'voltage_d_axis', 'current_q_axis', 'current_d_axis'], axis=1)
        self.estimatedDataList = self.estimatedDataList[['coolant_temperature', 'ambient_temperature', 'current_mean',
                                                         'voltage_mean', 'motor_speed', 'motor_torque',
                                                         'rotor_temperature']]
        self.estimatedDataList['motor_torque'] = self.estimatedDataList['motor_torque'].abs()
        self.estimatedDataList.rename(columns={'coolant_temperature': 'coolant', 'ambient_temperature': 'ambient',
                                               'current_mean': 'i_s', 'voltage_mean': 'u_s',
                                               'motor_torque': 'torque', 'rotor_temperature': 'pm'}, inplace=True)
        return self.estimatedDataList

    def classifyMotorState(self, estimatedDataList):
        self.motorStateClasses = self.model.predict(estimatedDataList)
        return self.motorStateClasses

    def formRecommendation(self, motorStates):
        motorEfficiency = " "
        Recommendation = " "
        self.motorStateClasses = list(chain.from_iterable(motorStates))
        self.motorStateClasses = {'motor_temperature_state': self.motorStateClasses[0],
                                  'motor_current_state': self.motorStateClasses[1],
                                  'motor_speed_state': self.motorStateClasses[2],
                                  'motor_torque_state': self.motorStateClasses[3]}
        if self.motorStateClasses['motor_temperature_state'] == 'normal' and \
                self.motorStateClasses['motor_current_state'] == 'normal':
            if self.motorStateClasses['motor_speed_state'] == 'low' and \
                    self.motorStateClasses['motor_torque_state'] == 'efficient':
                motorEfficiency = "Низька"
                Recommendation = "Обертовий момент знаходиться в оптимальних межах.\nДля отримання оптимальної " \
                                 "швидкості рекомендується утримувати поточний діапазон обертового моменту. "
            elif self.motorStateClasses['motor_speed_state'] == 'optimal' and \
                    self.motorStateClasses['motor_torque_state'] == 'optimal':
                pass
            else:
                motorEfficiency = "Не визначено"
                Recommendation = "Підготовка нових рекомендацій"

        elif (self.motorStateClasses['motor_temperature_state'] == 'high' and
              self.motorStateClasses['motor_current_state'] == 'normal') or \
                (self.motorStateClasses['motor_temperature_state'] == 'normal' and
                 self.motorStateClasses['motor_current_state'] == 'high'):
            pass

        elif self.motorStateClasses['motor_temperature_state'] == 'critical' or \
                self.motorStateClasses['motor_current_state'] == 'critical':
            motorEfficiency = "Дуже низька"
            Recommendation = "Критичні показники. Накладено обмеження на подання обертового моменту на двигун. "

        else:
            motorEfficiency = "Не визначено"
            Recommendation = "Підготовка нових рекомендацій"

        return motorEfficiency, Recommendation

    def formDataForSaveAndOutput(self, estimated_data_list, motor_efficiency, recommendation):
        self.estimatedDataList = estimated_data_list.drop(['coolant', 'ambient', 'u_s'], axis=1)
        self.estimatedDataList = self.estimatedDataList.values.tolist()
        print(self.estimatedDataList)
        self.estimatedDataList = list(chain.from_iterable(self.estimatedDataList))
        self.estimatedDataList = [int(item) for item in self.estimatedDataList]

        estimated_data_keys = ["motor_current_indicator", "motor_speed_indicator", "motor_torque_indicator",
                               "motor_temperature_indicator"]
        indicator_dictionary = dict(zip(estimated_data_keys, self.estimatedDataList))

        recommendation_datetime = datetime.today()
        recommendation_time = recommendation_datetime.strftime("%H:%M")
        recommendation_date = recommendation_datetime.strftime("%d-%m-%Y")

        recommendation_dictionary = {'recommendation': recommendation, 'motor_efficiency': motor_efficiency,
                                     'recommendation_date': recommendation_date,
                                     'recommendation_time': recommendation_time}

        return indicator_dictionary, recommendation_dictionary


def main():
    Classifier = RecommendationModel(r'models\KNeighborsModel.pkl')
    DAI = DataAccessInterface.DataAccessInterface()
    estimatedData = DAI.getEstimatedDataList()
    estimatedData = Classifier.getEstimatedDataList(estimatedData)
    print(estimatedData.to_string())
    motorStates = Classifier.classifyMotorState(estimatedData)
    print(motorStates)
    motor_efficiency, recommendation = Classifier.formRecommendation(motorStates)
    dict1, dict2 = Classifier.formDataForSaveAndOutput(estimatedData, motor_efficiency, recommendation)
    print(dict1)
    print(dict2)
    DAI.saveIndicatorAndRecommendationDataList(dict1, dict2)



    """
    print(sensorData)
    scaledArr = Forecaster.prepareSensorData(sensorData)
    print(scaledArr)
    prediction = Forecaster.makeTemperaturePrediction(scaledArr)
    print(prediction)
    estimatedData = Forecaster.formEstimatedDataList(sensorData, prediction)
    print(estimatedData)"""


if __name__ == '__main__':
    main()
