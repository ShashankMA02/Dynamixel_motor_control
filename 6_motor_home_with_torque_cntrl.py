import time
from dynamixel_sdk import *

# Control table addresses for MX series Dynamixel
ADDR_MX_TORQUE_ENABLE = 24           # Address for enabling/disabling torque
ADDR_MX_TORQUE_LIMIT = 34            # Address for torque limit
ADDR_MX_GOAL_POSITION = 30           # Address for goal position
ADDR_MX_PRESENT_POSITION = 36        # Address for present position

# Protocol version
PROTOCOL_VERSION = 1.0               # Protocol version used in the Dynamixel

# Default settings
BAUDRATE = 1000000                   # Dynamixel default baudrate
DEVICENAME = '/dev/ttyUSB0'          # Serial port name, check your device name
TORQUE_ENABLE = 1                    # Value for enabling torque
TORQUE_DISABLE = 0                   # Value for disabling torque
TORQUE_LIMIT = 500                   # Torque limit value (0 to 1023 for MX series)

# Goal positions
GOAL_POSITION_2560 = 2048   #2387           # Goal position for motors 1, 3, 5
GOAL_POSITION_1536 = 2048   #1710           # Goal position for motors 2, 4, 6

# Dynamixel IDs
DXL_IDS = [1, 2, 3, 4, 5, 6]         # Dynamixel IDs: 1 to 6

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
        print(f"Failed to enable torque for ID {dxl_id}. Error code: {dxl_comm_result}")
    elif dxl_error != 0:
        print(f"Error in enabling torque for ID {dxl_id}: {dxl_error}")
    else:
        print(f"Torque enabled for Dynamixel ID: {dxl_id}")

def set_torque_limit(dxl_id, torque_limit):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_LIMIT, torque_limit)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set torque limit for ID {dxl_id}. Error code: {dxl_comm_result}")
    elif dxl_error != 0:
        print(f"Error in setting torque limit for ID {dxl_id}: {dxl_error}")
    else:
        print(f"Set torque limit to {torque_limit} for Dynamixel ID: {dxl_id}")

def disable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to disable torque for ID {dxl_id}. Error code: {dxl_comm_result}")
    elif dxl_error != 0:
        print(f"Error in disabling torque for ID {dxl_id}: {dxl_error}")
    else:
        print(f"Torque disabled for Dynamixel ID: {dxl_id}")

def set_goal_position(dxl_id, goal_position):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal position for ID {dxl_id}. Error code: {dxl_comm_result}")
    elif dxl_error != 0:
        print(f"Error in setting goal position for ID {dxl_id}: {dxl_error}")

def read_present_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to read present position for ID {dxl_id}. Error code: {dxl_comm_result}")
    elif dxl_error != 0:
        print(f"Error in reading present position for ID {dxl_id}: {dxl_error}")
    return dxl_present_position

def close_port():
    portHandler.closePort()

def main():
    open_port()
    set_baudrate()

    # Enable torque and set torque limits for all motors
    for dxl_id in DXL_IDS:
        enable_torque(dxl_id)
        set_torque_limit(dxl_id, TORQUE_LIMIT)

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
            print(f"[ID:{dxl_id:03d}] GoalPos:{goal_position:03d}  PresPos:{present_position:03d}")

        # Check if all motors have reached their goal positions within a tolerance
        if all(abs(goal_position - read_present_position(dxl_id)) <= 20 for dxl_id, goal_position in zip(DXL_IDS, [GOAL_POSITION_2560, GOAL_POSITION_1536] * 3)):
            break

        time.sleep(0.1)

    # Disable torque for all motors
    for dxl_id in DXL_IDS:
        disable_torque(dxl_id)

    close_port()

if __name__ == "__main__":
    main()
