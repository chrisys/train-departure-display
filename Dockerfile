FROM python:3.13-slim-bookworm as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential

WORKDIR /usr/src/app

# Install the required python packages, and save the compiled result to an output folder
# This requires gcc/etc which is why we do it in the build image and save the result for the run image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim-bookworm

# Copy in the compiled packages
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

WORKDIR /usr/src/app
COPY src ./src
COPY VERSION .

CMD ["python3", "src/main.py"]