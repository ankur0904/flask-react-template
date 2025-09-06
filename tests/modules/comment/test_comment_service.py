import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from modules.application.common.types import PaginationParams, PaginationResult
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    Comment,
    CommentDeletionResult,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)


class TestCommentService(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_comment = Comment(
            id="test_comment_id",
            task_id="test_task_id",
            account_id="test_account_id",
            content="Test comment content",
            created_at=datetime.now(),
            updated_at=None,
        )

    @patch("modules.comment.comment_service.CommentWriter.create_comment")
    def test_create_comment_success(self, mock_create_comment: Mock) -> None:
        mock_create_comment.return_value = self.mock_comment

        params = CreateCommentParams(
            task_id="test_task_id", account_id="test_account_id", content="Test comment content"
        )

        result = CommentService.create_comment(params=params)

        assert result == self.mock_comment
        mock_create_comment.assert_called_once_with(params=params)

    @patch("modules.comment.comment_service.CommentReader.get_comment")
    def test_get_comment_success(self, mock_get_comment: Mock) -> None:
        mock_get_comment.return_value = self.mock_comment

        params = GetCommentParams(task_id="test_task_id", comment_id="test_comment_id", account_id="test_account_id")

        result = CommentService.get_comment(params=params)

        assert result == self.mock_comment
        mock_get_comment.assert_called_once_with(params=params)

    @patch("modules.comment.comment_service.CommentReader.get_comment")
    def test_get_comment_not_found(self, mock_get_comment: Mock) -> None:
        mock_get_comment.side_effect = CommentNotFoundError(comment_id="nonexistent_id")

        params = GetCommentParams(task_id="test_task_id", comment_id="nonexistent_id", account_id="test_account_id")

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    @patch("modules.comment.comment_service.CommentReader.get_paginated_comments")
    def test_get_paginated_comments_success(self, mock_get_paginated_comments: Mock) -> None:
        mock_pagination_result = PaginationResult(
            items=[self.mock_comment], pagination_params=PaginationParams(page=1, size=10), total_count=1, total_pages=1
        )
        mock_get_paginated_comments.return_value = mock_pagination_result

        params = GetPaginatedCommentsParams(
            task_id="test_task_id", account_id="test_account_id", pagination_params=PaginationParams(page=1, size=10)
        )

        result = CommentService.get_paginated_comments(params=params)

        assert result == mock_pagination_result
        mock_get_paginated_comments.assert_called_once_with(params=params)

    @patch("modules.comment.comment_service.CommentWriter.update_comment")
    def test_update_comment_success(self, mock_update_comment: Mock) -> None:
        updated_comment = Comment(
            id="test_comment_id",
            task_id="test_task_id",
            account_id="test_account_id",
            content="Updated comment content",
            created_at=self.mock_comment.created_at,
            updated_at=datetime.now(),
        )
        mock_update_comment.return_value = updated_comment

        params = UpdateCommentParams(
            task_id="test_task_id",
            comment_id="test_comment_id",
            account_id="test_account_id",
            content="Updated comment content",
        )

        result = CommentService.update_comment(params=params)

        assert result == updated_comment
        mock_update_comment.assert_called_once_with(params=params)

    @patch("modules.comment.comment_service.CommentWriter.update_comment")
    def test_update_comment_not_found(self, mock_update_comment: Mock) -> None:
        mock_update_comment.side_effect = CommentNotFoundError(comment_id="nonexistent_id")

        params = UpdateCommentParams(
            task_id="test_task_id", comment_id="nonexistent_id", account_id="test_account_id", content="Updated content"
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.update_comment(params=params)

    @patch("modules.comment.comment_service.CommentWriter.delete_comment")
    def test_delete_comment_success(self, mock_delete_comment: Mock) -> None:
        deletion_result = CommentDeletionResult(comment_id="test_comment_id", deleted_at=datetime.now(), success=True)
        mock_delete_comment.return_value = deletion_result

        params = DeleteCommentParams(task_id="test_task_id", comment_id="test_comment_id", account_id="test_account_id")

        result = CommentService.delete_comment(params=params)

        assert result == deletion_result
        mock_delete_comment.assert_called_once_with(params=params)

    @patch("modules.comment.comment_service.CommentWriter.delete_comment")
    def test_delete_comment_not_found(self, mock_delete_comment: Mock) -> None:
        mock_delete_comment.side_effect = CommentNotFoundError(comment_id="nonexistent_id")

        params = DeleteCommentParams(task_id="test_task_id", comment_id="nonexistent_id", account_id="test_account_id")

        with self.assertRaises(CommentNotFoundError):
            CommentService.delete_comment(params=params)
