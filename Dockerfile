FROM python:3
ADD GeoCoder.py /
RUN pip install locationiq
RUN pip install python-dotenv
ENTRYPOINT ["python", "GeoCoder.py"]
