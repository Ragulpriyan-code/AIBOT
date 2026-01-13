import os
from sentence_transformers import SentenceTransformer

def download():
    model_name = "all-MiniLM-L6-v2"
    # Set cache dir to a local folder that will be part of the Docker image
    cache_dir = os.path.join(os.getcwd(), "model_cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"📥 Downloading embedding model: {model_name} to {cache_dir}...")
    
    # Setting environment variables for the current process
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = cache_dir
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    
    SentenceTransformer(model_name, cache_folder=cache_dir)
    print("✅ Model downloaded and cached successfully.")

if __name__ == "__main__":
    download()
