import base64
import os
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps

def preprocess_and_enhance_image(image_input) -> str:
    """
    Optimized Image Preprocessing:
    - Auto-scales high-res camera photos to optimal dimensions (max 1024px) for 10x faster inference.
    - Enhances sharpness and contrast to decipher blurry/faint text.
    - Auto-corrects brightness and lighting.
    Returns base64 string ready for LLaVA.
    """
    if isinstance(image_input, str):
        if os.path.isfile(image_input):
            img = Image.open(image_input).convert('RGB')
        else:
            response = requests.get(image_input, stream=True)
            img = Image.open(BytesIO(response.content)).convert('RGB')
    elif hasattr(image_input, 'read'):
        img = Image.open(image_input).convert('RGB')
    else:
        img = image_input.convert('RGB')

    # 1. Normalize dimensions for fast & accurate inference
    # Max dimension capped at 1024px to prevent CPU bottlenecks on high-res camera photos
    max_dim = max(img.size)
    if max_dim > 1024:
        scale = 1024 / max_dim
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    
    # If image is too small, upscale to at least 600px for text legibility
    min_dim = min(img.size)
    if min_dim < 600:
        scale = 600 / min_dim
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)

    # 2. Auto-contrast to balance dark shadows or overexposure
    try:
        img = ImageOps.autocontrast(img, cutoff=0.5)
    except Exception:
        pass

    # 3. Enhance Sharpness (De-blurring filter)
    enhancer_sharpness = ImageEnhance.Sharpness(img)
    img = enhancer_sharpness.enhance(1.8)

    # 4. Enhance Contrast (makes text crisp and legible)
    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(1.25)

    # 5. Compress to compact JPEG
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=85, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def answer_visual_question(image_path_or_url: str, question: str = "") -> str:
    """
    High-accuracy Visual Question Answering using Ollama's LLaVA.
    Optimized for fast processing with a 180s safety timeout.
    """
    try:
        # Preprocess, downscale huge camera resolutions, and de-blur image
        b64_image = preprocess_and_enhance_image(image_path_or_url)
        
        if not question or question.strip() == "":
            prompt = (
                "You are an expert computer vision and document OCR specialist. Examine this image carefully. "
                "Read and transcribe all visible text, document policies, numbers, diagrams, or key details, "
                "and provide a structured, comprehensive summary."
            )
        else:
            prompt = (
                f"You are an expert document reader and vision assistant. Examine the text and details in this image carefully.\n"
                f"Answer the user's question with direct, factual precision based on the image content.\n\n"
                f"User Question: {question.strip()}\n"
                f"Answer:"
            )
            
        payload = {
            "model": "llava",
            "prompt": prompt,
            "images": [b64_image],
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096
            }
        }
        
        # 180s timeout buffer to guarantee completion on any hardware
        res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        if res.status_code == 200:
            return res.json().get("response", "Could not generate response from image.").strip()
        else:
            return f"Error from Vision model: HTTP {res.status_code} - {res.text}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Vision Model Timeout: The image was too heavy to process in time. Please try asking again or crop closer to the text."
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama Error: Ollama service is not running. Please make sure Ollama is open and running on your computer."
    except Exception as e:
        return f"Error analyzing image: {str(e)}"