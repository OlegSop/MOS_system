"""
Importing the main python files of the system,
which contain the implementation of its additional classes and interfaces.
"""
import TemperatureForecasting
import SensorControllerAccessInterface
import DataAccessInterface
import InformationPanelWindow
import RecommendationModel

# Additional required Python modules.
from PyQt5 import QtWidgets
import sys


# The class of the main object of synchronous motor condition monitoring recommendation system
class MainSystemObject:

    # Constructor method of a MainSystemObject class
    def __init__(self):
        self.processFlag = 1
        self.sensorData = None
        self.numberOfNewSensorData = None
        self.TempForecaster, self.Recommendator, self.DAI, self.SensorController, self.Window, = self.startSystem()

    # Destructor method of a MainSystemObject class
    def __del__(self):
        print('Delete all MainSystemObject instances from memory')

    # Method that loads all the main objects of the system, the machine learning models and information panel.
    def startSystem(self):
        self.TempForecaster = TemperatureForecasting.TemperatureForecastingModel(r'models\XGB_Model.pkl')
        self.Recommendator = RecommendationModel.RecommendationModel(r'models\KNeighborsModel.pkl')
        self.DAI = DataAccessInterface.DataAccessInterface
        self.SensorController = SensorControllerAccessInterface.SensorControllerAccessInterface
        self.Window = InformationPanelWindow.MainWindow
        # self.open_close_InformationPanel()
        self.manageProcesses()

        return self.TempForecaster, self.Recommendator, self.DAI, self.SensorController, self.Window

    # Method that call destructor method and terminates program execution.
    def stopSystem(self):
        del self.TempForecaster, self.Window, self.DAI, self.SensorController, self
        print("Terminate main system process")
        sys.exit()

    # Method that controls the opening and closing of the information panel
    def open_close_InformationPanel(self):
        app = QtWidgets.QApplication(sys.argv)
        win = self.Window()
        win.show()
        if app.exec_():
            self.processFlag = 0

    # Method conductor that determines the current activity of the system
    def manageProcesses(self):
        incorrectProcessFlagCounts = 0
        while True:
            if self.processFlag == 1:
                print("Starting temperature forecasting process")
                self.forecastTemperatures()
                self.numberOfNewSensorData = self.getNumberOfNewSensorData()
                print(self.numberOfNewSensorData)
                if self.numberOfNewSensorData >= 3:
                    self.processFlag = 2
                else:
                    self.SensorController.sendTimerRestartSignal()
            elif self.processFlag == 2:
                print("Starting recommendation process")
                self.makeRecommendations()
                self.processFlag = 1
                self.SensorController.sendTimerRestartSignal()
            elif self.processFlag == 0:
                self.stopSystem()
            else:
                incorrectProcessFlagCounts += 1
                print("Incorrect process flag №{}".format(incorrectProcessFlagCounts))
                if incorrectProcessFlagCounts >= 5:
                    print("Incorrect process flag error. System will be terminated!")
                    sys.exit()

    # Method that implements the process of predicting the rotor temperatures of a synchronous motor
    def forecastTemperatures(self):
        self.sensorData = self.SensorController.receiveSensorDataArray()
        self.sensorData = self.TempForecaster.getSensorDataList(self.sensorData)
        scaledArray = self.TempForecaster.prepareSensorData(self.sensorData)
        predictedValue = self.TempForecaster.makeTemperaturePrediction(scaledArray)
        estimatedValuesList = self.TempForecaster.formEstimatedDataList(self.sensorData, predictedValue)
        self.DAI.saveEstimatedDataList(estimatedValuesList)

    # Method that returns the current value of new sensor and forecast data entries in the database
    def getNumberOfNewSensorData(self):
        new_sensor_data_number = self.DAI.checkNumberOfNewSensorData()
        return new_sensor_data_number

    # Method that implements the recommendation process of the system
    def makeRecommendations(self):
        estimated_data = self.DAI.getEstimatedDataList()
        estimated_data = self.Recommendator.getEstimatedDataList(estimated_data)
        motorCondition = self.Recommendator.classifyMotorState(estimated_data)
        motorEfficiency, recommendation = self.Recommendator.formRecommendation(motorCondition)
        indicators_data, recommendation_data = self.Recommendator.formDataForSaveAndOutput(estimated_data,
                                                                                           motorEfficiency,
                                                                                           recommendation)
        self.DAI.saveIndicatorAndRecommendationDataList(indicators_data, recommendation_data)
        self.Window.updateInformationPanel(indicators_data, recommendation_data)


"""
The main system function that creates an object of the Main System Object class, 
thereby starting the execution flow of system processes
"""
if __name__ == '__main__':
    MainObject = MainSystemObject()
