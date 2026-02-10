FROM python:3.11-slim

# Install paramiko for SSH
RUN pip install --no-cache-dir paramiko

WORKDIR /app

# Copy honeypot files
COPY honeypot.py .
COPY logger.py .

# Create logs directory
RUN mkdir -p /app/logs

# Expose SSH port
EXPOSE 22

# Run honeypot
CMD ["python", "-u", "honeypot.py"]