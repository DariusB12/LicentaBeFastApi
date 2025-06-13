from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app_responses.analysis.make_analysis_social_account_resp import MakeAnalysisSocialAccountResponse
from database_connection.database import get_db
from security.jwt_token import verify_token
from service.analysis_service import make_social_account_analysis

router = APIRouter(prefix="/analysis", tags=["AnalysisAPI"])


@router.post("/analyse/{social_account_id}")
def analyse_social_account(social_account_id: int, user=Depends(verify_token), db: Session = Depends(get_db)):
    """
    Analyse the social media account
    :param social_account_id: the social media account id
    :param user: the current user (token validation)
    :param db: the db connection
    :return: HTTP 200OK if the analysis was made successfully
    Throws:
        -HTTP 400 BAD_REQUEST if the social account doesn't belong to the current user
                                or if the social account doesn't exist
                                if the AI model response doesn't contain a valid json block
                                if an error occurred while parsing the json detected block
        -HTTP_503_SERVICE_UNAVAILABLE if gemini and ollama did not work properly
        -HTTP 403 FORBIDDEN if the token is invalid
    """

    analysis = make_social_account_analysis(social_account_id, user.username, db)

    # TODO: NOTIFY ANALYSIS MADE
    response = MakeAnalysisSocialAccountResponse(
        message="Analysis made successfully",
        status_code=200,
    )

    # return JSONResponse(status_code=200, content=response.dict())
    return JSONResponse(status_code=200, content=analysis.dict())
