FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libglib2.0-0
RUN apt-get install -y wget ca-certificates gnupg2
RUN apt-get install -y postgresql postgresql-contrib
RUN apt-get install -y gcc libc-dev musl-dev build-essential python-psycopg2
COPY ./requirements.txt /requirements.txt
RUN apt install -y zlib1g-dev libjpeg-dev libpq-dev
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY ./wait-for /bin/wait-for

# -p for subdirectories
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN mkdir /app/propefy/static
RUN useradd user
RUN chown -R user:user /vol/
RUN chown -R user:user /bin/wait-for
RUN python3 manage.py collectstatic --no-input
RUN chmod -R 755 /vol/web
RUN chmod -R 755 /vol/web/static
RUN chmod -R 755 /bin/wait-for
USER user
EXPOSE 8000