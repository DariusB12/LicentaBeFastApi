from app_requests.translation_requests.post_comment_translation import PostCommentTranslation
from app_requests.translation_requests.post_translate_request import PostTranslationRequest
from service.utils.lang_utils import normalize_text, MAX_CHARACTERS_LENGTH_LINGUA, predict_text_language_lingua, \
    predict_text_language_fasttext_lid218, normalize_text_for_language_analysis
from service.utils.translation_utils import translate_text_to_english_nllb


def detect_lang_and_translate_to_english(text: str):
    """
    Normalizes the text, and then returns it translated

    IF THE TRANSLATION OF THE TEXT IS MADE FROM ENG TO ENG THEN THE TEXT QUALITY MAY IMPROVE
    (e.g I am going tod shopd => I am going to shop)

    :param text: text to be normalized and translated
    :return: the normalized and translated text
    """
    # NORMALIZE THE TEXT
    normalized_text = normalize_text(text)

    # NORMALIZE TEXT FOR LANGUAGE DETECTION
    normalized_text_for_lang_analysis = normalize_text_for_language_analysis(normalized_text)

    # DETECT THE LANGUAGE (lingua for short text or lid218 for long texts)
    if len(normalized_text_for_lang_analysis) <= MAX_CHARACTERS_LENGTH_LINGUA:
        # DETECT THE LANGUAGE WITH LINGUA
        src_lang = predict_text_language_lingua(normalized_text_for_lang_analysis)
        print(f"Lang lingua for description:", src_lang)
    else:
        # DETECT THE LANGUAGE WITH lid218
        src_lang = predict_text_language_fasttext_lid218(normalized_text_for_lang_analysis)
        print(f"Lang lid218 for description:", src_lang)

    translated_text = translate_text_to_english_nllb(normalized_text, src_lang)
    return translated_text


def translate_post_to_english(post: PostTranslationRequest):
    """
    Normalizes the description and comments, and then translates them to english
    :param post: the post object
    :return: the description and list with all the comments translated (if after the translation a comment became empty
    then it will be removed from the list)
    """
    # TRANSLATES THE DESCRIPTION
    translated_description = detect_lang_and_translate_to_english(post.description)

    translated_comments = []
    for comment in post.comments:
        # TRANSLATES THE COMMENT
        translated_comment = detect_lang_and_translate_to_english(comment.comment)
        if translated_comment != '':
            translated_post_comment = PostCommentTranslation(id=comment.id, comment=translated_comment)
            translated_comments.append(translated_post_comment)

    return translated_description, translated_comments
