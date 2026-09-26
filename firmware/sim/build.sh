#!/bin/sh
# Build the robot simulator around the real mouse_map.ino.
# arduino_proto.py adds function prototypes the way the Arduino IDE does, so a
# sketch that only compiles thanks to that (or fails because of it) behaves the same here.
set -e
cd "$(dirname "$0")"
mkdir -p build
python3 arduino_proto.py ../mouse_map/mouse_map.ino build/mouse_map_proto.cpp
g++ -std=gnu++17 -O2 -Wall -Wno-unused -Ifakehw -I../mouse_map \
    -DMOUSE_SKETCH='"build/mouse_map_proto.cpp"' robot_sim.cpp -o build/robot_sim
echo "built build/robot_sim"
