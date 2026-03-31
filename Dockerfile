FROM python:3.10-slim

LABEL maintainer="chho"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY devops_tool.py .

RUN useradd -m appuser
USER appuser

ENTRYPOINT ["python3", "devops_tool.py"]
CMD ["--help"]