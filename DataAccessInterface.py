import sqlite3
import pandas as pd


class DataAccessInterface:

    @staticmethod
    def getEstimatedDataList():
        connection = sqlite3.connect("database/systemDataBase.db")
        estimatedDataList = pd.read_sql_query("SELECT * FROM SensorAndPrognosesData ORDER BY measurment_ID DESC LIMIT 1"
                                              , connection)
        return estimatedDataList

    @staticmethod
    def saveEstimatedDataList(estimated_data):
        estimated_data_keys = ["coolant_temperature", "ambient_temperature", "current_d_axis", "current_q_axis",
                               "current_mean", "voltage_q_axis", "voltage_d_axis", "voltage_mean", "motor_speed",
                               "motor_torque", "rotor_temperature"]

        estimated_data_dictionary = dict(zip(estimated_data_keys, estimated_data))

        sql_insert_to_SensorAndPrognosesData_table = \
            """
            INSERT INTO SensorAndPrognosesData 
            (coolant_temperature, ambient_temperature,current_d_axis, 
            current_q_axis, current_mean,  voltage_d_axis, voltage_q_axis, voltage_mean, motor_speed, 
            motor_torque, rotor_temperature) VALUES 
            (:coolant_temperature, :ambient_temperature,:current_d_axis, :current_q_axis, :current_mean, 
            :voltage_d_axis, :voltage_q_axis, :voltage_mean, :motor_speed, :motor_torque, :rotor_temperature )
            """

        connection = sqlite3.connect("database/systemDataBase.db")
        cur = connection.cursor()
        cur.execute(sql_insert_to_SensorAndPrognosesData_table, estimated_data_dictionary)
        connection.commit()

    @staticmethod
    def saveIndicatorAndRecommendationDataList(indicator_data, recommendation_data):
        sql_insert_to_IndicatorData_table = \
            """
            INSERT INTO IndicatorData 
            (motor_temperature_indicator, motor_current_indicator,motor_speed_indicator, motor_torque_indicator ) VALUES 
            (:motor_temperature_indicator, :motor_current_indicator,:motor_speed_indicator, :motor_torque_indicator)
            """

        sql_update_keys_SensorAndPrognosesData_table = \
            """UPDATE SensorAndPrognosesData SET indicator_ID = ? WHERE measurment_ID in (SELECT measurment_ID
            FROM SensorAndPrognosesData WHERE indicator_ID is NULL) """

        sql_insert_to_Recommendation_table = \
            """
            INSERT INTO Recommendation 
            (recommendation, motor_efficiency, recommendation_date, recommendation_time ) VALUES 
            (:recommendation, :motor_efficiency, :recommendation_date, :recommendation_time)
            """

        sql_update_keys_IndicatorData_table = \
            """UPDATE IndicatorData SET recommendation_ID = ? WHERE indicator_ID in (SELECT indicator_ID
            FROM IndicatorData WHERE recommendation_ID is NULL) """

        connection = sqlite3.connect("database/systemDataBase.db")
        cur = connection.cursor()

        cur.execute(sql_insert_to_IndicatorData_table, indicator_data)
        indicator_ID = [cur.lastrowid]
        cur.execute(sql_update_keys_SensorAndPrognosesData_table, indicator_ID)
        connection.commit()

        cur.execute(sql_insert_to_Recommendation_table, recommendation_data)
        recommendation_ID = [cur.lastrowid]
        cur.execute(sql_update_keys_IndicatorData_table, recommendation_ID)
        connection.commit()

    @staticmethod
    def checkNumberOfNewSensorData():
        connection = sqlite3.connect("database/systemDataBase.db")
        DataRows = pd.read_sql_query("SELECT * FROM SensorAndPrognosesData ORDER BY measurment_ID DESC LIMIT 3"
                                     , connection)
        NewSensorDataNumber = int(DataRows['indicator_ID'].isna().sum())
        return NewSensorDataNumber


def main():
    """
    estimated_data = [18.3171, 27.35, -191.964, 77.9152, 207.1737, 35.1661, -126.2061, 131.0139, 969.3537, -87.0339,
                      67.1412]
    DAI = DataAccessInterface()
    DAI.saveEstimatedDataList(estimated_data)
    print("------------------------------------------------------")
    estimated_list = DAI.getEstimatedDataList()
    print(estimated_list)
    new = DAI.checkNumberOfNewSensorData()
    print(new)
    """


if __name__ == '__main__':
    main()
