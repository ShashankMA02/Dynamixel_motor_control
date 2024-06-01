import os
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE = 24               # Control table address is different for Dynamixel model
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36
ADDR_MX_TORQUE_MAX = 14

# Protocol version
PROTOCOL_VERSION = 1.0                   # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID = 6                               # Dynamixel ID: 1
BAUDRATE = 1000000                       # Dynamixel default baudrate : 57600
DEVICENAME = '/dev/ttyUSB0'              # Check which port is being used on your controller
                                          # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
TORQUE_ENABLE = 1                        # Value for enabling the torque
TORQUE_DISABLE = 0                       # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE = 1710        # Start position
DXL_MAXIMUM_POSITION_VALUE = 2387            # End position
DXL_MOVING_STATUS_THRESHOLD = 20         # Dynamixel moving status threshold
STEP_SIZE = 50                            # Position increment step size

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

def enable_torque():
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % DXL_ID)

def set_goal_position(goal_position):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def read_present_position():
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)
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
    enable_torque()

    goal_position = DXL_MINIMUM_POSITION_VALUE

    while goal_position <= DXL_MAXIMUM_POSITION_VALUE:
        set_goal_position(goal_position)

        while True:
            present_position = read_present_position()
            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, goal_position, present_position))

            if abs(goal_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break

            time.sleep(0.1)
        
        goal_position += STEP_SIZE
        time.sleep(1)  # Wait for 1 second before moving to the next step

    close_port()

if __name__ == "__main__":
    main()
