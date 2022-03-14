from typing import Dict, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from fastapi_jwt_auth import AuthJWT
# from fastapi_jwt_auth.exceptions import AuthJWTException
from modules.storage import dao
# from modules.pinger import pinger_all_network_with_threading
# from modules.security import security
from pydantic import BaseModel, Field

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


@app.post("/create-new-list", response_model=NewListResponse)
async def create_new_list(pushed_json: CreateNewList):
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


class ReadListsById(BaseModel):
    userid: int

    class Config:
        schema_extra = {"example": {"userid": 1}}


class ReadListsIdResponse(BaseModel):
    list_id: int
    list_name: str

    class Config:
        schema_extra = {"example": {"list_id": 1, "list_name": "My list"}}


@app.get("/read-lists-by-id", response_model=ReadListsIdResponse)
async def read_lists_by_id(pushed_json: ReadListsById):
    readed_lists = dao.DAO().read_lists_by_userid(pushed_json.userid)

    return {readed_lists}


class ReadTasksByListId(BaseModel):
    list_id: int

    class Config:
        schema_extra = {"example": {"list_id": 1}}


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
            "example": {
                "task_id": 1,
                "list_id": 1,
                "data": "Some text",
                "priority": 1,
                "status": 1,
                "created_datetime": "2022-03-14 18:00:00",
                "edite_datetime": "2022-03-14 19:00:00",
            }
        }


@app.get("/read-tasks-by-list-id", response_model=ReadTasksByListIdResponse)
async def read_lists_by_id(pushed_json: ReadTasksByListId):
    readed_tasks = dao.DAO().read_tasks_by_list_id(pushed_json.list_id)

    return readed_tasks


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
