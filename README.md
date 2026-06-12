# 🚨 ROS2 기반 TurtleBot3 비상구 및 대피로 차단 점검 로봇

## 팀 정보

| 항목 | 내용 |
|------|------|
| 팀명 | 올라프 |
| 팀원 | 김현영 |
| 학번 | 2371023 |


---

## 프로젝트 소개

ROS2 + Gazebo 시뮬레이션 환경에서 TurtleBot3 Waffle Pi를 이용해 실내 복도의 **비상구·대피로 차단 여부를 자동으로 점검**하는 로봇 시스템입니다.

LiDAR 센서 데이터를 기반으로 전방 장애물을 감지하며, 일시적 감지가 아닌 **지속 감지 기반**으로 위험을 확정하여 오탐을 최소화합니다.

```
EXIT_1 출발 → CENTER 점검(NORMAL) → EXIT_2 이동 → 장애물 지속 감지 → CONFIRMED_DANGER → 정지
```

---

## 개발 환경

| Category | Technology |
|----------|------------|
| OS | Ubuntu 22.04 LTS |
| ROS | ROS2 Humble |
| Simulator | Gazebo Classic |
| Robot | TurtleBot3 Waffle Pi |
| Language | Python |
| Visualization | RViz2 |
| Sensor | LiDAR `/scan` |

---

## 주요 기능

- **구역 기반 자동 순찰** — 지정 점검 구역에서만 장애물 판단 활성화
- **지속 감지 기반 위험 확정** — 일시 감지는 `CANDIDATE`, 일정 시간 지속 시 `CONFIRMED_DANGER`로 확정
- **RViz Marker 시각화** — 상태별 색상(Blue/Green/Yellow/Orange/Red)으로 직관적 확인

---

## 패키지 구조

```
exit_patrol_robot/
├── exit_patrol_robot/
│   ├── __init__.py
│   ├── scan_blockage_judge.py     # LiDAR 기반 장애물 판단
│   ├── inspection_visualizer.py   # RViz Marker 시각화
│   ├── corridor_patrol.py         # 자동 순찰 제어
│   └── simple_patrol.py
├── launch/
│   └── inspection.launch.py
├── worlds/
│   ├── exit_corridor.world
│   └── exit_corridor_obstacle.world
├── maps/
│   ├── exit_corridor_map.yaml
│   └── exit_corridor_map.pgm
├── config/
│   └── nav2_params.yaml
├── package.xml
└── setup.py
```

---

## 실행 방법

### 1. 빌드

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select exit_patrol_robot --symlink-install
source install/setup.bash
```

### 2. Gazebo 실행

```bash
export TURTLEBOT3_MODEL=waffle_pi
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models

LIBGL_ALWAYS_SOFTWARE=1 gzserver --verbose \
  -s libgazebo_ros_init.so -s libgazebo_ros_factory.so \
  ~/ros2_ws/src/exit_patrol_robot/worlds/exit_corridor_obstacle.world
```

### 3. 로봇 스폰

```bash
ros2 run gazebo_ros spawn_entity.py \
  -entity waffle_pi \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf \
  -x -2.55 -y 0.00 -z 0.05 -Y 0.0
```

### 4. 점검 시스템 실행

```bash
ros2 launch exit_patrol_robot inspection.launch.py
```

### 5. 상태 확인

```bash
ros2 topic echo /exit_patrol/blockage_state
ros2 topic echo /exit_patrol/current_zone
```

---

## 데모 영상

[![YouTube](https://img.shields.io/badge/YouTube-Demo-red?logo=youtube)](유튜브_링크_입력)

---

## AI 사용 여부

- 디버깅 보조
- README 문서 초안 작성 보조

---

## 참고 자료

- [ROBOTIS TurtleBot3 e-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)
- [TurtleBot3 Simulation (ROS2 Humble)](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/)
- [ROBOTIS-GIT/turtlebot3 (GitHub)](https://github.com/ROBOTIS-GIT/turtlebot3/tree/humble)
- [ROS2 Humble 공식 문서](https://docs.ros.org/en/humble/)
