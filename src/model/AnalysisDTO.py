from typing import List, Dict

from pydantic import BaseModel

from src.model.enums.BigFiveModelType import BigFiveModelType
from src.model.enums.GeneralEmotionType import GeneralEmotionType
from src.model.enums.HobbyType import HobbyType
from src.model.enums.InterestDomainType import InterestDomainType
from src.model.enums.PersonalityType import PersonalityType


class AnalysisDTO(BaseModel):
    id: int
    interest_domains: List[InterestDomainType]
    hobbies: List[HobbyType]

    general_emotions: Dict[GeneralEmotionType, float]
    personality_types: Dict[PersonalityType, float]
    big_five_model: Dict[BigFiveModelType, float]

    creationDate: str  # isoFormat()

    social_account_id: int
