// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract SensorDataStorage {
    struct SensorData {
        int temp_max;
        int temp_min;
        int temp_mean;
        int relative_humidity;
        int wind_speed;
    }

    mapping (string => SensorData) public sensorData;

    event storedSensorData(string sensorId, SensorData data, int year, int month, int day);

    function storeSensorData(
            string[] memory _sensorIds, 
            SensorData[] memory _sensorData, 
            int _year,
            int _month,
            int _day) public {
        for (uint i = 0; i < _sensorData.length; i++) {
            sensorData[_sensorIds[i]] = _sensorData[i];
            emit storedSensorData(_sensorIds[i], _sensorData[i], _year, _month, _day);
        }
    }
}