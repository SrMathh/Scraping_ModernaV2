#!/usr/bin/env bash
set -e

# limpa locks antigos no host
rm -f /tmp/.X99-lock

 docker run --rm -it \
   -u "$(id -u):$(id -g)" \
   --shm-size=6g --ipc=host \
   -e DISPLAY=:99 \
   -e WDM_LOCAL=1 \
   -e HOME=/tmp \
   -v "$(pwd)":/app \
   scraping-voiston \
   /bin/bash -c '\
     rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
     mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix
     touch /tmp/.Xauthority && export XAUTHORITY=/tmp/.Xauthority

     Xvfb :99 -screen 0 1920x1080x24 & XVFB_PID=$!
     sleep 2
     export DISPLAY=:99

     python3 src/scheduler.py
     kill $XVFB_PID
   '
