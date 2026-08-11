import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/youn/ROS/open_manipulator_ws/install/open_manipulator_teleop'
