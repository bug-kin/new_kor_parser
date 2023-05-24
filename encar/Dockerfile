FROM python:3.10.11-alpine3.18
RUN addgroup -g 1000 container_user && adduser -u 1000 -G container_user -s /bin/sh -D container_user
USER 1000
COPY . .
RUN pip install -U pip && pip install -r requirements.txt
CMD [ "python", "encar.py" ]
