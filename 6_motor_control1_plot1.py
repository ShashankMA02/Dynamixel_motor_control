#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import matplotlib.pyplot as plt
from dynamixel_sdk import *                    # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36
ADDR_MX_PRESENT_LOAD       = 40               # Address for present load

# Data Byte Length
LEN_MX_GOAL_POSITION       = 4
LEN_MX_PRESENT_POSITION    = 4
LEN_MX_PRESENT_LOAD        = 2                # Length for present load data

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_IDs                     = [1, 2, 3, 4, 5, 6]
BAUDRATE                    = 1000000           # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = 0                 # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 1000              # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold

# Goal positions for each motor
dxl_goal_positions = [
    [2390, 2048, 2350, 1700, 1024, 1024, 1024, 1536, 1024],
    [1706, 2048, 2350, 1700, 3072, 3072, 3072, 3072, 2560],
    [2390, 2048, 2350, 1700, 1024, 1536, 1024, 1024, 1536],
    [1706, 2048, 2350, 1700, 3072, 3072, 2560, 3072, 3072],
    [2390, 2048, 2350, 1700, 1024, 1024, 1536, 1024, 1024],  
    [1706, 2048, 2350, 1700, 3072, 2560, 3072, 2560, 3072]
]

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_MX_GOAL_POSITION, LEN_MX_GOAL_POSITION)

# Open port
if not portHandler.openPort():
    print("Failed to open the port")
    quit()

# Set port baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to change the baudrate")
    quit()

# Enable Dynamixel Torque for each motor
for DXL_ID in DXL_IDs:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % DXL_ID)

# Initialize data storage
positions = {DXL_ID: [] for DXL_ID in DXL_IDs}
loads = {DXL_ID: [] for DXL_ID in DXL_IDs}

# Main loop for goal position commands
for index in range(len(dxl_goal_positions[0])):
    param_goal_positions = []
    for i, DXL_ID in enumerate(DXL_IDs):
        param_goal_positions.append([
            DXL_LOBYTE(DXL_LOWORD(dxl_goal_positions[i][index])),
            DXL_HIBYTE(DXL_LOWORD(dxl_goal_positions[i][index])),
            DXL_LOBYTE(DXL_HIWORD(dxl_goal_positions[i][index])),
            DXL_HIBYTE(DXL_HIWORD(dxl_goal_positions[i][index]))
        ])
        # Add goal position to syncwrite parameter storage
        dxl_addparam_result = groupSyncWrite.addParam(DXL_ID, param_goal_positions[-1])
        if not dxl_addparam_result:
            print("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID)
            quit()

    # Syncwrite goal position
    dxl_comm_result = groupSyncWrite.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    # Clear syncwrite parameter storage
    groupSyncWrite.clearParam()

    time.sleep(0.1)  # Delay for the motors to start moving

    # Read present position and load for each motor
    while True:
        moving = False
        for DXL_ID in DXL_IDs:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)
            dxl_present_load, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_MX_PRESENT_LOAD)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            # Convert load value to signed value (11 bits)
            if dxl_present_load > 1023:
                dxl_present_load -= 1024

            positions[DXL_ID].append(dxl_present_position)
            loads[DXL_ID].append(dxl_present_load)

            if abs(dxl_goal_positions[DXL_IDs.index(DXL_ID)][index] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                moving = True

        if not moving:
            break

    time.sleep(0.1)

# Disable Dynamixel Torque for each motor
for DXL_ID in DXL_IDs:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Close port
portHandler.closePort()

# Plot position vs. load for each motor
plt.figure(figsize=(12, 8))
for DXL_ID in DXL_IDs:
    plt.plot(positions[DXL_ID], loads[DXL_ID], label=f'Motor {DXL_ID}')

plt.xlabel('Position')
plt.ylabel('Load')
plt.title('Position vs. Load for Dynamixel Motors')
plt.legend()
plt.grid()
plt.show()