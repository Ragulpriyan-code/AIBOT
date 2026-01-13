import os
from sentence_transformers import SentenceTransformer

def download():
    model_name = "all-MiniLM-L6-v2"
    print(f"📥 Downloading embedding model: {model_name}...")
    # This will download and cache the model in the default transfromers location
    # which we'll keep in the Docker image.
    SentenceTransformer(model_name)
    print("✅ Model downloaded and cached successfully.")

if __name__ == "__main__":
    download()
