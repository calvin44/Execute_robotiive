# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from fastapi import FastAPI
from pydantic import BaseModel
from robotiive.main import execute_robotiive

app = FastAPI()


class ExecutionRequest(BaseModel):
    project_name: str
    task_name: str
    external_variables: dict


@app.post("/")
def execute_task(request: ExecutionRequest):
    project_name = request.project_name
    task_name = request.task_name
    external_variables = request.external_variables

    execution_status = execute_robotiive(
        project_name, task_name, external_variables)

    return execution_status
