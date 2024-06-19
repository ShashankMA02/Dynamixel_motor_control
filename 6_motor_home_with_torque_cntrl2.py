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

# Goal positions (2048 for all motors)
GOAL_POSITION = 2048

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

    try:
        while True:
            # Set goal positions continuously to 2048 for all motors
            for dxl_id in DXL_IDS:
                set_goal_position(dxl_id, GOAL_POSITION)

            # Read and print present positions
            for dxl_id in DXL_IDS:
                present_position = read_present_position(dxl_id)
                print(f"[ID:{dxl_id:03d}] GoalPos:{GOAL_POSITION:03d}  PresPos:{present_position:03d}")

            # Pause briefly before the next iteration
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrupted by user")

    finally:
        # Disable torque for all motors
        for dxl_id in DXL_IDS:
            disable_torque(dxl_id)

        close_port()

if __name__ == "__main__":
    main()
