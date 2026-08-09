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

    # 1. Traitement d'image amélioré (Otsu pour s'adapter à la luminosité)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Aucune silhouette distincte détectée sur la photo.")

    # Isolation du corps principal
    main_contour = max(contours, key=cv2.contourArea)
    x, y, w_box, h_box = cv2.boundingRect(main_contour)

    if h_box == 0:
        raise ValueError("La silhouette détectée est invalide.")

    # Échelle de conversion : cm par pixel basée sur la hauteur réelle
    cm_per_pixel = height_cm / float(h_box)

    # 2. Masque de la silhouette pour mesurer la largeur exacte ligne par ligne
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [main_contour], -1, 255, -1)

    def get_row_width(y_percent: float) -> float:
        """Calcule la largeur en pixels du corps à une hauteur relative donnée (ex: 0.20 pour 20%)."""
        row_y = int(y + h_box * y_percent)
        row_y = min(max(row_y, 0), h - 1)
        row_pixels = np.where(mask[row_y, :] > 0)[0]
        if len(row_pixels) > 0:
            return float(row_pixels[-1] - row_pixels[0])
        return 0.0

    # 3. EXTRACTION DES LARGEURS SPÉCIFIQUES (par hauteur relative anatomique)
    # Carrure épaules (~18% du haut)
    shoulder_width_px = get_row_width(0.18)
    # Poitrine (~28% du haut)
    chest_width_px = get_row_width(0.28)
    # Taille - point le plus étroit du buste (entre 38% et 45%)
    waist_widths = [get_row_width(pct) for pct in np.linspace(0.38, 0.45, 10)]
    waist_width_px = min([w for w in waist_widths if w > 0] or [shoulder_width_px * 0.7])
    # Hanches (~52% du haut)
    hip_width_px = get_row_width(0.52)

    # Convertir en cm
    shoulder_width_cm = round(shoulder_width_px * cm_per_pixel, 1)
    chest_width_cm = round(chest_width_px * cm_per_pixel, 1)
    waist_width_cm = round(waist_width_px * cm_per_pixel, 1)
    hip_width_cm = round(hip_width_px * cm_per_pixel, 1)

    # 4. LONGUEURS ANATOMIQUES
    arm_length_cm = round((h_box * 0.33) * cm_per_pixel, 1)      # Épaule à Poignet
    leg_length_cm = round((h_box * 0.47) * cm_per_pixel, 1)      # Entrejambe à Cheville
    bust_height_cm = round((h_box * 0.28) * cm_per_pixel, 1)     # Épaule à Taille

    # 5. CIRCONFÉRENCES (Ratios d'ellipse réalistes pour profil moyen)
    # Formule basée sur la largeur mesurée de face
    chest_circ_cm = round(chest_width_cm * 2.05, 1)
    waist_circ_cm = round(waist_width_cm * 1.90, 1)
    hip_circ_cm = round(hip_width_cm * 2.10, 1)

    return {
        "longueurs": {
            "longueur_bras_cm": arm_length_cm,
            "longueur_jambe_entrejambe_cm": leg_length_cm,
            "hauteur_buste_cm": bust_height_cm
        },
        "largeurs_a_plat": {
            "carrure_epaules_cm": shoulder_width_cm,
            "largeur_poitrine_cm": chest_width_cm,
            "largeur_taille_cm": waist_width_cm,
            "largeur_bassin_cm": hip_width_cm
        },
        "cirferences_estimees": {
            "tour_de_poitrine_cm": chest_circ_cm,
            "tour_de_taille_cm": waist_circ_cm,
            "tour_de_hanches_cm": hip_circ_cm
        }
    }