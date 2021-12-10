FROM balenalib/raspberry-pi-debian-python:3.7-buster-run AS builder

WORKDIR /usr/src/app

RUN mkdir -p /usr/src/debian-rootfs

RUN install_packages apt-rdepends

RUN apt-get update && \
        apt-get download \
        $(apt-rdepends tzdata python3 libopenjp2-7 libfreetype6-dev libjpeg-dev libtiff5 libxcb1 | grep -v "^ " | sed 's/debconf-2.0/debconf/g' | sed 's/^libc-dev$/libc6-dev/g' | sed 's/^libz-dev$/zlib1g-dev/g')

RUN for pkg in *.deb; \
      do dpkg-deb  -x $pkg /usr/src/debian-rootfs; \
      done

COPY ./requirements.txt .
RUN pip install -t /usr/src/python-packages -r requirements.txt --no-cache-dir --extra-index-url=https://www.piwheels.org/simple


FROM busybox:stable


COPY --from=builder /usr/src/debian-rootfs ./
COPY --from=builder /usr/src/python-packages/ /usr/src/python-packages/

COPY VERSION ./

COPY src ./src
ENV PYTHONPATH=/usr/src/python-packages/

CMD ["python3", "src/main.py"]