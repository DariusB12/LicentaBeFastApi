from pydantic import BaseModel

from model.AnalysisDTO import AnalysisDTO


class MakeAnalysisSocialAccountResponse(BaseModel):
    message: str
    status_code: int
    analysis: AnalysisDTO
