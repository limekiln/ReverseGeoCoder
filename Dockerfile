FROM python:3
ADD GeoCoder.py /
RUN pip install locationiq
CMD ["python", "GeoCoder.py"]
