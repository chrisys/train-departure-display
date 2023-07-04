FROM balenalib/raspberry-pi-alpine-python:3.11.2-3.15-build as builder

WORKDIR /usr/src/app

# Shared libraries
RUN apk add freetype-dev libjpeg-turbo-dev

# Install the required python packages, and save the compiled result to an output folder
# This requires gcc/etc which is why we do it in the build image and save the result for the run image
COPY ./requirements.txt .
RUN pip install --target=/usr/src/python-packages -r requirements.txt --no-cache-dir --config-settings="pillow=--disable-zlib"

# Grab the "run" image for the device, which is much lighter weight
FROM balenalib/raspberry-pi-alpine-python:3.11.2-3.15-run

# Copy in the compiled packages
COPY --from=builder /usr/src/python-packages/ /usr/src/python-packages/

# Shared libraries
RUN apk add freetype-dev libjpeg-turbo-dev tzdata

# And the app
WORKDIR /usr/src/app
COPY src ./src
COPY VERSION .

# Tell python where to find these mysterious precompiled packages
ENV PYTHONPATH=/usr/src/python-packages

# And off we go
CMD ["python3", "src/main.py"]
