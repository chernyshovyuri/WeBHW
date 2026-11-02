from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Path, status

# Явное лучше неявного: https://peps.python.org/pep-0020/
from src.webhm.schemas import (
    CreateProject,
    Project,
    ProjectUpdate,
    Tag,
    Task,
    CreateTag,
)


app = FastAPI()

# "База данных" всех созданных проектов
list_projects: list[Project] = []
project_id = 1

list_tags: list[Tag] = []
tag_id = 1

list_task: list[Task] = []
task_id = 1

ProjectId = Annotated[int, Path(gt=0)]


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
    project_id: ProjectId, payload: Annotated[ProjectUpdate, Body()]
) -> Project:

    project = next((pro for pro in list_projects if pro.id == project_id), None)

    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    target = payload.model_fields_set

    if "name" in target:
        project.name = payload.name

    if "description" in target:
        project.description = payload.description

    return project


@app.delete("/project/{project_id}")
def delete_project(project_id: ProjectId) -> Project:

    id_project = next((pro for pro in list_projects if pro.id == project_id), None)

    if id_project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    list_projects.remove(id_project)

    return id_project

    """
    тут еще нужно сделать каскадное удваление задач как это сделать?
    
    """


@app.get("/tags")
def get_tags() -> list[Tag]:
    return list_tags


@app.post("/tags", status_code=status.HTTP_201_CREATED)
def post_tags(payload: Annotated[CreateTag, Body()]) -> Tag:

    global tag_id

    new_tags = Tag(id=tag_id, **payload.model_dump())

    list_tags.append(new_tags)

    tag_id += 1

    return new_tags


@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: Annotated[int, Path(gt=0)]):

    id_tag = next((tag for tag in list_tags if tag.id == tag_id), None)

    if id_tag is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    list_tags.remove(id_tag)

    return id_tag
