FROM debian:bookworm-slim

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential libssl-dev libffi-dev \
    curl systemd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama client
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and startup script
COPY src/ /app/
COPY Modelfile .
COPY ollama-setup.sh /ollama-setup.sh
RUN chmod +x /ollama-setup.sh

# Expose port 8000 for prompt service
EXPOSE 8000

CMD ["/ollama-setup.sh"]
