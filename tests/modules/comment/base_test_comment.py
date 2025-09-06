import json
import unittest
from typing import Tuple

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import Account, CreateAccountByUsernameAndPasswordParams
from modules.comment.comment_service import CommentService
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
from modules.comment.types import Comment, CreateCommentParams
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task


class BaseTestComment(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_COMMENT_CONTENT = "This is a test comment"
    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "This is a test task description"
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRestApiServer.create()

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    # URL HELPER METHODS

    def get_comment_api_url(self, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, task_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/tasks/{task_id}/comments/{comment_id}"

    # ACCOUNT AND TOKEN HELPER METHODS

    def create_test_account(
        self, username: str = None, password: str = None, first_name: str = None, last_name: str = None
    ) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username or self.DEFAULT_USERNAME,
                password=password or self.DEFAULT_PASSWORD,
                first_name=first_name or self.DEFAULT_FIRST_NAME,
                last_name=last_name or self.DEFAULT_LAST_NAME,
            )
        )

    def create_access_token(self, username: str = None, password: str = None) -> str:
        request_data = {"username": username or self.DEFAULT_USERNAME, "password": password or self.DEFAULT_PASSWORD}

        with app.test_client() as client:
            response = client.post(self.ACCESS_TOKEN_URL, data=json.dumps(request_data), headers=self.HEADERS)
        return response.json.get("access_token")

    def create_account_and_get_token(
        self, username: str = None, password: str = None, first_name: str = None, last_name: str = None
    ) -> Tuple[Account, str]:
        account = self.create_test_account(username, password, first_name, last_name)
        token = self.create_access_token(username, password)
        return account, token

    # TASK HELPER METHODS

    def create_test_task(self, account_id: str, title: str = None, description: str = None) -> Task:
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title=title or self.DEFAULT_TASK_TITLE,
                description=description or self.DEFAULT_TASK_DESCRIPTION,
            )
        )

    # COMMENT HELPER METHODS

    def create_test_comment(self, task_id: str, account_id: str, content: str = None) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task_id, account_id=account_id, content=content or self.DEFAULT_COMMENT_CONTENT
            )
        )

    # REQUEST HELPER METHODS

    def make_authenticated_request(
        self, method: str, task_id: str, token: str, comment_id: str = None, data: dict = None
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(task_id, comment_id)
        else:
            url = self.get_comment_api_url(task_id)

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method == "POST":
                return client.post(url, data=json.dumps(data), headers=headers)
            elif method == "GET":
                return client.get(url, headers=headers)
            elif method == "PATCH":
                return client.patch(url, data=json.dumps(data), headers=headers)
            elif method == "DELETE":
                return client.delete(url, headers=headers)

    # ASSERTION HELPER METHODS

    def assert_comment_response(
        self, comment_data: dict, content: str, task_id: str, account_id: str, comment_id: str = None
    ) -> None:
        assert comment_data.get("content") == content
        assert comment_data.get("task_id") == task_id
        assert comment_data.get("account_id") == account_id
        assert comment_data.get("created_at") is not None
        if comment_id:
            assert comment_data.get("id") == comment_id

    def assert_error_response(self, response, expected_status_code: int, expected_error_code: str) -> None:
        assert response.status_code == expected_status_code
        assert response.json is not None
        assert response.json.get("code") == expected_error_code
