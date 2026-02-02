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
        name='rf2o_laser_odometry',
        parameters=[
            { PathJoinSubstitution([ './', 'parameters', 'slam', 'rf2o_laser_odometry.yaml' ]) },
            { 'base_frame_id': PathJoinSubstitution([ robot_namespace, 'base_footprint' ]) },
            { 'odom_frame_id': PathJoinSubstitution([ robot_namespace, 'odom' ]) },
        ],
        arguments=['--ros-args', '--log-level', 'warn'],
        output='screen',
        emulate_tty=True,
    )

    slam_toolbox = IncludeLaunchDescription(
        PathJoinSubstitution([ './', 'slam_toolbox-online_async_namespaced.launch.py']),
        launch_arguments={
            'autostart' : 'true',
            'use_lifecycle_manager'  : 'false',
            'slam_params_file' : PathJoinSubstitution([ './', 'parameters', 'slam', 'slam_toolbox.yaml' ]),
            'use_sim_time' : 'true',
            'namespace' : robot_namespace,
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
            "--frame-id", PathJoinSubstitution([ robot_namespace, 'map' ]),
            "--child-frame-id", PathJoinSubstitution([ robot_namespace, 'odom' ])
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

    tf_basefootprint_baselink = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_base_link_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", PathJoinSubstitution([ robot_namespace, 'base_footprint' ]),
            "--child-frame-id", PathJoinSubstitution([ robot_namespace, 'base_link' ])
        ],
        #remappings=[('/tf','tf'),('/tf_static','tf_static')],
        output="screen",
        emulate_tty=True,
    )

    # LiDAR TF
    tf_baselink_laser = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_laserframe_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", PathJoinSubstitution([ robot_namespace, 'base_link' ]),
            "--child-frame-id", PathJoinSubstitution([ robot_namespace, 'laser_frame' ])
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
        GroupAction(
            actions=[
                PushRosNamespace(robot_namespace),
                rf2o_odom,

                #tf_map_odom,
                #tf_odom_basefootprint,
                tf_basefootprint_baselink,
                tf_baselink_laser,
            ]),
        slam_toolbox,
    ])
