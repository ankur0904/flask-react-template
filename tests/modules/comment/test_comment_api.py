from server import app

from modules.authentication.types import AccessTokenErrorCode
from modules.comment.types import CommentErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", task.id, token, data=comment_data)

        assert response.status_code == 201
        assert response.json is not None
        self.assert_comment_response(
            response.json, content=self.DEFAULT_COMMENT_CONTENT, task_id=task.id, account_id=account.id
        )

    def test_create_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {}

        response = self.make_authenticated_request("POST", task.id, token, data=comment_data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request("POST", task.id, token, data=None)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Request body is required" in response.json.get("message")

    def test_create_comment_missing_token(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        url = self.get_comment_api_url(task.id)
        with app.test_client() as client:
            response = client.post(url, json=comment_data, headers=self.HEADERS)

        self.assert_error_response(response, 401, AccessTokenErrorCode.MISSING_TOKEN)

    def test_get_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_authenticated_request("GET", task.id, token, comment_id=comment.id)

        assert response.status_code == 200
        assert response.json is not None
        self.assert_comment_response(
            response.json,
            content=self.DEFAULT_COMMENT_CONTENT,
            task_id=task.id,
            account_id=account.id,
            comment_id=comment.id,
        )

    def test_get_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_paginated_comments_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create multiple comments
        self.create_test_comment(task.id, account.id, "First comment")
        self.create_test_comment(task.id, account.id, "Second comment")

        response = self.make_authenticated_request("GET", task.id, token)

        assert response.status_code == 200
        assert response.json is not None
        assert "items" in response.json
        assert "total_count" in response.json
        assert "pagination_params" in response.json
        assert response.json["total_count"] == 2
        assert len(response.json["items"]) == 2

    def test_get_paginated_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request("GET", task.id, token)

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["total_count"] == 0
        assert len(response.json["items"]) == 0

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)
        updated_content = "Updated comment content"
        update_data = {"content": updated_content}

        response = self.make_authenticated_request("PATCH", task.id, token, comment_id=comment.id, data=update_data)

        assert response.status_code == 200
        assert response.json is not None
        self.assert_comment_response(
            response.json, content=updated_content, task_id=task.id, account_id=account.id, comment_id=comment.id
        )

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)
        update_data = {}

        response = self.make_authenticated_request("PATCH", task.id, token, comment_id=comment.id, data=update_data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated content"}

        response = self.make_authenticated_request(
            "PATCH", task.id, token, comment_id=fake_comment_id, data=update_data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_authenticated_request("DELETE", task.id, token, comment_id=comment.id)

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["comment_id"] == comment.id
        assert response.json["success"] is True
        assert "deleted_at" in response.json

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_comment_isolation_between_users(self) -> None:
        """Test that users can only access their own comments"""
        # Create first user and task
        account1, token1 = self.create_account_and_get_token(username="user1@example.com")
        task1 = self.create_test_task(account1.id)
        comment1 = self.create_test_comment(task1.id, account1.id)

        # Create second user and task
        account2, token2 = self.create_account_and_get_token(username="user2@example.com")
        self.create_test_task(account2.id)

        # User2 should not be able to access User1's comment
        response = self.make_authenticated_request("GET", task1.id, token2, comment_id=comment1.id)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

        # User2 should not be able to update User1's comment
        update_data = {"content": "Hacked content"}
        response = self.make_authenticated_request("PATCH", task1.id, token2, comment_id=comment1.id, data=update_data)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

        # User2 should not be able to delete User1's comment
        response = self.make_authenticated_request("DELETE", task1.id, token2, comment_id=comment1.id)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_comment_pagination(self) -> None:
        """Test comment pagination functionality"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create 5 comments
        for i in range(5):
            self.create_test_comment(task.id, account.id, f"Comment {i + 1}")

        # Test first page with size 3
        url = f"{self.get_comment_api_url(task.id)}?page=1&size=3"
        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            response = client.get(url, headers=headers)

        assert response.status_code == 200
        assert response.json["total_count"] == 5
        assert len(response.json["items"]) == 3
        assert response.json["pagination_params"]["page"] == 1
        assert response.json["pagination_params"]["size"] == 3

        # Test second page
        url = f"{self.get_comment_api_url(task.id)}?page=2&size=3"
        with app.test_client() as client:
            response = client.get(url, headers=headers)

        assert response.status_code == 200
        assert len(response.json["items"]) == 2  # Remaining comments
