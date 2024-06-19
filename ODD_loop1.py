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
DXL_MAIN_ID = 1  # Dynamixel ID that will decrement in small steps
DXL_IDS = [1, 2, 3, 4, 5, 6]  # List of all Dynamixel IDs
BAUDRATE = 1000000  # Dynamixel default baudrate
DEVICENAME = '/dev/ttyUSB0'  # Check which port is being used on your controller
TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE = 2048  # Start position
DXL_ODD_MAX_POSITION_VALUE = 1540  # End position for odd motors
DXL_EVEN_MAX_POSITION_VALUE = 2557  # End position for even motors
DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold
STEP_SIZE_MAIN = -5  # Main motor decrement step size
STEP_SIZE = 5  # Position increment step size for other motors
TORQUE_MAX_LEVEL = 300  # Maximum torque level (adjust as needed, 0-1023 for MX series)

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

def move_motor(dxl_id, start_position, end_position, step_size):
    goal_position = start_position

    while (goal_position >= end_position if step_size < 0 else goal_position <= end_position):
        set_goal_position(dxl_id, goal_position)

        while True:
            present_position = read_present_position(dxl_id)
            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (dxl_id, goal_position, present_position))

            if abs(goal_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break

            time.sleep(0.1)

        goal_position += step_size

    # Reset to home position
    set_goal_position(dxl_id, start_position)
    while True:
        present_position = read_present_position(dxl_id)
        print("[ID:%03d] ResetPos:%03d  PresPos:%03d" % (dxl_id, start_position, present_position))

        if abs(start_position - present_position) <= DXL_MOVING_STATUS_THRESHOLD:
            break

        time.sleep(0.1)

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
    
    goal_position_main = DXL_MINIMUM_POSITION_VALUE

    while True:
        # Decrement the main motor (motor 1) in steps of -5
        for goal_position_main in range(DXL_MINIMUM_POSITION_VALUE, DXL_ODD_MAX_POSITION_VALUE - 1, STEP_SIZE_MAIN):
            set_goal_position(DXL_MAIN_ID, goal_position_main)

            while True:
                present_position_main = read_present_position(DXL_MAIN_ID)
                print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_MAIN_ID, goal_position_main, present_position_main))

                if abs(goal_position_main - present_position_main) <= DXL_MOVING_STATUS_THRESHOLD:
                    break

                time.sleep(0.1)

            # For each step of motor 1, move all other motors
            for dxl_id in [2, 4, 6]:
                move_motor(dxl_id, DXL_MINIMUM_POSITION_VALUE, DXL_EVEN_MAX_POSITION_VALUE, STEP_SIZE)
            for dxl_id in [3, 5]:
                move_motor(dxl_id, DXL_MINIMUM_POSITION_VALUE, DXL_ODD_MAX_POSITION_VALUE, -STEP_SIZE)
        
        # Reset motor 1 to home position
        set_goal_position(DXL_MAIN_ID, DXL_MINIMUM_POSITION_VALUE)
        while True:
            present_position_main = read_present_position(DXL_MAIN_ID)
            print("[ID:%03d] ResetPos:%03d  PresPos:%03d" % (DXL_MAIN_ID, DXL_MINIMUM_POSITION_VALUE, present_position_main))

            if abs(DXL_MINIMUM_POSITION_VALUE - present_position_main) <= DXL_MOVING_STATUS_THRESHOLD:
                break

            time.sleep(0.1)

        time.sleep(1)  # Wait for 1 second before the next loop iteration

    close_port()

if __name__ == "__main__":
    main()
