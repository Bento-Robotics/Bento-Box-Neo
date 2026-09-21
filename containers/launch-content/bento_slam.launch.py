from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode

from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    robot_namespace = LaunchConfiguration('robot_namespace')

    rf2o_odom = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        # no name because rf2o is weird and registers 2 Nodes
        parameters=[
            { PathJoinSubstitution([ '.', 'parameters', 'slam', 'rf2o_laser_odometry.yaml' ]) },
            { 'laser_scan_topic': PathJoinSubstitution([ '/', robot_namespace, 'scan' ]) },
#            { 'base_frame_id': PathJoinSubstitution([ '/', 'base_footprint' ]) },
#            { 'odom_frame_id': PathJoinSubstitution([ '/', 'odom' ]) },
        ],
        arguments=['--ros-args', '--log-level', 'warn'],
        output='screen',
        emulate_tty=True,
    )

    slam_toolbox = IncludeLaunchDescription(
        PathJoinSubstitution([ '.', 'slamtoolbox-online_async.launch.py' ]),
        launch_arguments={
            'autostart': 'true',
            'use_lifecycle_manager': 'false',
            'slam_params_file': PathJoinSubstitution([ '.', 'parameters', 'slam', 'slam_toolbox.yaml' ]),
            'use_sim_time': 'false',
            'namespace': robot_namespace,
        }.items()
    )

    tf_map_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", "map",  #PathJoinSubstitution([ robot_namespace, 'map' ]),
            "--child-frame-id", "odom",  #PathJoinSubstitution([ robot_namespace, 'odom' ])
        ],
        #remappings=[('/tf','tf'),('/tf_static','tf_static')],
        output="screen",
        emulate_tty=True,
    )

    tf_odom_basefootprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_base_footprint_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", PathJoinSubstitution([ robot_namespace, 'odom' ]),
            "--child-frame-id", PathJoinSubstitution([ robot_namespace, 'base_footprint' ])
        ],
        #remappings=[('/tf','tf'),('/tf_static','tf_static')],
        output="screen",
        emulate_tty=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace',
            default_value='bento',
            description='set namespace for robot nodes'
        ),
        tf_map_odom,
        #tf_odom_basefootprint,

        rf2o_odom,
        slam_toolbox
    ])
