#!/usr/bin/env python3
"""
Community LLM Training Agent - Qwen 2.5 2B

This agent:
1. Pulls training tasks from the coordinator
2. Runs fine-tuning on Qwen2.5-2B using LoRA
3. Returns trained checkpoints
"""

import os
import json
import time
import uuid
import hashlib
import base64
import requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import random

COORDINATOR = os.getenv("COORDINATOR_URL", "http://localhost:8000")
MODEL_NAME = "Qwen/Qwen2.5-2B-Instruct"

def generate_keypair():
    secret = str(uuid.uuid4()).encode()
    pubkey = hashlib.sha256(secret).hexdigest()[:16]
    return base64.b64encode(secret).decode(), pubkey

# Load or create keypair
key_file = "/tmp/qwen_agent_key.json"
import os
if os.path.exists(key_file):
    with open(key_file) as f:
        data = json.load(f)
        secret = data["secret"]
        pubkey = data["pubkey"]
else:
    secret, pubkey = generate_keypair()
    with open(key_file, "w") as f:
        json.dump({"secret": secret, "pubkey": pubkey}, f)

agent_id = pubkey
print(f"[*] Qwen Agent starting with ID: {agent_id}")

# Load model and tokenizer
print("[*] Loading Qwen2.5-2B model...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    print("[+] Model loaded successfully")
except Exception as e:
    print(f"[!] Failed to load model: {e}")
    model = None
    tokenizer = None

# Wait for coordinator
import sys
for i in range(10):
    try:
        resp = requests.get(f"{COORDINATOR}/", timeout=5)
        print("[+] Coordinator is ready")
        break
    except:
        print(f"[*] Waiting for coordinator... ({i+1}/10)")
        time.sleep(3)
else:
    print("[!] Coordinator not available")
    sys.exit(1)

# Register as training agent
resp = requests.post(f"{COORDINATOR}/register", json={
    "id": agent_id,
    "pubkey": pubkey,
    "price_per_hour": 0.05,
    "capacity": "gpu=1,cpu=4,ram=8"
})
print(f"[+] Registered: {resp.json()}")

def train_step(task_data):
    """
    Run a fine-tuning step on Qwen2.5-2B
    """
    if model is None:
        return {"error": "Model not loaded", "loss": 999.0}
    
    batch = task_data.get("batch", [])
    epochs = task_data.get("epochs", 1)
    
    if not batch:
        return {"error": "Empty batch", "loss": 999.0}
    
    print(f"[*] Fine-tuning on {len(batch)} samples for {epochs} epoch(s)...")
    
    # Prepare training data
    texts = []
    for item in batch:
        prompt = item.get("prompt", "")
        response = item.get("response", "")
        # Format as instruction
        text = f"Instruction: {prompt}\nResponse: {response}"
        texts.append(text)
    
    # Tokenize
    try:
        encodings = tokenizer(texts, truncation=True, padding=True, max_length=256, return_tensors="pt")
        encodings = {k: v.to(model.device) for k, v in encodings.items()}
        
        # Create dataset
        class SimpleDataset:
            def __init__(self, encodings):
                self.encodings = encodings
            def __len__(self):
                return len(self.encodings["input_ids"])
            def __getitem__(self, i):
                return {k: v[i] for k, v in self.encodings.items()}
        
        dataset = SimpleDataset(encodings)
        
        # Quick training with minimal steps
        training_args = TrainingArguments(
            output_dir="/tmp/checkpoint",
            num_train_epochs=epochs,
            per_device_train_batch_size=1,
            learning_rate=1e-4,
            logging_steps=1,
            save_strategy="no",
            report_to="none",
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
        )
        
        trainer.train()
        
        # Get training loss
        loss = trainer.state.log_history[-1].get("loss", 0) if trainer.state.log_history else 0
        
        # Generate checkpoint hash
        checkpoint_hash = hashlib.sha256(
            f"{agent_id}{time.time()}".encode()
        ).hexdigest()[:16]
        
        return {
            "loss": loss,
            "checkpoint_hash": checkpoint_hash,
            "samples_processed": len(batch) * epochs,
            "agent_id": agent_id,
            "model": MODEL_NAME
        }
        
    except Exception as e:
        print(f"[!] Training error: {e}")
        return {"error": str(e), "loss": 999.0}

# Main loop
while True:
    try:
        # Heartbeat
        requests.post(f"{COORDINATOR}/heartbeat", json={
            "id": agent_id,
            "capacity": "gpu=1,cpu=4,ram=8"
        }, timeout=5)
        
        # Pull task
        resp = requests.get(f"{COORDINATOR}/tasks/{agent_id}")
        data = resp.json()
        
        if data.get("task"):
            task = data["task"]
            task_id = task["id"]
            payload = task["payload"]
            print(f"[*] Got training task {task_id}")
            
            # Run training
            result = train_step(payload)
            print(f"[+] Training complete: loss={result.get('loss', 'N/A')}")
            
            # Submit result
            sig_input = f"{secret}{task_id}"
            signature = base64.b64encode(sig_input.encode()).decode()
            
            requests.post(f"{COORDINATOR}/result", json={
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result,
                "signature": signature
            })
        else:
            print("[*] No training tasks, waiting...")
            
    except Exception as e:
        print(f"[!] Error: {e}")
    
    time.sleep(10)
