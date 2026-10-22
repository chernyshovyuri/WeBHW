from typing import Literal
from pydantic import BaseModel, Field


Status = Literal["Ну ка быстро..", "Выполняется", "Завершено"]
Priority = Literal["Низкий", "Средний", "Высокий"]


class Tag(BaseModel):
    """Тег для группировки задач; используется в ответах API и списке тегов задачи."""

    id: int = Field(description="id для тэга")
    name: str = Field(min_length=1, max_length=16, description="Наименование тега")


class Project(BaseModel):
    """Проект, объединяющий задачи; используется для хранения и ответа API."""

    id: int = Field(description="id проекта")
    name: str = Field(min_length=1, max_length=64, description="имя проекта")
    description: str | None = Field(None, min_length=1, description="Описание проекта")


class CreateProject(BaseModel):
    """Данные запроса на создание проекта; проверяет название и описание без ID."""

    name: str = Field(min_length=1, max_length=64, description="имя проекта")
    description: str | None = Field(None, min_length=1, description="Описание проекта")


class Task(BaseModel):
    """Задача проекта со статусом, приоритетом и тегами; используется для хранения и ответа API."""

    id: int = Field(description="id для задачи")
    project_id: int = Field(description="id проекта")
    title: str = Field(min_length=1, max_length=64, description="Название задачи")
    description: str | None = Field(None, min_length=1, description="Описание задачи")
    status: Status = Field("Ну ка быстро..", description="Статус задачи")
    priority: Priority = Field("Средний", description="Приоритет задачи")
    tags: list[Tag] = Field(default_factory=list, description="Список тегов")


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=64, description="имя проекта"
    )
    description: str | None = Field(None, min_length=1, description="Описание проекта")


class TaskUpdate(BaseModel):
    title: str | None = Field(
        None, min_length=1, max_length=64, description="Название задачи"
    )
    description: str | None = Field(None, min_length=1, description="Описание задачи")
    status: Status | None = Field(None, description="Статус задачи")
    priority: Priority | None = Field(None, description="Приоритет задачи")
    tag_ids: list[int] | None = Field(None, description="Список тегов")


class CreateTag(BaseModel):
    name: str = Field(min_length=1, max_length=16, description="Наименование тега")


class CreateTask(BaseModel):
    title: str = Field(min_length=1, max_length=64, description="Название задачи")
    description: str | None = Field(None, min_length=1, description="Описание задачи")
    status: Status = Field("Ну ка быстро..", description="Статус задачи")
    priority: Priority = Field("Средний", description="Приоритет задачи")
    tag_ids: list[int] = Field(default_factory=list, description="Список тегов")
