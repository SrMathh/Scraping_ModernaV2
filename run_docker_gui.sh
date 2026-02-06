#!/usr/bin/env bash
set -e

# Nome da imagem que você buildou
IMAGE_NAME="scraping-voiston"

# Limpa locks antigos no host (opcional, dependendo do seu setup)
rm -f /tmp/.X99-lock

docker run --rm -it \
   --shm-size=2g \
   --ipc=host \
   -p 5900:5900 \
   -e DISPLAY=:99 \
   -v "$(pwd)":/app \
   $IMAGE_NAME \
   /bin/bash -c "
     rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
     
     # Criar o arquivo .Xauthority para evitar erros do PyAutoGUI
     touch /tmp/.Xauthority
     xauth generate :99 . trusted 2>/dev/null || true
     
     Xvfb :99 -screen 0 1920x1080x24 &
     sleep 2
     
     # Inicia o servidor VNC com a senha 1234 definida no seu Dockerfile
     x11vnc -display :99 -rfbport 5900 -forever -shared -bg -nopw
     
     echo 'VNC iniciado na porta 5900. Conecte-se agora!'
     
     # Roda o seu script principal
     python3 src/main.py
   "