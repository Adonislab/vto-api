from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.replicate_service import run_idm_vton, download_image_bytes

router = APIRouter(prefix="", tags=["Essayage Virtuel"])

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/try-on")
async def try_on(
    human_image: UploadFile = File(..., description="Photo de la personne"),
    garment_image: UploadFile = File(..., description="Photo du vêtement"),
    category: str = Form("upper_body", description="upper_body, lower_body ou dresses"),
    description: str = Form("clothing item", description="Description courte")
):
    try:
        for img in [human_image, garment_image]:
            if img.content_type not in ALLOWED_TYPES:
                raise HTTPException(status_code=400, detail=f"Format non supporté pour {img.filename}.")

        human_bytes = await human_image.read()
        garment_bytes = await garment_image.read()

        result_url = run_idm_vton(human_bytes, garment_bytes, category, description)
        return {"success": True, "result_url": result_url, "category": category}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'essayage : {str(e)}")


@router.post("/try-on-outfit")
async def try_on_outfit(
    human_image: UploadFile = File(...),
    top_image: UploadFile = File(None),
    bottom_image: UploadFile = File(None)
):
    try:
        if not top_image and not bottom_image:
            raise HTTPException(status_code=400, detail="Veuillez fournir au moins un vêtement.")

        current_human_bytes = await human_image.read()
        result_url = None

        if top_image:
            top_bytes = await top_image.read()
            result_url = run_idm_vton(current_human_bytes, top_bytes, "upper_body")
            current_human_bytes = download_image_bytes(result_url)

        if bottom_image:
            bottom_bytes = await bottom_image.read()
            result_url = run_idm_vton(current_human_bytes, bottom_bytes, "lower_body")

        return {"success": True, "result_url": result_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la tenue : {str(e)}")