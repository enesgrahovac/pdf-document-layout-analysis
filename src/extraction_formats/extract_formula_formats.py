import io
from PIL.Image import Image
from rapid_latex_ocr import LatexOCR
from data_model.PdfImages import PdfImages
from fast_trainer.PdfSegment import PdfSegment
from pdf_token_type_labels.TokenType import TokenType


def get_latex_format(model: LatexOCR, formula_image: Image):
    buffer = io.BytesIO()
    formula_image.save(buffer, format="jpeg")
    image_bytes = buffer.getvalue()
    result, elapsed_time = model(image_bytes)
    return result


def extract_formula_format(pdf_images: PdfImages, predicted_segments: list[PdfSegment]):
    formula_segments = [
        (index, segment) for index, segment in enumerate(predicted_segments) if segment.segment_type == TokenType.FORMULA
    ]
    if not formula_segments:
        return

    model = LatexOCR()

    for index, formula_segment in formula_segments:
        page_image: Image = pdf_images.pdf_images[formula_segment.page_number - 1]
        left, top = formula_segment.bounding_box.left, formula_segment.bounding_box.top
        width, height = formula_segment.bounding_box.width, formula_segment.bounding_box.height
        formula_image = page_image.crop((left, top, left + width, top + height))
        try:
            extracted_formula = get_latex_format(model, formula_image)
        except RuntimeError:
            continue
        predicted_segments[index].text_content = extracted_formula