FROM cgr.dev/chainguard/python:latest-dev as builder

RUN pip install webssh --user

FROM cgr.dev/chainguard/python:latest

WORKDIR /app

COPY --from=builder /home/nonroot/.local/lib/python3.12/site-packages /home/nonroot/.local/lib/python3.12/site-packages
COPY --from=builder /home/nonroot/.local/bin /home/nonroot/.local/bin

# Adding the directory containing wssh to PATH
ENV PATH="/home/nonroot/.local/bin:${PATH}"

ENTRYPOINT ["wssh", "--fbidhttp=False", "--address=0.0.0.0", "--port=8888"]