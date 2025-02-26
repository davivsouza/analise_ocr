import base64
import io
import os
import fitz
import json
from PIL import Image, ImageEnhance


# Função para converter imagem em Base64
def convert_to_base64(image_path: str):
    """Carrega uma imagem, melhora a qualidade e converte para Base64."""
    img = Image.open(image_path)
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# Função para extrair uma página de um PDF e converter para Base64
def pdf_to_base64(pdf_path: str, page_number: int = 1):
    """Extrai uma página do PDF, melhora a qualidade e converte para base64."""
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1)
    matrix = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=matrix)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
