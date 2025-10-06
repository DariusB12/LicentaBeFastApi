import base64
import json
import os

# import ollama
from sqlalchemy.orm import Session
from starlette import status

from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger
from model.AnalysisDTO import AnalysisDTO
from google import genai
from google.genai import types
from model.entities import SocialMediaAccount
from repo.social_account_repo import get_user_social_account, add_social_account_analysis_repo
from service.utils.analyse_utils import get_analysis_prompt_images, parse_analysis_json_response

# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# response = ollama.chat(model=OLLAMA_MODEL)
# logger.debug(f'OLLAMA MODELS LOADED - {OLLAMA_MODEL}')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set!")
if not GEMINI_MODEL_NAME:
    logger.error("GEMINI_MODEL_NAME environment variable not set!")

# genai.configure(api_key=GEMINI_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

def analyse_social_account(social_account: SocialMediaAccount) -> AnalysisDTO:
    """
    Creates the analysis of the given social account using gemini flash 2.0 API
    If the gemini api fails (no network connection, or server crash) then we use Ollama gemma3:4b-it-qat local model
    Gemini is faster, gemma takes around 5 minutes to generate the analysis (for a medium social account content size)
    :param social_account: the social media account
    :return: the analysis of the social media account
    Throws:
        -HTTP_503_SERVICE_UNAVAILABLE if gemini and ollama did not work properly
        -HTTP_400_BAD_REQUEST if the response doesn't contain a valid json block
                                if an error occurred while parsing the json detected block
    """
    prompt, images = get_analysis_prompt_images(social_account)
    logger.debug(f"Generated prompt:\n{prompt}")
    try:
        # model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        contents = []
        # PASS THE IMAGES IN THE ORDER THEY APPEAR IN PROMPT
        # for img_base64 in images:
        #     contents.append({
        #         "inline_data": {
        #             "mime_type": 'image/png',
        #             "data": img_base64,
        #         }
        #     })
        for img_base64 in images:
            try:
                image_bytes = base64.b64decode(img_base64)
                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/png'
                    )
                )
            except Exception as e:
                logger.error(f"Error decoding image base64: {e}")

        # PASS THE PROMPT
        # contents.append({"text": prompt})
        contents.append(types.Part.from_text(text=prompt))

        # DEBUG PURPOSE, VERIFY THE TOKEN SIZE (GEMINI FLASH 2.0 MAX 1M TOKENS PER MINUTE)
        # try:
        #     token_count_response = model.count_tokens(contents)
        #     total_tokens = token_count_response.total_tokens
        #     logger.debug(f"Token count for this request: {total_tokens} tokens")
        # except Exception as e:
        #     logger.error(f"Error counting tokens: {e}")
        try:
            token_count_response = client.models.count_tokens(
                model=GEMINI_MODEL_NAME,
                contents=contents
            )
            total_tokens = token_count_response.total_tokens
            logger.debug(f"Token count for this request: {total_tokens} tokens")
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")

        # response_gemini = model.generate_content(contents)
        response_gemini = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=contents
        )
        logger.debug(response_gemini)

        # EXTRACT THE GENERATED RESPONSE
        # analysis = parse_analysis_json_response(response_gemini.to_dict()["candidates"][0]["content"]["parts"][0]["text"], social_account.id)
        analysis = parse_analysis_json_response(response_gemini.text, social_account.id)

        return analysis
    # IF THROWN JSON PARSE ERRORS, THEN WE RAISE AGAIN THE ERROR, IF ANY OTHER ERR HAPPENED (GEMINI API) THEN TRY OLLAMA
    except CustomHTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error calling GEMINI model")
        raise CustomHTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Analysis could not be made, gemmini did not work properly."
        )
    # except Exception as e:
    #     logger.error(f"Error calling Gemini API: {e}")
    #     logger.debug(f"Using Ollama {OLLAMA_MODEL} model for analysis")
    #     # IF GEMINI FAILS WE USE A LOCAL STORED MULTIMODAL MODEL WITH OLLAMA
    #     try:
    #         response_ollama = ollama.chat(
    #             model=OLLAMA_MODEL,
    #             messages=[{
    #                 'role': 'user',
    #                 'content': prompt,
    #                 'images': images
    #             }]
    #         )
    #         logger.debug(response_ollama)
    #
    #         # EXTRACT THE GENERATED RESPONSE
    #         analysis = parse_analysis_json_response(response_ollama.message.content, social_account.id)
    #
    #         return analysis
    #     except Exception as e:
    #         logger.error(f"Error calling Ollama {OLLAMA_MODEL} model")
    #         raise CustomHTTPException(
    #             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #             message="Analysis could not be made, gemmini and ollama did not work properly."
    #         )


def make_social_account_analysis(social_account_id: int, username: str, db: Session) -> AnalysisDTO:
    """
    Creates the social account analysis
    :param social_account_id: the social account id
    :param username: the current user username
    :param db: the db connection
    :return: the analysis made
    Throws:
        -HTTP 400 BAD_REQUEST if the social account doesn't belong to the current user
                                or if the social account doesn't exist
                                if the AI model response doesn't contain a valid json block
                                if an error occurred while parsing the json detected block
        -HTTP_503_SERVICE_UNAVAILABLE if gemini and ollama did not work properly
    """
    social_account = get_user_social_account(social_account_id, username, db)

    analysis = analyse_social_account(social_account)

    analysis_id = add_social_account_analysis_repo(analysis, username, db)
    analysis.id = analysis_id

    return analysis
