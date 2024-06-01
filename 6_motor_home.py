import os
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE = 24               # Control table address is different for Dynamixel model
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36

# Protocol version
PROTOCOL_VERSION = 1.0                   # See which protocol version is used in the Dynamixel

# Default setting
DXL_IDS = [1, 2, 3, 4, 5, 6]             # Dynamixel IDs: 1, 2, 3, 4, 5, 6
BAUDRATE = 1000000                       # Dynamixel default baudrate : 57600
DEVICENAME = '/dev/ttyUSB0'              # Check which port is being used on your controller
TORQUE_ENABLE = 1                        # Value for enabling the torque
TORQUE_DISABLE = 0                       # Value for disabling the torque

# Goal positions
GOAL_POSITION_2560 = 2387
GOAL_POSITION_1536 = 1710   # + or - 30 degree instead of 45

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

def open_port():
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        quit()

def set_baudrate():
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        quit()

def enable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % dxl_id)

def set_goal_position(dxl_id, goal_position):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def read_present_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    return dxl_present_position

def close_port():
    portHandler.closePort()

def main():
    open_port()
    set_baudrate()

    # Enable torque for all motors
    for dxl_id in DXL_IDS:
        enable_torque(dxl_id)

    # Set goal positions for motors 1, 3, 5 to 2560 and motors 2, 4, 6 to 1536
    set_goal_position(1, GOAL_POSITION_2560)
    set_goal_position(3, GOAL_POSITION_2560)
    set_goal_position(5, GOAL_POSITION_2560)
    set_goal_position(2, GOAL_POSITION_1536)
    set_goal_position(4, GOAL_POSITION_1536)
    set_goal_position(6, GOAL_POSITION_1536)

    while True:
        # Read and print present positions
        for dxl_id in DXL_IDS:
            present_position = read_present_position(dxl_id)
            goal_position = GOAL_POSITION_2560 if dxl_id in [1, 3, 5] else GOAL_POSITION_1536
            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (dxl_id, goal_position, present_position))

        # Check if all motors have reached their goal positions
        if all(abs((GOAL_POSITION_2560 if dxl_id in [1, 3, 5] else GOAL_POSITION_1536) - read_present_position(dxl_id)) <= 20 for dxl_id in DXL_IDS):
            break

        time.sleep(0.1)

    close_port()

if __name__ == "__main__":
    main()
