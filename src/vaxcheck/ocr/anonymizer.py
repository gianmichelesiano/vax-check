from PIL import Image, ImageDraw

ANAGRAFICA_ZONE_RATIO = 0.15


def anonymize_booklet_image(img: Image.Image) -> Image.Image:
    """Oscura la zona anagrafica del libretto svizzero prima dell'invio a Claude API.

    Il libretto vaccinale svizzero standard ha layout fisso:
    - Top ~15%: nome, cognome, data nascita, numero AVS, firma
    - Resto: tabella vaccinazioni

    Returns una copia dell'immagine con zona anagrafica oscurata.
    """
    result = img.copy()
    draw = ImageDraw.Draw(result)
    w, h = result.size
    obscure_height = int(h * ANAGRAFICA_ZONE_RATIO)
    draw.rectangle([0, 0, w, obscure_height], fill=(100, 100, 100))
    return result


def verify_anonymization(img: Image.Image) -> bool:
    """Verifica che la zona anagrafica sia oscurata."""
    w, h = img.size
    check_height = int(h * ANAGRAFICA_ZONE_RATIO)
    sample_pixels = [
        img.getpixel((w // 4, check_height // 2)),
        img.getpixel((w // 2, check_height // 2)),
        img.getpixel((3 * w // 4, check_height // 2)),
    ]
    return all(
        abs(r - 100) < 20 and abs(g - 100) < 20 and abs(b - 100) < 20
        for r, g, b, *_ in sample_pixels
    )
