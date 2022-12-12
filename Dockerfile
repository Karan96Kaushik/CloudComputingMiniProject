FROM python:3
ADD app.py /
ADD *.py /
ADD models/*.py /
ADD requirements.txt /
ADD templates/*.html /
ADD .env /
EXPOSE 5000
RUN pip install -r requirements.txt
CMD [ "python", "./app.py" ]
