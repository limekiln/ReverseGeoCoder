FROM python:3
ADD GeoCoder.py /
RUN pip install locationiq
ENTRYPOINT ["python", "GeoCoder.py"]
