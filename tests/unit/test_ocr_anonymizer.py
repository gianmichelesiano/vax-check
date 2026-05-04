from PIL import Image

from vaxcheck.ocr.anonymizer import anonymize_booklet_image, verify_anonymization


def test_anonymize_covers_top_15_percent():
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    result = anonymize_booklet_image(img)
    assert result.getpixel((400, 100)) == (100, 100, 100)
    assert result.getpixel((400, 300)) == (255, 255, 255)


def test_verify_anonymization_passes():
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    anonymized = anonymize_booklet_image(img)
    assert verify_anonymization(anonymized) is True


def test_verify_anonymization_fails_on_original():
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    assert verify_anonymization(img) is False
