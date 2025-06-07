import re

import ctranslate2
import transformers

from service.utils.lang_utils import COMMON_LANGUAGES

# LOAD THE NLLB MODEL
translator = ctranslate2.Translator("ai_models/nllb/nllb-200-distilled-600M-ctranslate2", device='cuda')

# load all the tokenizers for all the languages when starting the app, in order to cut down on waiting time
tokenizers_dict = {
    'fra': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='fra_Latn',
                                                      clean_up_tokenization_spaces=True),
    'spa': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='spa_Latn',
                                                      clean_up_tokenization_spaces=True),
    'deu': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='deu_Latn',
                                                      clean_up_tokenization_spaces=True),
    'ita': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='ita_Latn',
                                                      clean_up_tokenization_spaces=True),
    'ron': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='ron_Latn',
                                                      clean_up_tokenization_spaces=True),
    'por': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='por_Latn',
                                                      clean_up_tokenization_spaces=True),
    'eng': transformers.AutoTokenizer.from_pretrained("ai_models/nllb/nllb-200-distilled-600M-ctranslate2",
                                                      src_lang='eng_Latn')
}


def split_sentences(text):
    """
    Splits the given text into sentences, using the punctuation marks .,?,!
    :param text: the text to pe split
    :return: the split sentences

    ?<= is positive lookbehind e.g (?<=foo)bar => finds the 1st bar ("bar" which has "foo" before it)
    .strip() => " Hello there! " becomes "Hello there!" (removes unnecessary whitespaces)
    """
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def translate_text_to_english_nllb(txt, src_lang):
    """
    Translates a given text from a specified source language to English using the NLLB (No Language Left Behind) model.
    If the source language is not present in the COMMON_LANGUAGES list then the text won't be translated

    IF THE TRANSLATION OF THE TEXT IS MADE FROM ENG TO ENG THEN THE TEXT QUALITY MAY IMPROVE
    (e.g I am going tod shopd => I am going to shop)

    :param txt: the input text to be translated
    :param src_lang: the source language code in iso_code_639_3 format
    :return: the translated text in English, or the original text if src_lang is not in the COMMON_LANGUAGES list
    """
    if src_lang not in COMMON_LANGUAGES:
        return txt
    tgt_lang = "eng_Latn"
    sentences = split_sentences(txt)
    translated_sentences = []

    print(f"\nTRANSLATE: {txt}")
    for sentence in sentences:
        tokens = tokenizers_dict[src_lang].convert_ids_to_tokens(tokenizers_dict[src_lang].encode(sentence))
        result = translator.translate_batch([tokens], target_prefix=[[tgt_lang]])[0]
        translated = tokenizers_dict[src_lang].decode(
            tokenizers_dict[src_lang].convert_tokens_to_ids(result.hypotheses[0][1:]))
        translated_sentences.append(translated.strip())

    translated_text = " ".join(translated_sentences)
    # remove the <unk> tags added by NLLB for unknown characters
    translated_text = re.sub(r'<unk>', '', translated_text)
    print(f"\nTRANSLATED: {translated_text}")

    return translated_text
