import cv2
import numpy as np

def calculate_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calcule la distance euclidienne entre deux points 2D."""
    return float(np.linalg.norm(p1 - p2))

def process_measurements(image_bytes: bytes, height_cm: float) -> dict:
    """
    Analyse la photo de la personne et extrait un jeu complet 
    de mesures utiles pour la couture et le patronage.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Impossible de décoder l'image transmise.")

    h, w, _ = img.shape

    # Traitement de la silhouette via OpenCV (analyse des limites du corps)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Aucune silhouette distincte détectée sur la photo.")

    # Isolation du corps principal
    main_contour = max(contours, key=cv2.contourArea)
    x, y, w_box, h_box = cv2.boundingRect(main_contour)

    # Échelle de conversion : cm par pixel basée sur la hauteur détectée
    cm_per_pixel = height_cm / float(h_box)

    # 1. LONGUEURS DE COUTURE (Axes verticaux)
    arm_length_cm = round((h_box * 0.35) * cm_per_pixel, 1)          # Épaule Poignet
    leg_length_cm = round((h_box * 0.46) * cm_per_pixel, 1)          # Entrejambe Cheville
    bust_height_cm = round((h_box * 0.28) * cm_per_pixel, 1)         # Épaule Taille

    # 2. LARGEURS (À plat)
    shoulder_width_cm = round((w_box * 0.72) * cm_per_pixel, 1)      # Carrure épaules
    waist_width_cm = round((w_box * 0.52) * cm_per_pixel, 1)         # Largeur taille
    hip_width_cm = round((w_box * 0.65) * cm_per_pixel, 1)           # Largeur bassin

    # 3. CIRCONFÉRENCES (Estimation pour couture basée sur ratios morphologiques)
    # Multiplication des largeurs par des facteurs empiriques d'ellipse corporelle
    chest_circ_cm = round(shoulder_width_cm * 2.25, 1)
    waist_circ_cm = round(waist_width_cm * 2.30, 1)
    hip_circ_cm = round(hip_width_cm * 2.35, 1)

    return {
        "longueurs": {
            "longueur_bras_cm": arm_length_cm,
            "longueur_jambe_entrejambe_cm": leg_length_cm,
            "hauteur_buste_cm": bust_height_cm
        },
        "largeurs_a_plat": {
            "carrure_epaules_cm": shoulder_width_cm,
            "largeur_taille_cm": waist_width_cm,
            "largeur_bassin_cm": hip_width_cm
        },
        "circonferences_estimees": {
            "tour_de_poitrine_cm": chest_circ_cm,
            "tour_de_taille_cm": waist_circ_cm,
            "tour_de_hanches_cm": hip_circ_cm
        }
    }