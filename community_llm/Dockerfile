FROM python:3.11-slim

WORKDIR /app

# Install PyTorch and transformers
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers datasets accelerate peft

COPY train_agent.py .
ENV COORDINATOR_URL=http://coordinator:8000
ENV MODEL_NAME=Qwen/Qwen2.5-2B-Instruct

CMD ["python", "train_agent.py"]
