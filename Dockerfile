FROM python:3.13-slim-bookworm as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl

WORKDIR /opt/build
WORKDIR /opt/build/ui

# Download WiFi Connect
# Use latest version. If specific version is required, it should be provided as vX.Y.Z, e.g v4.11.37
ARG VERSION="latest"

RUN \
    export BASE_URL="https://github.com/balena-os/wifi-connect/releases" &&\    
    DETECTED_ARCH=$(uname -m) &&\
    case $DETECTED_ARCH in \
        "aarch64") \
            BINARY_ARCH_NAME="aarch64-unknown-linux-gnu" ;; \
        "x86_64") \
            BINARY_ARCH_NAME="x86_64-unknown-linux-gnu" ;;\
        "armv7l") \
            BINARY_ARCH_NAME="armv7-unknown-linux-gnueabihf" ;;\
        *) \
            echo >&2 "error: unsupported architecture ($DETECTED_ARCH)"; exit 1 ;; \ 
    esac;\
    if [ ${VERSION} = "latest" ]; then \
        export URL_PARTIAL="latest/download" ; \
    else \
        export URL_PARTIAL="download/${VERSION}" ; \
    fi; \
    curl -Ls "$BASE_URL/$URL_PARTIAL/wifi-connect-$BINARY_ARCH_NAME.tar.gz" \
    | tar -xvz -C  /opt/build && \
    curl -Ls "$BASE_URL/$URL_PARTIAL/wifi-connect-ui.tar.gz" \
    | tar -xvz -C  /opt/build/ui

# Install the required python packages, and save the compiled result to an output folder
# This requires gcc/etc which is why we do it in the build image and save the result for the run image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build final stage
FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    wireless-tools \
    dnsmasq

# Copy in the compiled packages
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /opt/build /usr/src/app

WORKDIR /usr/src/app
COPY src ./src
COPY VERSION .

# For WiFi Connect
ENV DBUS_SYSTEM_BUS_ADDRESS unix:path=/host/run/dbus/system_bus_socket

CMD ["sh", "src/start.sh"]