# Base image Python
FROM python:3.10-slim

# Instalar dependências do sistema para o X11 e Selenium
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libx11-dev \
    libxcomposite1 \
    libxrandr2 \
    libgtk2.0-0 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    xauth \
    xvfb \
    x11vnc \
    wget \
    gnupg \
    fonts-liberation \
    ffmpeg \
    x264 \
    libx264-dev \
    libcurl4 \
    libcurl3-gnutls \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libvulkan1 \
    xdg-utils \
    gnome-screenshot \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*
# Instalar o Google Chrome (versão estável)
RUN wget -O /tmp/google-chrome-stable_135.0.7049.52-1_amd64.deb \
        https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_135.0.7049.52-1_amd64.deb && \
    dpkg -i /tmp/google-chrome-stable_135.0.7049.52-1_amd64.deb || apt-get install -f -y && \
    rm /tmp/google-chrome-stable_135.0.7049.52-1_amd64.deb

# 2) Impede futuras atualizações automáticas do Chrome
RUN apt-mark hold google-chrome-stable

# Instalar dependências Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar o código do projeto
COPY . .
WORKDIR /app
# Configuração do Xvfb e VNC
RUN mkdir /root/.vnc && \
    x11vnc -storepasswd 1234 /root/.vnc/passwd

# Configurar o ambiente
ENV DISPLAY=:99
ENV WDM_LOCAL=1
ENV HOME=/tmp

# Comando padrão
RUN chmod +x run_docker_gui.sh