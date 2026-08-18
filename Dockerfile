FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    curl \
    unzip \
    jq \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

RUN bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

RUN pip3 install flask

COPY . /app
WORKDIR /app

RUN chmod +x start.sh

CMD ["./start.sh"]
