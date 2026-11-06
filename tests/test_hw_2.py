"""API-тесты HW_2. Запуск: python -m unittest discover -s tests -v."""

import unittest

from fastapi.testclient import TestClient

from src.webhm import HW_2 as api
from src.webhm.schemas import Task


class HW2APITests(unittest.TestCase):
    def setUp(self):
        # Каждый тест получает собственное хранилище и счётчики.
        api.list_projects.clear()
        api.list_tags.clear()
        api.list_task.clear()
        api.project_id = api.tag_id = api.task_id = 1
        self.client = TestClient(api.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        api.list_projects.clear()
        api.list_tags.clear()
        api.list_task.clear()
        api.project_id = api.tag_id = api.task_id = 1

    def create_project(self, name="Учёба"):
        response = self.client.post("/projects", json={"name": name})
        self.assertEqual(response.status_code, 201)
        return response.json()

    def seed_task(self, project_id, **fields):
        # Прямое заполнение позволяет проверять остальные маршруты,
        # пока POST задач не зарегистрирован в приложении.
        task = Task(id=api.task_id, project_id=project_id, title="Домашка", **fields)
        api.task_id += 1
        api.list_task.append(task)
        return task.model_dump()

    def test_initial_lists_are_empty(self):
        for path in ("/projects", "/tags"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).json(), [])

    def test_create_and_get_projects(self):
        first = self.create_project()
        second = self.create_project("Работа")
        self.assertEqual(first, {"id": 1, "name": "Учёба", "description": None})
        self.assertEqual(second["id"], 2)
        self.assertEqual(self.client.get("/projects").json(), [first, second])
        self.assertEqual(self.client.get("/projects/1").json(), first)

    def test_invalid_project_payload(self):
        for payload in ({}, {"name": ""}, {"name": "x" * 65},
                        {"name": "OK", "description": ""}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/projects", json=payload).status_code, 422)
        self.assertEqual(api.list_projects, [])

    def test_update_project_preserves_omitted_fields(self):
        self.create_project()
        response = self.client.patch("/projects/1", json={"description": "Текст"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "Учёба", "description": "Текст"})
        response = self.client.patch("/projects/1", json={"description": None})
        self.assertIsNone(response.json()["description"])

    def test_delete_project(self):
        project = self.create_project()
        response = self.client.delete("/project/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), project)
        self.assertEqual(self.client.get("/projects/1").status_code, 404)

    def test_missing_project(self):
        for method, path, kwargs in (
            ("get", "/projects/99", {}),
            ("patch", "/projects/99", {"json": {"name": "Новое"}}),
            ("delete", "/project/99", {}),
            ("get", "/projects/99/tasks", {}),
        ):
            with self.subTest(method=method, path=path):
                self.assertEqual(self.client.request(method, path, **kwargs).status_code, 404)

    def test_invalid_path_ids(self):
        for value in ("0", "-1", "abc"):
            for path in (f"/projects/{value}", f"/tags/{value}",
                         f"/projects/{value}/tasks", f"/projects/1/tasks/{value}"):
                method = "DELETE" if path.startswith("/tags/") else "GET"
                with self.subTest(path=path):
                    self.assertEqual(self.client.request(method, path).status_code, 422)

    def test_create_list_and_delete_tags(self):
        for number, name in enumerate(("Python", "FastAPI"), start=1):
            response = self.client.post("/tags", json={"name": name})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {"id": number, "name": name})
        self.assertEqual(len(self.client.get("/tags").json()), 2)
        response = self.client.delete("/tags/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "Python"})
        self.assertEqual(self.client.get("/tags").json(), [{"id": 2, "name": "FastAPI"}])
        self.assertEqual(self.client.delete("/tags/1").status_code, 404)

    def test_invalid_tag_payload(self):
        for payload in ({}, {"name": ""}, {"name": "x" * 17}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/tags", json=payload).status_code, 422)
        self.assertEqual(api.list_tags, [])

    def test_tasks_are_filtered_by_project(self):
        self.create_project()
        self.create_project("Другой")
        task = self.seed_task(1)
        self.seed_task(2)
        self.assertEqual(self.client.get("/projects/1/tasks").json(), [task])
        response = self.client.get("/projects/1/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), task)

    def test_task_cannot_be_accessed_or_deleted_through_other_project(self):
        self.create_project()
        self.create_project("Другой")
        self.seed_task(1)
        for method in ("GET", "DELETE", "PATCH"):
            kwargs = {"json": {"status": "Завершено", "priority": "Высокий"}} if method == "PATCH" else {}
            with self.subTest(method=method):
                response = self.client.request(method, "/projects/2/tasks/1", **kwargs)
                self.assertEqual(response.status_code, 404)
        self.assertEqual(len(api.list_task), 1)
        self.assertEqual(api.list_task[0].status, "Ну ка быстро..")

    def test_missing_task_or_parent(self):
        self.create_project()
        self.seed_task(1)
        for path in ("/projects/1/tasks/99", "/projects/99/tasks/1"):
            for method in ("GET", "DELETE", "PATCH"):
                kwargs = {"json": {"status": "Завершено", "priority": "Высокий"}} if method == "PATCH" else {}
                with self.subTest(path=path, method=method):
                    self.assertEqual(self.client.request(method, path, **kwargs).status_code, 404)

    def test_delete_task(self):
        self.create_project()
        task = self.seed_task(1)
        response = self.client.delete("/projects/1/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), task)
        self.assertEqual(self.client.get("/projects/1/tasks").json(), [])

    def test_update_task_and_replace_tags(self):
        self.create_project()
        self.seed_task(1)
        tag = self.client.post("/tags", json={"name": "Python"}).json()
        payload = {"title": "Готово", "status": "Завершено", "priority": "Высокий", "tag_ids": [tag["id"]]}
        response = self.client.patch("/projects/1/tasks/1", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tags"], [tag])
        for field in ("title", "status", "priority"):
            self.assertEqual(response.json()[field], payload[field])
        payload["tag_ids"] = []
        self.assertEqual(self.client.patch("/projects/1/tasks/1", json=payload).json()["tags"], [])

    def test_update_task_rejects_unknown_tags(self):
        self.create_project()
        self.seed_task(1)
        response = self.client.patch("/projects/1/tasks/1", json={
            "status": "Ну ка быстро..", "priority": "Средний", "tag_ids": [99],
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(api.list_task[0].tags, [])

    def test_update_task_validation(self):
        self.create_project()
        self.seed_task(1)
        for invalid in ({"title": ""}, {"status": "unknown"}, {"priority": "unknown"}):
            payload = {"status": "Завершено", "priority": "Высокий", **invalid}
            with self.subTest(payload=payload):
                self.assertEqual(self.client.patch("/projects/1/tasks/1", json=payload).status_code, 422)
        self.assertEqual(api.list_task[0].status, "Ну ка быстро..")

    @unittest.expectedFailure
    def test_create_task_over_http(self):
        # Известный дефект: перед app.post(...) отсутствует @.
        self.create_project()
        response = self.client.post("/projects/1/tasks", json={"title": "Домашка"})
        self.assertIn(response.status_code, (200, 201))
        self.assertEqual(response.json()["title"], "Домашка")
        self.assertEqual(self.client.get("/projects/1/tasks").json(), [response.json()])

    @unittest.expectedFailure
    def test_partial_task_update(self):
        # Известный дефект: TaskUpdate требует status и priority.
        self.create_project()
        self.seed_task(1)
        response = self.client.patch("/projects/1/tasks/1", json={"title": "Новое"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Новое")
        self.assertEqual(response.json()["status"], "Ну ка быстро..")


if __name__ == "__main__":
    unittest.main()
