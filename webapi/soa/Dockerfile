FROM python:3
COPY . /soa
WORKDIR soa
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD [ "python3", "run.py" ]
