from typing import List, Dict

from pydantic import BaseModel

from model.enums.BigFiveModelType import BigFiveModelType
from model.enums.GeneralEmotionType import GeneralEmotionType
from model.enums.HobbyType import HobbyType
from model.enums.InterestDomainType import InterestDomainType
from model.enums.PersonalityType import PersonalityType


class AnalysisDTO(BaseModel):
    id: int
    interest_domains: List[InterestDomainType]
    hobbies: List[HobbyType]

    general_emotions: Dict[GeneralEmotionType, float]
    personality_types: Dict[PersonalityType, float]
    big_five_model: Dict[BigFiveModelType, float]

    creationDate: str  # isoFormat()

    social_account_id: int
