import os
import io
import replicate
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

app = FastAPI(
    title="Virtual Try-On API",
    description="API d'essayage virtuel de vêtements avec FastAPI et IA Générative"
)

# Configuration CORS pour autoriser l'accès depuis votre Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du client Replicate
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN manquant dans le fichier .env")

replicate_client = replicate.Client(api_token=REPLICATE_TOKEN)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API VTO opérationnelle"}


@app.post("/try-on")
async def try_on(
    human_image: UploadFile = File(..., description="Photo de la personne (PNG/JPEG)"),
    garment_image: UploadFile = File(..., description="Photo du vêtement (PNG/JPEG)"),
    category: str = Form("upper_body", description="Catégorie: upper_body, lower_body ou dresses"),
    description: str = Form("clothing item", description="Description courte du vêtement")
):
    """
    Endpoint d'essayage virtuel : prend 2 fichiers images et génère le rendu d'essayage.
    """
    try:
        # Validation des types MIME
        for img in [human_image, garment_image]:
            if img.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Format non supporté pour {img.filename}. Utilisez JPEG ou PNG."
                )

        # Lecture du contenu des images envoyées
        human_bytes = await human_image.read()
        garment_bytes = await garment_image.read()

        # Création des flux binaires pour transmission directe à l'API Replicate
        human_file_obj = io.BytesIO(human_bytes)
        garment_file_obj = io.BytesIO(garment_bytes)

        # Appel du modèle VTO via Replicate (IDM-VTON)
        output = replicate_client.run(
            "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
            input={
                "human_img": human_file_obj,
                "garm_img": garment_file_obj,
                "garment_des": description,
                "category": category,
                "crop": True,
                "steps": 30
            }
        )

        # L'API Replicate retourne un objet FileOutput ou une chaîne d'URL
        result_url = str(output)

        return {
            "success": True,
            "result_url": result_url,
            "category": category
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du traitement de l'essayage : {str(e)}"
        )