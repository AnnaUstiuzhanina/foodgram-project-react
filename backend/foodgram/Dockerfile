FROM python:3.9.5 
 
WORKDIR /code 
 
COPY requirements.txt . 
 
RUN pip3 install -r requirements.txt 

COPY . .

CMD python manage.py collectstatic
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
