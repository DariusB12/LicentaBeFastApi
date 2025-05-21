import re
import base64
import numpy as np
from fastapi import status
import cv2
from exceptions.custom_exceptions import CustomHTTPException
from service.yolo_services.emoji import EMOJI_REGEXP
import fasttext
from lingua import Language, LanguageDetectorBuilder

COMMON_LANGUAGES = ['eng', 'fra', 'spa', 'deu', 'ita', 'ron', 'por']
COMMON_LANGUAGES_LINGUA = [Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.GERMAN, Language.ITALIAN,
                           Language.ROMANIAN, Language.PORTUGUESE]
MAX_CHARACTERS_LENGTH_LINGUA = 50

# CREATE THE LINGUA LANGUAGE DETECTOR
detector = LanguageDetectorBuilder.from_languages(*COMMON_LANGUAGES_LINGUA).build()

# LOAD THE LANGUAGE DETECTION MODEL lid218
modelLID = fasttext.load_model(
    "ai_models/language_detection/lid218e.bin")

NON_ALPHA_TOKEN_RE = re.compile(
    # using MULTILINE so that ^ means the beginning of a line
    r'(^|[\s\b])([^A-Za-z\n]+)([\s\b]|$)', re.MULTILINE)


def normalize_text(text):
    """
    Normalizes the given text by reducing the noise
    """
    # If the description/comment is too long and has '... more' at the end of text, then remove it
    # Or if at the end of the text there are more link, it will appear the first link followed by 'and x more'
    text = re.sub(r'\.\.\.\smore|\s*and\s*\d\s*more\s*$', '', text)

    # remove strange types of links (e.g amywinehouse.Ink.to/biolB)
    # if the string matches word/word then it won't fit into the regex because
    # on instagram profiles we can have for example Music/band which is meaningful for the profile description, and
    # we don't want to remove this sequences
    text = re.sub(r'(?!\w+/\w+)(\b\w+(\.\w{2,})*/\S*(\.\w{2,})*(/\S*(\.\w{2,})*)*)', '', text)

    # REMOVE LINKS LIKE http, youtu.be, .com
    text = re.sub(r'https?://\S+|youtu\.be/\S+|.+\.com', '', text)

    # remove words containing only non letters (also removes phone numbers)
    text = NON_ALPHA_TOKEN_RE.sub(r'\1\3', text)

    # tags = DMs (ex: @another_account)
    text = re.sub(r'@\w+(\.\w+)*', '', text)
    # consecutive newlines become single newline
    text = re.sub(r'\n{2,}', '\n', text)
    # multiple white spaces become single space
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    # after newlines, remove the white spaces
    text = re.sub(r'\n([^\S\r\n]+)', '\n', text)

    # Remove leading whitespace/newlines only from the first line
    text = re.sub(r'^(\s+)', '', text)

    # Remove newline at the end of text, if it exists
    return text.rstrip('\n')


def remove_emojis_from_text(text):
    return re.sub(EMOJI_REGEXP, '', text)


def denoise_text_for_language_analysis(text):
    """
    Denoise an already normalized text, but this time this function normalizes
    for language analysis, it entails removing irrelevant text for language detection:
    - spaces/newlines become single space (the text becomes a single line text)
    - text becomes lower case
    :param text: the already normalized text
    :return: the denoise text IN LOWER CASE (BETTER LANGUAGE DETECTION)
    """
    # SPACES/NEWLINES BECOME SINGLE SPACE
    text = re.sub(r'\s+', ' ', text)

    # I observed that language is best detected when the text is given all in lowercase
    return text.strip().lower()


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


def predict_text_language_fasttext_lid218(text):
    """
    Predicts the language of the given text, the languages predicted by the lid218 model are filtered, and the function
    extracts the first language detected with the highest probability, that is also included in the COMMON_LANGUAGES
    list, if no common language was detected, then english will be the default language returned
    :param text: the text from which we predict the language
    :return: the predicted language
    """
    src_lang = 'eng'
    # LIST WITH ALL THE LANGUAGES SORTED BASED ON PROBABILITIES
    predictions = modelLID.predict(text, k=218)
    for prediction in predictions[0]:
        lang = prediction.replace('__label__', '').split('_')[0]
        if lang in COMMON_LANGUAGES:
            src_lang = prediction.replace('__label__', '').split('_')[0]
            print(f"Lang Detected:", src_lang)
            return src_lang
    return src_lang


def predict_text_language_lingua(text):
    """
    Predicts the language of the given text with lingua model (very accurate for short and mixed texts),
    The detection is made based on the included languages in the COMMON_LANGUAGES_LINGUA list
    If no language was detected, then english will be the default language returned
    :param text: the text from which we predict the language
    :return: the predicted language
    """
    # FIND THE LANGUAGE WITH LINGUA
    detected_language = detector.detect_language_of(text)
    if detected_language is None:
        return 'eng'
    return detected_language.iso_code_639_3.name.lower()
