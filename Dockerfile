FROM python:3.11.9

WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .

ENTRYPOINT python main.py
