ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        aiohttp \
        voluptuous

# Copy data
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ] 