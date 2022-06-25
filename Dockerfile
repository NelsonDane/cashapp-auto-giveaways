# Nelson Dane

# Build from alpine to keep the image small
FROM alpine:latest

# Install python and pip
RUN apk add --no-cache py3-pip

# Grab needed files
WORKDIR /app
COPY ./requirements.txt .
COPY replies.py .
COPY searches.py .
COPY ./cashapp.py .

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python3","cashapp.py"]

