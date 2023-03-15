// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract SensorDataStorage {
    struct SensorData {
        string date;
        int temp_max;
        int temp_min;
        int temp_mean;
        int relative_humidity;
        int wind_speed;
    }

    mapping (string => SensorData) public sensorData;

    event storedSensorData(string sensorId, SensorData data);

    // Define a function for storing sensor data.
    function storeSensorData(
            string memory _date, 
            int _temp_max, 
            int _temp_min,
            int _temp_mean, 
            int _relative_humidity, 
            int _wind_speed, 
            string memory _sensorId) public {

        sensorData[_sensorId] = SensorData({
            date: _date, 
            temp_max: _temp_max, 
            temp_min: _temp_min,
            temp_mean: _temp_mean, 
            relative_humidity: _relative_humidity, 
            wind_speed: _wind_speed
        });

        emit storedSensorData(_sensorId, sensorData[_sensorId]);
    }
}