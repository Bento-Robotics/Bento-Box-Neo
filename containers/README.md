# Bento-Box container
*This directory contains source and configuration files of Bento-Box's container subsystem.*  
The use of containers drastically reduces fault recovery time (for instance a dead SD card or software crash),  
and automates many tasks for us (such as programmatically setting up/configuring software and starting containers on boot).

> Containers are like faster virtual machines, which you can configure using a `compose.yml` file, telling it what hardware and files to access.  
> Images are like read-only hard-drives for containers. You can always delete a container and create a new, identical one from the same Image.


## Important commands
`docker restart bento-box-ros` - restart the container (software crash, hardware glitch, etc)  
`docker start bento-box-ros` - forcibly start container (if autostart were to fail)  
`docker ps` - list running containers  
`docker ps -a` - list all containers  
`docker images` - list all images  
`docker logs --since 2m bento-box-ros` - show container logs of last 2 minutes (see what exactly crashed)  
ℹ️📂 `cd xx/Bento-Box/container` - go to this here folder, **needed for all `docker compose xx` commands!**  
👉📁 `docker compose down` - shut down and delete container (clean up, disables autostart)  
👉📁 `docker compose restart` - restart the container (same as `docker restart`)  
👉📁 `docker compose up` - set up and start container (use after `docker compose down`, enables autostart)  


## Installation
> Building the container image will download (compressed) ∼281MB (ros2 image), ∼400MB of packages, and in total use ∼4GB of storage.  
> **Internet connection required**

> ℹ️ If you are setting up Bento-Box from scratch, follow the installation guide at [system-files/README.md](../system-files/README.md).  
> This here is only for the container system.

```shell
# Set up Docker & tools we'll need
sudo apt update
sudo apt install docker.io docker-compose-v2 git -y
sudo usermod -aG $USER docker
sudo reboot

# (Set up this Repo and) Build image and start container
#git clone https://github.com/Bento-Robotics/Bento-Box.git
cd Bento-Box/container
docker compose up -d  # if it can't find ros:jazzy, retry after doing `docker pull docker.io/library/ros:jazzy`
```

### Alternative for low-spec or offline bots
> For when your robot is too weak to build an image (for instance a pi zero), or there is no way of connecting it to the Internet.

**Example: building an Image for a arm64 robot (raspberry pi):**
```shell
# On PC
cd xx/Bento-Box/container/build/
docker build --arch=arm64 --tag bento-box:jazzy-arm .
docker image save -o bento-box_jazzy-arm.tar bento-box:jazzy-arm

# Transfer file over ssh (any kind of file transfer will do)
scp bento-box_jazzy-arm.tar 192.168.robot.ip:~/

# On Robot
docker image load -i bento-box_jazzy-arm.tar
docker images  # Image should now show up in list
```


## Configuring
> Containers run one file / line of bash, and shut down if it ends.

### What the container runs
Last line in `compose.yml`:
```yml
command: 'ros2 launch bento-box.launch.py robot_namespace:="bento_box"'
```

Example for doing multiple things:
```yml
command: bash -c 'while true; do cansend can0 580#0241AD347300; sleep 1; done&  ros2 launch bento-box.launch.py robot_namespace:="bento_box"''
```

### What ROS runs
Everything in [bento-box.launch.py](./launch-content/bento-box.launch.py)

Parameter files of the individual Nodes started by said launch file are under [launch-content/parameters](./launch-content/parameters/)
