FROM python:3
ADD app.py /
RUN pip install flask pymongo python-dotenv
CMD [ "python", "./app.py" ]
