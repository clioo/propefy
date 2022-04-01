FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install -y libgl1-mesa-glx libglib2.0-0
RUN apt-get install -y wget ca-certificates gnupg2
RUN apt-get install -y postgresql postgresql-contrib
RUN apt-get install -y gcc libc-dev musl-dev build-essential python3-psycopg2
COPY ./requirements.txt /requirements.txt
RUN apt-get update -y --allow-releaseinfo-change
RUN apt-get install -y zlib1g-dev libjpeg-dev libpq-dev
RUN apt-get install -y binutils
RUN apt-get install -y libproj-dev
RUN apt-get install -y zlib1g-dev
RUN apt-get install -y gdal-bin
RUN apt-get install -y libgdal-dev
RUN apt-get install -y g++
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY ./wait-for /bin/wait-for

# -p for subdirectories
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN useradd user
RUN mkdir /app/propefy/static
RUN chown -R user:user /vol/
RUN chown -R user:user /bin/wait-for
RUN python3 manage.py collectstatic --no-input
RUN chmod -R 755 /vol/web
RUN chmod -R 755 /vol/web/static
RUN chmod -R 755 /bin/wait-for
USER user
EXPOSE 8000
