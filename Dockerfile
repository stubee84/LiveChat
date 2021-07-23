FROM --platform=arm64 debian

COPY frontend/ /opt/LiveChat/frontend
COPY livechatapp/ /opt/LiveChat/livechatapp
COPY LiveChat/ /opt/LiveChat/LiveChat
COPY manage.py /opt/LiveChat/
COPY db.sqlite3 /opt/LiveChat/
COPY pytest.ini /opt/LiveChat/
COPY requirements.txt /opt/LiveChat/
COPY *.json /opt/LiveChat/

WORKDIR /opt/LiveChat/

RUN sudo apt update && sudo apt upgrade && sudo apt install nano
RUN sudo apt install python3 python3-pip
RUN sudo apt install nodejs npm