import re
import base64
import numpy as np
from fastapi import status
import cv2
from exceptions.custom_exceptions import CustomHTTPException

def parse_number(text):
    """
    Extracts the number from the given text
    The text is expected to be in the format that instagram shows numbers:
    x.xxx B (billions), x.xxx M (millions), x.x K (thousands) or d,ddd (thousands) or a single number without ',' or '.'
    :param text: the text which contains a number
    :return: the number extracted from the text and transformed (if B,M or K suffixes are present) accordingly
    """
    text = text.strip()

    # EXTRACT THE NUMBER AND SUFFIX (K, M, B)
    # \s matches a whitespace (blank, tab \t , and newline \r or \n )
    match = re.search(r'([\d.,]+)\s*([KMB]?)', text, re.IGNORECASE)
    if not match:
        return None

    number_str, suffix = match.groups()
    suffix = suffix.upper()

    # IF THE NUMBER IS WITH ',' (on instagram only thousand numbers can be ex: 1,222)
    if ',' in number_str:
        # SEPARATE THE NUMBERS BY THE COMMA
        parts = number_str.split(',')
        if len(parts[-1]) == 3 and all(p.isdigit() for p in parts):
            number_str = ''.join(parts)

    try:
        # FIRST WE CONVERT TO FLOAT (because of the values like 1.2K, 2.3B, 12.34M)
        number = float(number_str)
        if suffix == 'K':
            number *= 1_000
        elif suffix == 'M':
            number *= 1_000_000
        elif suffix == 'B':
            number *= 1_000_000_000
        return int(number)
    except ValueError:
        return None


def cv2_img_to_base64(cv2_img, image_format='jpeg'):
    """
    Converts a cv2 image to a base64-encoded string, by default converts it to jpeg format

    :param cv2_img: OpenCV image (numpy array).
    :param image_format: Image format (jpeg, png or jpg).
    :return: Base64-encoded string of the image, with data URI prefix.
    :raises: HTTP_400_BAD_REQUEST if the conversion from cv2 to base64 could not be made
    """
    try:
        # Encode image as bytes (e.g., .jpg or .png)
        success, encoded_image = cv2.imencode(f'.{image_format}', cv2_img)
        if not success:
            raise ValueError("Image encoding failed.")

        # Convert to base64
        base64_bytes = base64.b64encode(encoded_image.tobytes())
        base64_str = base64_bytes.decode('utf-8')

        # Return with data URI prefix
        return f'data:image/{image_format};base64,{base64_str}'
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Could not convert cv2 image to base64."
        )


def base64_to_cv2_img(base64_str):
    """
    Converts a base64 image into a cv2 image
    :param base64_str: the image in base64 format
    :return: the image converted into cv2
    Throws exception if the image is not a valid base64 string
    """
    try:
        # IF base64_str HAS THE PREFIX: "data:image/jpeg;base64,..." WE REMOVE IT:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        # DECODE BASE64 INTO BYTES
        img_bytes = base64.b64decode(base64_str)

        # TRANSFORM THE BYTES INTO NUMPY.ARRAY
        nparr = np.frombuffer(img_bytes, np.uint8)

        # DECODE THE NUMPY ARRAY INTO CV2 IMAGE
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_cv2 is not None:
            return img_cv2
        else:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid base64 image format."
            )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid base64 image format."
        )


def languages_list_to_tesseract_lang(languages):
    """
    Converts a list of strings representing language names accepted by tesseract, into a single string
    with languages concatenated with '+'
    :param languages: a lis tof languages
    :return: a stirng with languages concatenated with '+'
    """
    tesseract_lang = ""
    for i in range(0, len(languages)):
        if i != len(languages) - 1:
            tesseract_lang += languages[i] + "+"
        else:
            tesseract_lang += languages[i]

    return tesseract_lang
