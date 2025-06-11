import fasttext
from lingua import Language, LanguageDetectorBuilder
import re

from logging_config import logger

COMMON_LANGUAGES = ['eng', 'fra', 'spa', 'deu', 'ita', 'ron', 'por']
COMMON_LANGUAGES_LINGUA = [Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.GERMAN, Language.ITALIAN,
                           Language.ROMANIAN, Language.PORTUGUESE]
MAX_CHARACTERS_LENGTH_LINGUA = 50

# CREATE THE LINGUA LANGUAGE DETECTOR
detector = LanguageDetectorBuilder.from_languages(*COMMON_LANGUAGES_LINGUA).build()

# LOAD THE LANGUAGE DETECTION MODEL lid218
modelLID = fasttext.load_model(
    "ai_models/language_detection/lid218e.bin")
logger.debug('LID218 MODEL LOADED')

NON_ALPHA_TOKEN_RE = re.compile(
    # using MULTILINE so that ^ means the beginning of a line
    r'(^|[\s\b])([^A-Za-z\n]+)([\s\b]|$)', re.MULTILINE)


def normalize_text(text):
    """
    Normalizes the given text by removing inconsistent data (consecutive white spaces, links, numbers etc.)
    """
    # If the description/comment is too long and has '... more' at the end of text, then remove it
    # Or if at the end of the text there are more link, it will appear the first link followed by 'and x more'
    text = re.sub(r'\.\.\.\smore|\s*and\s*\d\s*more\s*$', '', text)

    # removes  '-' characters that delimits text sequences (e.g '...text... - dupa cum reiese din articolul xyz.')
    text = re.sub(r'\s+-\s+', ' ', text)

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


def normalize_text_for_language_analysis(text):
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
