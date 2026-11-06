ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER 0:0
RUN python -m pip install --no-cache-dir inspect-tool-support==1.2.0 \
    && chown -R 1000:1000 /testbed
COPY --chmod=755 inspect-sandbox-tools /var/tmp/.da7be258e003d428/inspect-sandbox-tools
ENV HOME=/tmp PIP_NO_INDEX=1 PIP_DISABLE_PIP_VERSION_CHECK=1
USER 1000:1000
