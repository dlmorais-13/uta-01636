FROM nhtrung/dcai

RUN apt-get update -y && apt-get install vim -y
COPY rundc.py /app/rundc.py

