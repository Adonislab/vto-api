from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.pose_service import process_measurements

router = APIRouter(prefix="", tags=["Anatomie & Mensurations"])

@router.post("/estimate-measurements")
async def estimate_measurements(
    human_image: UploadFile = File(...),
    height_cm: float = Form(..., description="Taille de la personne en cm")
):
    try:
        image_bytes = await human_image.read()
        measurements = process_measurements(image_bytes, height_cm)

        return {
            "success": True,
            "user_height_cm": height_cm,
            "estimated_measurements": measurements,
            "note": "Estimation basée sur les proportions visuelles."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")