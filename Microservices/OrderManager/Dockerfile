FROM python:3.10

RUN apt-get update && apt-get install -y vim nano lsb-release apt-utils
RUN python3 -m pip install -U pip==22.2.1

COPY . /app

RUN pip3 install /app/wheels/* && pip3 install -r /app/requirements.txt

CMD ["python3.10", "/usr/local/lib/python3.10/site-packages/order_manager/main.py"]
