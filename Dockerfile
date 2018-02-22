FROM python:3-onbuild

CMD ["python", "server.py"]

EXPOSE 9999:9999/udp