FROM python:3.11

WORKDIR /

RUN pip install black[d]

EXPOSE 9090
CMD ["blackd", "--bind-host", "0.0.0.0", "--bind-port", "9090"]
