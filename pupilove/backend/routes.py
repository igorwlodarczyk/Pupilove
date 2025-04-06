from fastapi import APIRouter, Depends
from database import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/execute-select", response_class=JSONResponse)
def query_input_form(query: str, db=Depends(get_db_connection)):
    return db.execute_select(query)
