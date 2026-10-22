from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Path, status

# Явное лучше неявного: https://peps.python.org/pep-0020/
from src.webhm.schemas import CreateProject, Project, ProjectUpdate


app = FastAPI()

# "База данных" всех созданных проектов
list_projects: list[Project] = []
project_id = 1


@app.get("/projects")
def get_projects() -> list[Project]:
    return list_projects


@app.get("/projects/{id}")
def get_project_by_id(id: Annotated[int, Path(gt=0)]) -> Project:
    project = next((p for p in list_projects if p.id == id), None)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return project


@app.post(
    "/projects", status_code=status.HTTP_201_CREATED
)  # Код 201 используется для успешного создания ресурса
def create_project(payload: Annotated[CreateProject, Body()]) -> Project:
    # payload - термин обозначющий "полезные данные", которые передаются в запросе
    global project_id
    new_project = Project(id=project_id, **payload.model_dump())
    list_projects.append(new_project)
    project_id += 1
    return new_project


@app.patch("/projects/{project_id}")
def update_project(
    project_id: Annotated[int, Path(gt=0)], payload: Annotated[ProjectUpdate, Body()]
) -> Project:

    project = next((pro for pro in list_projects if pro.id == project_id), None)

    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if payload.name is not None:
        project.name = payload.name

    if payload.description is not None:
        project.description = payload.description

    return project
