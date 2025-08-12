import json
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models.UserData import UserData
from core.run_analysis import runAnalysis
from utils.logger import get_logger

app = FastAPI()
logger = get_logger()

class SWPRequest(BaseModel):
    user_data: UserData
    swp_mode: Literal['conservative', 'aggressive']
    pre_retirement_risk: Literal['conservative', 'aggressive', 'balanced']
    post_retirement_risk: Literal['conservative', 'aggressive', 'balanced']

@app.post('/swp-calculator')
async def swp_calculator(req: SWPRequest):
    logger.info('---------- New Request Received ----------')
    try:
        result = runAnalysis(req.user_data, req.swp_mode, req.pre_retirement_risk, req.post_retirement_risk)
        return result
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except KeyError as ke:
        logger.error(f"KeyError: {ke}")
        raise HTTPException(status_code=400, detail=f"Missing key: {ke}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
