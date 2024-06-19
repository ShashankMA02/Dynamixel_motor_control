import os
import time
import csv  # Add CSV module
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

# CSV file name
CSV_FILE = 'motor_positions.csv'

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

def initialize_csv():
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Iteration', 'Motor1', 'Motor2', 'Motor3', 'Motor4', 'Motor5', 'Motor6']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def write_to_csv(iteration, motor_positions):
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([iteration] + motor_positions)

def main():
    open_port()
    set_baudrate()
    
    initialize_csv()  # Initialize CSV file with header
    
    # Enable torque and set max torque level for all Dynamixels
    for dxl_id in DXL_IDS:
        enable_torque(dxl_id)
        set_torque_level(dxl_id, TORQUE_MAX_LEVEL)
    
    iteration_count = 1

    # Main loop structure as per your requirement
    for motorID1 in range(2048, 1535, -5):  # Range from 2048 to 1540, decrementing by 5
        for motorID2 in range(2048, 2558, 5):  # Range from 2048 to 2557, incrementing by 5
            move_motor(2, 2048, 2558, 5)
            reset_motor(2, 2048)
        for motorID3 in range(2048, 1535, -5):  # Range from 2048 to 1540, decrementing by 5
            move_motor(3, 2048, 1540, -5)
            reset_motor(3, 2048)
        for motorID4 in range(2048, 2558, 5):  # Range from 2048 to 2557, incrementing by 5
            move_motor(4, 2048, 2558, 5)
            reset_motor(4, 2048)
        for motorID5 in range(2048, 1535, -5):  # Range from 2048 to 1540, decrementing by 5
            move_motor(5, 2048, 1540, -5)
            reset_motor(5, 2048)
        for motorID6 in range(2048, 2558, 5):  # Range from 2048 to 2557, incrementing by 5
            move_motor(6, 2048, 2558, 5)
            reset_motor(6, 2048)
        move_motor(1, 2048, 1540, -5)  # Decrement motorID1 in steps of -5 in range of 2048 to 1540

        # Capture motor positions after each iteration and write to CSV
        motor_positions = []
        for dxl_id in DXL_IDS:
            position = read_present_position(dxl_id)
            motor_positions.append(position)
        
        write_to_csv(iteration_count, motor_positions)
        iteration_count += 1

    close_port()

if __name__ == "__main__":
    main()
