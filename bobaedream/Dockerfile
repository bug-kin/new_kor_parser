FROM python:3.10.11-alpine3.18
WORKDIR /parser/bobaedream
COPY . .
RUN pip install -U pip && pip install -r requirements.txt

ENTRYPOINT [ "python", "bobaedream.py" ]