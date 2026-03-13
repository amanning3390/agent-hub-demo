#!/usr/bin/env python3
"""
Community LLM - Qwen2.5-2B Training Job

This client submits training jobs to fine-tune Qwen2.5-2B
using the distributed agent network.
"""

import os
import json
import time
import uuid
import requests

COORDINATOR = os.getenv("COORDINATOR_URL", "http://localhost:8000")
X402 = os.getenv("X402_URL", "http://localhost:8080")

# Training data for Qwen
TRAINING_DATA = [
    {"prompt": "What is machine learning?", "response": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."},
    {"prompt": "Explain neural networks:", "response": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information using connectionist approaches."},
    {"prompt": "What is Python used for?", "response": "Python is a versatile programming language used for web development, data science, AI/ML, automation, and more."},
    {"prompt": "Define deep learning:", "response": "Deep learning is a subset of machine learning using artificial neural networks with multiple layers (deep neural networks) to learn representations of data."},
    {"prompt": "What is a transformer model?", "response": "Transformer is a neural network architecture using self-attention mechanisms, enabling parallel processing of sequential data. It's the foundation of modern LLMs."},
    {"prompt": "Explain backpropagation:", "response": "Backpropagation is an algorithm used to train neural networks. It computes gradients of a loss function with respect to network weights."},
    {"prompt": "What is tokenization?", "response": "Tokenization is the process of converting text into numerical tokens that language models can process."},
    {"prompt": "Define hyperparameters:", "response": "Hyperparameters are configuration settings chosen before training a machine learning model, such as learning rate, batch size, and number of epochs."},
]

def create_training_job():
    """Create a Qwen fine-tuning job"""
    
    offer = {
        "title": "Qwen2.5-2B Community Fine-tuning",
        "description": "Fine-tune Qwen2.5-2B on community knowledge",
        "budget_usd": 10,
        "max_price_per_hour_usd": 0.05,
        "resource_requirements": {
            "cpu_cores": 4,
            "gpu_units": 1,
            "ram_gb": 8
        },
        "deadline_unix": int(time.time()) + 7200,
        "type": "training",
        "model": "Qwen/Qwen2.5-2B-Instruct",
        "payload": {}
    }
    
    print("[*] Creating Qwen training offer...")
    resp = requests.post(f"{COORDINATOR}/offers", json=offer)
    if resp.status_code != 200:
        print(f"[!] Failed: {resp.text}")
        return None
    
    offer_data = resp.json()
    offer_id = offer_data["offer_id"]
    print(f"[+] Offer created: {offer_id}")
    
    # Fund
    pay_resp = requests.post(f"{X402}/create-payment", json={"amount_usd": 10})
    payment_id = pay_resp.json()["payment_id"]
    requests.get(f"{X402}/complete/{payment_id}")
    print("[+] Payment completed")
    
    # Create training tasks
    tasks = []
    for i, data in enumerate(TRAINING_DATA):
        task_id = str(uuid.uuid4())
        tasks.append({
            "id": task_id,
            "payload": {
                "task_type": "fine_tune",
                "batch": [data],
                "epochs": 1,
                "learning_rate": 0.0001,
                "model": "Qwen/Qwen2.5-2B-Instruct"
            }
        })
    
    requests.post(f"{COORDINATOR}/offers/{offer_id}/tasks", json={"tasks": tasks})
    print(f"[+] Submitted {len(tasks)} fine-tuning tasks")
    
    return offer_id

def monitor_training(offer_id):
    """Monitor training progress"""
    print("\n=== Qwen2.5-2B Training Progress ===")
    
    total = len(TRAINING_DATA)
    while True:
        time.sleep(5)
        resp = requests.get(f"{COORDINATOR}/offers/{offer_id}/results")
        if resp.status_code != 200:
            continue
        
        results = resp.json().get("results", [])
        completed = len(results)
        
        losses = []
        for r in results:
            if "output" in r and "loss" in r["output"]:
                losses.append(r["output"]["loss"])
        
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        print(f"Progress: {completed}/{total} | Avg Loss: {avg_loss:.4f}")
        
        if completed >= total:
            break
    
    print("\n=== Training Complete ===")
    print("Qwen2.5-2B has learned from community data!")
    
    print("\nCheckpoints:")
    for r in results:
        if "output" in r:
            out = r["output"]
            print(f"  - {out.get('checkpoint_hash', '?')} | Loss: {out.get('loss', 0):.4f}")

if __name__ == "__main__":
    offer_id = create_training_job()
    if offer_id:
        monitor_training(offer_id)
