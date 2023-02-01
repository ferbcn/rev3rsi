# pull official base image
FROM python:3.10.8-alpine

# set work directory
WORKDIR /usr/src/rev3rsi

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
#COPY mysite .
#COPY reversi .
#COPY staticfiles .

#RUN python manage.py collectstatic --noinput

COPY mysite mysite
COPY reversi reversi
COPY staticfiles staticfiles

CMD ["gunicorn", "--bind", ":80", "--workers", "4", "mysite.wsgi:application"]