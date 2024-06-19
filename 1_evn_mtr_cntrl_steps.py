import os
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE = 24  # Control table address is different for Dynamixel model
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36
ADDR_MX_TORQUE_MAX = 14

# Protocol version
PROTOCOL_VERSION = 1.0  # See which protocol version is used in the Dynamixel

# Default setting
DXL_RUNNING_IDS = [6] #, 4, 6]  # Dynamixel IDs that will run
DXL_IDS = [1, 2, 3, 4, 5, 6]  # List of all Dynamixel IDs
BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
DEVICENAME = '/dev/ttyUSB0'  # Check which port is being used on your controller
# ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE = 2048  # Start position
DXL_MAXIMUM_POSITION_VALUE = 2557  # End position
DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold
STEP_SIZE = 10  # Position increment step size (positive for incrementing towards max position)
TORQUE_MAX_LEVEL = 512  # Maximum torque level (adjust as needed, 0-1023 for MX series)

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

def set_torque_level(dxl_id, torque_level):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_MAX, torque_level)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Torque level set to %d for Dynamixel#%d" % (torque_level, dxl_id))

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
    
    # Enable torque and set max torque level for all Dynamixels
    for dxl_id in DXL_IDS:
        enable_torque(dxl_id)
        set_torque_level(dxl_id, TORQUE_MAX_LEVEL)
    
    # Read the present position of all Dynamixels to hold them in place
    current_positions = {}
    for dxl_id in DXL_IDS:
        current_positions[dxl_id] = read_present_position(dxl_id)
    
    # Lock all Dynamixels except the ones running
    for dxl_id in DXL_IDS:
        if dxl_id not in DXL_RUNNING_IDS:
            set_goal_position(dxl_id, current_positions[dxl_id])
    
    for running_id in DXL_RUNNING_IDS:
        goal_position = DXL_MINIMUM_POSITION_VALUE
        while goal_position <= DXL_MAXIMUM_POSITION_VALUE:
            set_goal_position(running_id, goal_position)

            while True:
                present_position = read_present_position(running_id)
                print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (running_id, goal_position, present_position))

                if abs(goal_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                    break

                time.sleep(0.1)
            
            goal_position += STEP_SIZE  # Increment position
            time.sleep(1)  # Wait for 1 second before moving to the next step

    close_port()

if __name__ == "__main__":
    main()




# import os
# import time
# from dynamixel_sdk import *  # Uses Dynamixel SDK library

# # Control table address
# ADDR_MX_TORQUE_ENABLE = 24  # Control table address is different for Dynamixel model
# ADDR_MX_GOAL_POSITION = 30
# ADDR_MX_PRESENT_POSITION = 36
# ADDR_MX_TORQUE_MAX = 14

# # Protocol version
# PROTOCOL_VERSION = 1.0  # See which protocol version is used in the Dynamixel

# # Default setting
# DXL_ID_RUNNING = 2  # Dynamixel ID: 2,4,6
# DXL_IDS = [1, 2, 3, 4, 5, 6]  # List of all Dynamixel IDs
# BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
# DEVICENAME = '/dev/ttyUSB0'  # Check which port is being used on your controller
# # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
# TORQUE_ENABLE = 1  # Value for enabling the torque
# TORQUE_DISABLE = 0  # Value for disabling the torque
# DXL_MINIMUM_POSITION_VALUE = 2048  # Start position
# DXL_MAXIMUM_POSITION_VALUE = 2557  # End position
# DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold
# STEP_SIZE = 50  # Position increment step size (negative for decrementing towards max position)
# TORQUE_MAX_LEVEL = 512  # Maximum torque level (adjust as needed, 0-1023 for MX series)

# # Initialize PortHandler instance
# portHandler = PortHandler(DEVICENAME)

# # Initialize PacketHandler instance
# packetHandler = PacketHandler(PROTOCOL_VERSION)

# def open_port():
#     if portHandler.openPort():
#         print("Succeeded to open the port")
#     else:
#         print("Failed to open the port")
#         quit()

# def set_baudrate():
#     if portHandler.setBaudRate(BAUDRATE):
#         print("Succeeded to change the baudrate")
#     else:
#         print("Failed to change the baudrate")
#         quit()

# def enable_torque(dxl_id):
#     dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
#     if dxl_comm_result != COMM_SUCCESS:
#         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#     elif dxl_error != 0:
#         print("%s" % packetHandler.getRxPacketError(dxl_error))
#     else:
#         print("Dynamixel#%d has been successfully connected" % dxl_id)

# def set_torque_level(dxl_id, torque_level):
#     dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_MAX, torque_level)
#     if dxl_comm_result != COMM_SUCCESS:
#         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#     elif dxl_error != 0:
#         print("%s" % packetHandler.getRxPacketError(dxl_error))
#     else:
#         print("Torque level set to %d for Dynamixel#%d" % (torque_level, dxl_id))

# def set_goal_position(dxl_id, goal_position):
#     dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
#     if dxl_comm_result != COMM_SUCCESS:
#         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#     elif dxl_error != 0:
#         print("%s" % packetHandler.getRxPacketError(dxl_error))

# def read_present_position(dxl_id):
#     dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_MX_PRESENT_POSITION)
#     if dxl_comm_result != COMM_SUCCESS:
#         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#     elif dxl_error != 0:
#         print("%s" % packetHandler.getRxPacketError(dxl_error))
#     return dxl_present_position

# def close_port():
#     portHandler.closePort()

# def main():
#     open_port()
#     set_baudrate()
    
#     # Enable torque and set max torque level for all Dynamixels
#     for dxl_id in DXL_IDS:
#         enable_torque(dxl_id)
#         set_torque_level(dxl_id, TORQUE_MAX_LEVEL)
    
#     # Read the present position of all Dynamixels to hold them in place
#     current_positions = {}
#     for dxl_id in DXL_IDS:
#         current_positions[dxl_id] = read_present_position(dxl_id)
    
#     # Lock all Dynamixels except the one running
#     for dxl_id in DXL_IDS:
#         if dxl_id != DXL_ID_RUNNING:
#             set_goal_position(dxl_id, current_positions[dxl_id])
    
#     goal_position = DXL_MINIMUM_POSITION_VALUE

#     while goal_position >= DXL_MAXIMUM_POSITION_VALUE:
#         set_goal_position(DXL_ID_RUNNING, goal_position)

#         while True:
#             present_position = read_present_position(DXL_ID_RUNNING)
#             print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID_RUNNING, goal_position, present_position))

#             if abs(goal_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
#                 break

#             time.sleep(0.1)
        
#         goal_position += STEP_SIZE  # Decrement position
#         time.sleep(1)  # Wait for 1 second before moving to the next step

#     close_port()

# if __name__ == "__main__":
#     main()
