#!/usr/bin/env python3
from svan_simple_control_msgs.msg import SvanCommand
from std_msgs.msg import Float32MultiArray
import rospy

rospy.init_node('svan_simple_control_node')

command_publisher = rospy.Publisher('/svan/io_interface',Float32MultiArray,queue_size=1)

current_operation_mode = SvanCommand.MODE_STOP
current_key_data = Float32MultiArray()
current_key_data.data = [0] * 9

def constrain_value(value,minumum: float = -1.0,maximum: float = 1.0):
    return max(minumum, min(value, maximum))


def set_operation_mode(mode: int):
    global current_operation_mode, current_key_data, command_publisher
    current_key_data.data = [0] * 9
    if mode == SvanCommand.MODE_TROT:
        rospy.loginfo("Trot Mode")
        current_operation_mode = SvanCommand.MODE_TROT
        current_key_data.data[0] = 4.0
    elif mode == SvanCommand.MODE_PUSHUP:
        rospy.loginfo("Pushup Mode")
        current_operation_mode = SvanCommand.MODE_PUSHUP
        current_key_data.data[0] = 3.0
    elif mode == SvanCommand.MODE_TWIRL:
        rospy.loginfo("Twirl Mode")
        current_operation_mode = SvanCommand.MODE_TWIRL
        current_key_data.data[0] = 2.0
    elif mode == SvanCommand.MODE_STOP:
        rospy.loginfo("Stop Mode")
        current_operation_mode = SvanCommand.MODE_STOP
        current_key_data.data[0] = 1.0
    elif mode == SvanCommand.MODE_SLEEP:
        rospy.loginfo("Sleep Mode")
        current_operation_mode = SvanCommand.MODE_SLEEP
        current_key_data.data[0] = 6.0

    command_publisher.publish(current_key_data)

def set_velocity(vel_x: float = 0.0, vel_y: float = 0.0):
    global current_operation_mode, current_key_data
    if vel_x == 0.0 and vel_y == 0.0:
        if current_operation_mode == SvanCommand.MODE_TROT:
            set_operation_mode(SvanCommand.MODE_STOP)
        return

    if current_operation_mode != SvanCommand.MODE_TROT:
        set_operation_mode(SvanCommand.MODE_TROT)
    
    vel_x = constrain_value(vel_x)
    vel_y = constrain_value(vel_y)
    current_key_data.data[1] = vel_x
    current_key_data.data[2] = vel_y
    command_publisher.publish(current_key_data)

def set_roll(magnitude: float):
    global current_key_data
    magnitude = constrain_value(magnitude)
    current_key_data.data[3] = magnitude
    command_publisher.publish(current_key_data)

def set_pitch(magnitude: float):
    global current_key_data
    magnitude = constrain_value(magnitude)
    current_key_data.data[4] = magnitude
    command_publisher.publish(current_key_data)

def set_yaw(direction: int = SvanCommand.YAW_NONE):
    global current_key_data
    if direction == SvanCommand.YAW_NONE and current_key_data.data[5] != 0:
        current_key_data.data[5] = 0
        command_publisher.publish(current_key_data)
    
    elif direction == SvanCommand.YAW_RIGHT and current_key_data.data[5] != -1.0:
        current_key_data.data[5] = -1.0
        command_publisher.publish(current_key_data)
    
    elif direction == SvanCommand.YAW_RIGHT and current_key_data.data[5] != 1.0:
        current_key_data.data[5] = 1.0
        command_publisher.publish(current_key_data)

def set_height(state: int):
    global current_key_data
    
    if state == SvanCommand.HEIGHT_UP and current_key_data.data[8] != 1:
        current_key_data.data[8] = 1
        command_publisher.publish(current_key_data)
    
    elif state == SvanCommand.HEIGHT_DOWN and current_key_data.data[8] != -1:
        current_key_data.data[8] = -1
        command_publisher.publish(current_key_data)

def handle_new_command(command: SvanCommand):
    rospy.loginfo(f"Recieved Command: {command}")

    # operation mode
    if command.command_type == SvanCommand.COMMAND_OPERATION_MODE:
        rospy.loginfo(f"Setting operation mode to {command.operation_mode}")
        set_operation_mode(mode=command.operation_mode)

    # linear movement
    elif command.command_type == SvanCommand.COMMAND_MOVEMENT:
        rospy.loginfo(f"Setting Velocity: Vel_X: {command.vel_x} Vel_Y: {command.vel_y}")
        set_velocity(vel_x=command.vel_x,vel_y=command.vel_y)

    # vertical height
    elif command.command_type == SvanCommand.COMMAND_HEIGHT:
        rospy.loginfo(f"Setting height to {command.height}")
        set_height(state=command.height)
    
    # roll 
    elif command.command_type == SvanCommand.COMMAND_ROLL:
        rospy.loginfo(f"Setting roll to {command.roll}")
        set_roll(magnitude=command.roll)

    # pitch
    elif command.command_type == SvanCommand.COMMAND_PITCH:
        rospy.loginfo(f"Setting pitch to {command.pitch}")
        set_pitch(magnitude=command.pitch)

    # yaw
    elif command.command_type == SvanCommand.COMMAND_YAW:
        rospy.loginfo(f"Setting yaw to {command.yaw}")
        set_yaw(direction=command.yaw)

rospy.Subscriber('/svan/simple_control',SvanCommand,handle_new_command)

if __name__ == '__main__':
    try:
        rospy.loginfo("READY")
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
