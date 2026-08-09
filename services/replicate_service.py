import os
import io
import urllib.request
import replicate
from dotenv import load_dotenv

load_dotenv()

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
MODEL_VERSION = "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985"

def get_replicate_client():
    if not REPLICATE_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN manquant dans le fichier .env")
    return replicate.Client(api_token=REPLICATE_TOKEN)

def run_idm_vton(human_bytes: bytes, garment_bytes: bytes, category: str, description: str = "clothing item") -> str:
    client = get_replicate_client()
    output = client.run(
        MODEL_VERSION,
        input={
            "human_img": io.BytesIO(human_bytes),
            "garm_img": io.BytesIO(garment_bytes),
            "garment_des": description,
            "category": category,
            "crop": True,
            "steps": 30
        }
    )
    return str(output)

def download_image_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read()