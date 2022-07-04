# Nelson Dane

# Build from alpine to keep the image small
FROM alpine:latest
# Set default timezone
ENV TZ=America/New_York

# Install python, pip, and tzdata
RUN apk add --no-cache py3-pip tzdata

# Grab needed files
WORKDIR /app
COPY ./requirements.txt .
COPY ./replies.py .
COPY ./cashapp.py .

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python3","cashapp.py"]

