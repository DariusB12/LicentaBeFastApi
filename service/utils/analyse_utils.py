import json
from datetime import datetime
from typing import List, Dict, Any
import re

from starlette import status

from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger
from model.AnalysisDTO import AnalysisDTO
from model.entities import SocialMediaAccount
from model.enums.BigFiveModelType import BigFiveModelType
from model.enums.GeneralEmotionType import GeneralEmotionType
from model.enums.HobbyType import HobbyType
from model.enums.InterestDomainType import InterestDomainType
from model.enums.PersonalityType import PersonalityType
from service.utils.photos_utils import get_photo_base64


def get_analysis_prompt_images(social_account: SocialMediaAccount) -> (str, List[str]):
    """
    Generates the prompt for AI multimodal models to analyse the social media account, along with a list of the
    social account images in base64 format, ordered by their appearance in the prompt
    :param social_account: the social account to be analysed
    :return: the generated prompt and the ordered list with the images in base64
    """
    prompt_parts = []
    all_images_base64_ordered = []
    image_placeholder_counter = 0

    prompt_parts.append(
        "Perform a comprehensive personality analysis of the following social media account. Analyze the user's interests, hobbies, general emotions, personality types, and Big Five personality traits based on all provided information (profile details, posts details, and all associated images).")
    prompt_parts.append(
        "Return the analysis strictly as a JSON object, matching the structure and types defined below. Ensure all required fields for the Big Five Model are present, even if their percentage is 0.0.")
    prompt_parts.append("\n--- Account Details ---")
    prompt_parts.append(f"Username: {social_account.username}")
    prompt_parts.append(f"Profile Description: {social_account.profile_description}")
    prompt_parts.append(f"Followers: {social_account.no_followers}")
    prompt_parts.append(f"Following: {social_account.no_following}")
    prompt_parts.append(f"Number of Posts: {social_account.no_of_posts}")

    # Add profile photo
    prompt_parts.append("\n--- Profile Photo ---")
    image_placeholder_counter += 1
    prompt_parts.append(f"Profile Photo: [IMAGE_{image_placeholder_counter}]")
    all_images_base64_ordered.append(get_photo_base64(social_account.profile_photo_filename))

    prompt_parts.append("\n--- Posts and Their Contents ---")
    for i, post in enumerate(social_account.posts):
        prompt_parts.append(f"\n**Post {i + 1}:**")  # Added index i for clearer context if needed
        prompt_parts.append(f"  Description: {post.description}")
        prompt_parts.append(f"  No of likes: {"private" if post.noLikes == -1 else post.noLikes}")
        prompt_parts.append(f"  No of comments: {"private" if post.noComments == -1 else post.noComments}")
        prompt_parts.append(f"  Date Posted: {post.datePosted.strftime('%Y-%m-%d')}")

        if len(post.photos) > 0:
            prompt_parts.append("  Associated Images:")
            for photo in post.photos:
                image_placeholder_counter += 1
                prompt_parts.append(f"    [IMAGE_{image_placeholder_counter}]")
                all_images_base64_ordered.append(get_photo_base64(photo.post_photo_filename))
        else:
            prompt_parts.append("  No images associated with this post.")

        if len(post.comments) > 0:
            prompt_parts.append("  Associated Comments:")
            for j, comment in enumerate(post.comments):
                prompt_parts.append(f"\n**Comment {j + 1}:**")  # Added index j for clearer context if needed
                prompt_parts.append(f"  Content: {comment.content}")
        else:
            prompt_parts.append("  No comments associated with this post.")

    prompt_parts.append("\n--- Analysis Requirements ---")
    prompt_parts.append(
        "Your response MUST be a JSON object with the following structure. Strictly adhere to the provided enum values for lists and dictionary keys. If a specific item (e.g., a hobby) cannot be clearly identified, omit it from the list/dictionary. For dictionary values, use float percentages from 0.0 to 1.0.")

    prompt_parts.append("\n**JSON Structure:**")
    prompt_parts.append(json.dumps({
        "interest_domains": [e.value for e in InterestDomainType],
        "hobbies": [e.value for e in HobbyType],
        "general_emotions": {e.value: 0.0 for e in GeneralEmotionType},
        "personality_types": {e.value: 0.0 for e in PersonalityType},
        "big_five_model": {e.value: 0.0 for e in BigFiveModelType},
    }, indent=2))

    prompt_parts.append("\n**Specific Instructions for Each Field:**")
    prompt_parts.append(
        f"1.  **interest_domains (List of Strings):** Identify the main topics or themes of interest based on profile description, post texts, and images. Only use values from the `InterestDomainType` enum: {', '.join([e.value for e in InterestDomainType])} . Include only topics or themes of interest identified.")
    prompt_parts.append(
        f"2.  **hobbies (List of Strings):** Identify activities or hobbies based on profile description, post texts, and images. Only use values from the `HobbyType` enum: {', '.join([e.value for e in HobbyType])} . Include only hobbies identified.")
    prompt_parts.append(
        f"3.  **general_emotions (Dictionary: String -> Float):** Estimate the predominant emotions based on profile description, post texts, images, no of likes, no of comments, no of posts and post dates. Keys MUST be from `GeneralEmotionType` enum. Values are percentages (0.0 to 1.0). Include only emotions identified.")
    prompt_parts.append(
        f"4.  **personality_types (Dictionary: String -> Float):** Infer personality traits based on profile description, post texts, images, no of likes, no of comments, no of posts and post dates. Keys MUST be from `PersonalityType` enum. Values are percentages (0.0 to 1.0). Include only traits identified.")
    prompt_parts.append(
        f"5.  **big_five_model (Dictionary: String -> Float):** Provide percentages (0.0 to 1.0) for ALL five traits based on profile description, post texts, images, no of likes, no of comments, no of posts and post dates. Keys MUST be from `BigFiveModelType` enum. You MUST include ALL five: {', '.join([e.value for e in BigFiveModelType])}, even if the percentage is 0.0.")

    prompt_parts.append("\nYour response must be ONLY the JSON object, nothing else.")

    return "\n".join(prompt_parts), all_images_base64_ordered


def parse_analysis_json_response(response: str, social_account_id: int) -> AnalysisDTO:
    """
    Converts a string which is a json object representing the analysis made by the AI models.
    The response is expected to be like the following:
    ```json\n{\n  \"interest_domains\": [\n    \"TECHNOLOGY\",\n    \"SPORTS\",\n    \"ENTERTAINMENT\",\n    \"RELATIONSHIPS\",\n    \"TRAVELLING\"\n  ],\n  \"hobbies\": [\n    \"GYM\",\n    \"TRAVELLING\",\n    \"READING\",\n    \"LISTENING_TO_MUSIC\",\n    \"WATCHING_MOVIES\"\n  ],\n  \"general_emotions\": {\n    \"HAPPY\": 0.3,\n    \"MOTIVATED\": 0.6\n  },\n  \"personality_types\": {\n    \"CURIOUS\": 0.7,\n    \"FUNNY\": 0.4,\n    \"ADVENTUROUS\": 0.5\n  },\n  \"big_five_model\": {\n    \"OPENNESS\": 0.6,\n    \"CONSCIENTIOUSNESS\": 0.3,\n    \"EXTRAVERSION\": 0.5,\n    \"AGREEABLENESS\": 0.4,\n    \"NEUROTICISM\": 0.2\n  }\n}\n```

    :param social_account_id: the id of the social account to add the analysis
    :param response: the string response of the AI model
    :return: the AnalysisDTO entity obtained from the response
    Throws:
        -HTTP_400_BAD_REQUEST if the response doesn't contain a valid json block
                                if an error occurred while parsing the json detected block

    """

    try:
        # EXTRACT THE JSON STRING
        match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)

        if not match:
            logger.error("No valid JSON block detected")
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Analysis could not be made, gemmini and ollama did not work properly."
            )

        # THE FIRST MATCHING GROUP CONTAINS THE JSON
        json_string_clean = match.group(1)

        # PARSE THE JSON STRING INTO A PYTHON DICTIONARY
        parsed_data: Dict[str, Any] = json.loads(json_string_clean)

        # FILTER THE VALUES FORM JSON SO THAT ONLY THE VALUES PRESENT IN THE ENUMS ARE TAKEN

        # Filter interest_domains (List of Strings)
        if "interest_domains" in parsed_data and isinstance(parsed_data["interest_domains"], list):
            parsed_data["interest_domains"] = [
                val for val in parsed_data["interest_domains"]
                if isinstance(val, str) and val in [e.value for e in InterestDomainType]
            ]
            if not parsed_data["interest_domains"]:  # Ensure it's not empty if nothing valid was found
                parsed_data["interest_domains"] = []

        # Filter hobbies (List of Strings)
        if "hobbies" in parsed_data and isinstance(parsed_data["hobbies"], list):
            parsed_data["hobbies"] = [
                val for val in parsed_data["hobbies"]
                if isinstance(val, str) and val in [e.value for e in HobbyType]
            ]
            if not parsed_data["hobbies"]:  # Ensure it's not empty if nothing valid was found
                parsed_data["hobbies"] = []

        # Filter general_emotions (Dictionary: String -> Float)
        if "general_emotions" in parsed_data and isinstance(parsed_data["general_emotions"], dict):
            parsed_data["general_emotions"] = {
                key: val for key, val in parsed_data["general_emotions"].items()
                if
                isinstance(key, str) and key in [e.value for e in GeneralEmotionType] and isinstance(val, (int, float))
            }
            if not parsed_data["general_emotions"]:  # Ensure it's not empty if nothing valid was found
                parsed_data["general_emotions"] = {}

        # Filter personality_types (Dictionary: String -> Float)
        if "personality_types" in parsed_data and isinstance(parsed_data["personality_types"], dict):
            parsed_data["personality_types"] = {
                key: val for key, val in parsed_data["personality_types"].items()
                if isinstance(key, str) and key in [e.value for e in PersonalityType] and isinstance(val, (int, float))
            }
            if not parsed_data["personality_types"]:  # Ensure it's not empty if nothing valid was found
                parsed_data["personality_types"] = {}

        #Filter BigFiveModelType
        temp_big_five_model = {}
        if "big_five_model" in parsed_data and isinstance(parsed_data["big_five_model"], dict):
            for key, val in parsed_data["big_five_model"].items():
                if isinstance(key, str) and key in [e.value for e in BigFiveModelType] and isinstance(val,
                                                                                                      (int, float)):
                    temp_big_five_model[key] = val
        parsed_data["big_five_model"] = temp_big_five_model

        # Ensure all required BigFiveModelType keys are present with a default of 0.0
        for enum_member in BigFiveModelType:
            if enum_member.value not in parsed_data["big_five_model"]:
                parsed_data["big_five_model"][enum_member.value] = 0.0

        # ADD THE REST OF THE ATTRIBUTES
        parsed_data["creationDate"] = datetime.now().isoformat()
        parsed_data["social_account_id"] = social_account_id

        # Create the AnalysisDTO using the dictionary
        # Pydantic will make automatically the conversion
        analysis_dto = AnalysisDTO(**parsed_data)

        # Remove 0.0 values from GeneralEmotionType and PersonalityType
        # Filter GeneralEmotionType
        filtered_emotions = {
            key: value for key, value in analysis_dto.general_emotions.items()
            if value != 0.0  # Keep if value is not 0.0
        }
        analysis_dto.general_emotions = filtered_emotions

        # Filter PersonalityType
        filtered_personalities = {
            key: value for key, value in analysis_dto.personality_types.items()
            if value != 0.0  # Keep if value is not 0.0
        }
        analysis_dto.personality_types = filtered_personalities

        return analysis_dto

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing the JSON: {e}")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Error parsing the JSON: {e}"
        )
    except Exception as e:
        logger.error(f"Error parsing the JSON: {e}")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Error parsing the JSON: {e}"
        )
