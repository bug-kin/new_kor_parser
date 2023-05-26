FROM python:3.10.6-slim-buster
RUN groupadd --gid 1000 node && useradd --uid 1000 --gid node --shell /bin/bash --create-home node
USER node
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD [ "python", "kbchachacha.py" ]
