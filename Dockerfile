FROM python:3.12-alpine3.22 as builder

RUN apk add --no-cache \
        freetype-dev \
        libjpeg-turbo-dev \
        gcc \
        musl-dev \
        linux-headers 

WORKDIR /usr/src/app

# Install the required python packages, and save the compiled result to an output folder
# This requires gcc/etc which is why we do it in the build image and save the result for the run image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine3.22

RUN apk add --no-cache \
        freetype-dev \
        libjpeg-turbo-dev \
        tzdata

# Copy in the compiled packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

WORKDIR /usr/src/app
COPY src ./src
COPY version.txt .

CMD ["python3", "src/main.py"]