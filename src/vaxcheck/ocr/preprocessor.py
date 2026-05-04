from PIL import Image, ImageEnhance

MAX_DIMENSION = 2048
MIN_DIMENSION = 800


def preprocess_booklet_image(img: Image.Image) -> Image.Image:
    """Prepara l'immagine per OCR ottimale.

    1. Converte in RGB (rimuove canale alpha)
    2. Ridimensiona se troppo grande (preserva aspect ratio)
    3. Aumenta contrasto (aiuta testo scritto a mano)
    4. Upscale se troppo piccola
    """
    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size

    if max(w, h) < MIN_DIMENSION:
        scale = MIN_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    if max(w, h) > MAX_DIMENSION:
        scale = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)

    return img
