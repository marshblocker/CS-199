// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

struct DeviceData {
    string deviceId;
    uint256 x;
    uint256 y;
    string timestamp;
}

contract DeviceManager {
    // Maps device id to device data.
    mapping(string => DeviceData) public deviceDataMap;

    event storedDeviceData(address indexed sender, DeviceData data);

    function storeDeviceData(
        string memory deviceId,
        uint256 x,
        uint256 y,
        string memory timestamp
    ) public {
        deviceDataMap[deviceId] = DeviceData({
            deviceId: deviceId,
            x: x,
            y: y,
            timestamp: timestamp
        });

        emit storedDeviceData(msg.sender, deviceDataMap[deviceId]); 
    }
}