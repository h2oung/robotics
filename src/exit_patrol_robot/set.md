# 가제보 실행

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null

LIBGL_ALWAYS_SOFTWARE=1 \
GALLIUM_DRIVER=llvmpipe \
MESA_GL_VERSION_OVERRIDE=3.3 \
GAZEBO_MODEL_DATABASE_URI="" \
GAZEBO_MODEL_PATH=/opt/ros/humble/share/turtlebot3_gazebo/models \
gazebo --verbose \
-s libgazebo_ros_init.so \
-s libgazebo_ros_factory.so \
~/ros2_ws/src/exit_patrol_robot/worlds/exit_corridor.world

# Waffle Pi 스폰
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null

export GAZEBO_MODEL_PATH=/opt/ros/humble/share/turtlebot3_gazebo/models

ros2 run gazebo_ros spawn_entity.py \
  -entity waffle_pi \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf \
  -x 0.0 -y -0.5 -z 0.01

# base_scan TF 연결
source /opt/ros/humble/setup.bash

ros2 run tf2_ros static_transform_publisher \
  -0.064 0 0.121 0 0 0 \
  base_footprint base_scan

# SLAM 실행
source /opt/ros/humble/setup.bash

ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true

# RViz 실행
source /opt/ros/humble/setup.bash

rviz2 --ros-args -p use_sim_time:=true


### 설정 
Fixed Frame: map

Add → By topic → /map → nav_msgs/msg/OccupancyGrid
Add → By topic → /scan → sensor_msgs/msg/LaserScan
Add → By display type → TF

# 로봇 조종
source /opt/ros/humble/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 지도 저장
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null

mkdir -p ~/ros2_ws/src/exit_patrol_robot/maps

ros2 run nav2_map_server map_saver_cli \
  -f ~/ros2_ws/src/exit_patrol_robot/maps/exit_corridor_map

# 지도 확인
ls -l ~/ros2_ws/src/exit_patrol_robot/maps

# 방향
z z z     속도 낮추기
l         아주 천천히 회전
k         정지
i         조금 전진
k         정지
j         반대 방향으로 천천히 회전