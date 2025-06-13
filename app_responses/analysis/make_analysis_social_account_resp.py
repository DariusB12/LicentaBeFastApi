from pydantic import BaseModel


class MakeAnalysisSocialAccountResponse(BaseModel):
    message: str
    status_code: int