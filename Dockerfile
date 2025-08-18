FROM python:3.11 as requirements-stage

WORKDIR /tmp

FROM python:3.11

WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .

ENTRYPOINT ["sh", "./scripts/launch_prod.sh"]
