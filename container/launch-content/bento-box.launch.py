import os
import yaml

from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace, ROSTimer

from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.substitutions import EnvironmentVariable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    robot_namespace = LaunchConfiguration('robot_namespace')

    diagnostics = Node(
        package='bento_diagnostics',
        executable='bento_diagnostics_node',
        name='bento_diagnostics',
        parameters=[
            {"publish_rate": 1000},
            {"config_file": PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'diagnostics', 'diagnostics_config.yaml'])},
        ],
        output='screen',
        emulate_tty=True,
    )

    aggregator = Node(
        package='diagnostic_aggregator',
        executable='aggregator_node',
        parameters=[PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'diagnostics', 'aggregator_analysers.yaml'])],
        output='screen',
    )

    bento_drive = Node(
        package='bento_drive',
        executable='bento_drive_node',
        name='bento_drive_node',
        parameters=[ PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'bento-box.yaml' ]) ],
        remappings=[('odom', '/odom' ), ('pose', '/pose')],
        output='screen',
	emulate_tty=True,
    )

    # There is some bug in bento_drive,
    # where the motorcontrollers de-enable without an eduart power-management board sending something.
    # Bento-Box has no such board, so we just send the 'important' thing the board would send
    # (I think it is a voltage readout, because bento_drive complains about undervoltage)
    can_fix = ExecuteProcess(
        cmd=[['while true; do cansend can0 580#0241AD347300; sleep 1; done']],
        shell=True,
    )

    joystick = Node(
        package='joy_linux',
        executable='joy_linux_node',
    )

    camera_ros_1 = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera_node_1',
        parameters=[ PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'camera_ros-1.yaml' ]) ],
        namespace="cam1",
        emulate_tty=True,
    )

    camera_ros_2 = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera_node_2',
        parameters=[ PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'camera_ros-2.yaml' ]) ],
        namespace="cam2",
        emulate_tty=True,
    )

    lidar = Node(
        name='rplidar_composition',
        package='rplidar_ros',
        executable='rplidar_composition',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'serial_port': '/dev/ttyUSB0',
            'serial_baudrate': 115200,  # A1 / A2
            # 'serial_baudrate': 256000, # A3
            'frame_id': 'laser_frame',
            'inverted': False,
            'angle_compensate': True,
            'use_sim_time' : True,
        }],
    )

    robot_model = IncludeLaunchDescription(
        PathJoinSubstitution([ '.', 'xacro-robot-description.launch.py' ]),
        launch_arguments={
            'model': PathJoinSubstitution([ '/', 'launch-content', 'parameters', 'bento-box-neo.urdf' ]),
        }.items()
    )

    slam = IncludeLaunchDescription(
        PathJoinSubstitution([ '.', 'bento_slam.launch.py' ]),
        launch_arguments={
            'robot_namespace': robot_namespace,
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace',
            default_value='bento',
            description='set namespace for robot nodes'
        ),
        # start diagnostics before everything else
        diagnostics,
        aggregator,
        # and give it a 3-second head start to initialize
        ROSTimer(
            period=3.0,
            actions=[
                PushRosNamespace(robot_namespace),
                joystick,
                camera_ros_1,
                camera_ros_2,
                bento_drive,
            ]),
        lidar,
#        slam,  # already namespaced
        can_fix,
        robot_model,
    ])
