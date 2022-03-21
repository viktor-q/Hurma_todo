from typing import Dict, Optional, List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from modules.storage import dao
# from modules.pinger import pinger_all_network_with_threading
from modules.security import security
from pydantic import BaseModel, Field
import json

app = FastAPI()

origins = ["*"]

# search this!11
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateNewList(BaseModel):
    list_name: str
    user_id: int

    class Config:
        schema_extra = {"example": {"list_name": "My new list", "user_id": 1}}


class NewListResponse(BaseModel):
    new_list_id: int

    class Config:
        schema_extra = {"example": {"new_list_id": 1}}


@app.post("/create-new-list", response_model=NewListResponse, description="Access bearer token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTY0Nzg1OTMyNywibmJmIjoxNjQ3ODU5MzI3LCJqdGkiOiJmZjY1Y2U2ZS0xMWZhLTQxYzktOGNkMS1hMWE4YzM2YjgwNGMiLCJleHAiOjE2NDc4NjAyMjcsInR5cGUiOiJhY2Nlc3MiLCJmcmVzaCI6ZmFsc2V9.RbjM47WNf-TUY3tUmfD0wF4OBeqW85UsgSL9z2DWuig")
async def create_new_list(pushed_json: CreateNewList, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    create_list = dao.DAO().create_list(pushed_json.list_name, pushed_json.user_id)

    return NewListResponse(new_list_id=create_list)


class CreateNewTask(BaseModel):
    list_id: int
    data: str
    priority: int
    status: int

    class Config:
        schema_extra = {"example": {"list_id": 1, "data": "Some text", "priority": 1, "status": 1}}


class NewTaskResponse(BaseModel):
    new_task_id: int

    class Config:
        schema_extra = {"example": {"new_task_id": 1}}


@app.post("/create-new-task", response_model=NewTaskResponse)
async def create_new_task(pushed_json: CreateNewTask):
    create_task = dao.DAO().create_task(
        pushed_json.list_id, pushed_json.data, pushed_json.priority, pushed_json.status
    )

    return NewTaskResponse(new_task_id=create_task)


# class ReadListsById(BaseModel):
#     userid: int
#
#     class Config:
#         schema_extra = {"example": {"userid": 1}}


class ReadListsIdResponse(BaseModel):
    list_id: int
    list_name: str
    user_id: int

    class Config:
        schema_extra = {"example": [{"list_id": 1, "list_name": "My list", "user_id": 1}]}


@app.get("/read-lists-by-id/{user_id}", response_model=List[ReadListsIdResponse])
async def read_lists_by_id(user_id: int):
    readed_lists = dao.DAO().read_lists_by_userid(user_id)
    return readed_lists


# class ReadTasksByListId(BaseModel):
#     list_id: int
#
#     class Config:
#         schema_extra = {"example": {"list_id": 1}}


class ReadTasksByListIdResponse(BaseModel):
    task_id: int
    list_id: int
    data: str
    priority: int
    status: int
    created_datetime: str
    edite_datetime: Optional[str] = None

    class Config:
        schema_extra = {
            "example": [{
                "task_id": 1,
                "list_id": 1,
                "data": "Some text",
                "priority": 1,
                "status": 1,
                "created_datetime": "2022-03-14 18:00:00",
                "edite_datetime": "2022-03-14 19:00:00",
            }]
        }


@app.get("/read-tasks-by-list-id/{list_id}", response_model=List[ReadTasksByListIdResponse])
async def read_lists_by_id(list_id: int):
    readed_tasks = dao.DAO().read_tasks_by_list_id(list_id)

    return readed_tasks


# Auth block

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()

class User(BaseModel):
    login: str
    password: str

class ReturnLoginUser(BaseModel):
    access_token: str

    class Config:
        schema_extra = {"access_token": "blabla123bla456"}


@app.get("/login-user", response_model=ReturnLoginUser)
async def login_user(data: User, Authorize: AuthJWT = Depends()) -> dict:
    new_class = security.CustomSecurity()
    response_check_pass_in_db = new_class.check_user(data.login, data.password)
    if response_check_pass_in_db["status_pass"] == "BAD":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=data.login)
    return {"access_token": access_token}


# admin/admin/  "new_user_id": 1
@app.get("/create-user")
async def create_user(data: User):
    new_class = security.CustomSecurity()
    new_user_id = new_class.registration_new_user(data.login, data.password)
    return {"new_user_id": new_user_id}


# exception handler for authjwt
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
