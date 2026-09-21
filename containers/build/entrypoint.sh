#!/bin/bash

# Set up ros2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash" --

# Source compiled packages
source "/bento_ws/install/setup.bash" --

exec "$@"
