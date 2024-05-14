FROM python:3.11.9

WORKDIR /usr/src/app
COPY . .
RUN python -m pip install -r requirements.txt

ENTRYPOINT python main.py
