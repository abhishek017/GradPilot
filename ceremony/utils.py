from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

def process_photo(image_path, size=(900, 1200)):
    """
    Auto-crop to center and resize to 3:4 portrait ratio.
    size default = 900x1200 (high quality for big screen)
    """
    if not image_path:
        return None

    img = Image.open(image_path).convert("RGB")

    target_ratio = size[0] / size[1]
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image too wide → crop horizontally
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = img.height
    else:
        # Image too tall → crop vertically
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = img.width

    img = img.crop((left, top, right, bottom))
    img = img.resize(size, Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)

    return ContentFile(buffer.getvalue())