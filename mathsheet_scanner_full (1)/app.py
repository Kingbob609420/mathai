from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64
import io
import torch
from PIL import Image
import requests
import re
import json
import os
import sympy
from sympy import symbols, solve, simplify, expand

app = Flask(__name__)
CORS(app)

# Try to use local model if available, otherwise use API
try:
    from transformers import pipeline
    print("Loading local OCR model...")
    pipe = pipeline("image-to-text", model="microsoft/trocr-base-handwritten", use_fast=True)
    USE_LOCAL_MODEL = True
    print("Local OCR model loaded successfully!")
except Exception as e:
    print(f"Local model not available: {e}")
    USE_LOCAL_MODEL = False
    pipe = None

# Hugging Face API configuration
HF_API_TOKEN = "hf_FhIncFxUmjJfMaYTCVrmUjvPsMajDhSRU"  # Set your token here
HF_API_URL = "https://api-inference.huggingface.co/models/razhan/trocr-handwritten-ckb"

# Hugging Face GPT-OSS-120B configuration
GPT_API_URL = "https://api-inference.huggingface.co/models/amd/Instella-3B-Math"

def set_api_token(token):
    """Set the Hugging Face API token"""
    global HF_API_TOKEN
    HF_API_TOKEN = token
    print(f"API token set: {token[:10]}..." if token else "No API token set")

def call_gpt_api(question):
    """Call Hugging Face API for math solving using Instella-3B-Math"""
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "inputs": f"{question}",
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.1,
                "do_sample": False
            }
        }

        print(f"Calling Hugging Face Instella-3B-Math API for: {question}")

        response = requests.post(
            GPT_API_URL,
            headers=headers,
            json=data,
            timeout=60
        )

        print(f"API Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                answer = result.get('generated_text', '')
            else:
                return None
            return answer.strip()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error calling math API: {e}")
        return None


def health_check():
    return jsonify({'status': 'healthy', 'ocr_loaded': USE_LOCAL_MODEL and pipe is not None})

if __name__ == '__main__':
    print("Starting MathScan API...")
    print(f"OCR Model: {'Loaded' if USE_LOCAL_MODEL and pipe is not None else 'Not loaded'}")
    print(f"Hugging Face API Token: {'Set' if HF_API_TOKEN else 'Not set - will use local model'}")
    print(f"GPT API: {'Available' if HF_API_TOKEN else 'Not available - will use local math solving'}")
    app.run(debug=False, host='0.0.0.0', port=5000) 