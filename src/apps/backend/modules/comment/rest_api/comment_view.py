from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.application.common.constants import DEFAULT_PAGINATION_PARAMS
from modules.application.common.types import PaginationParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentBadRequestError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, task_id: str, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError(message="Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError(message="Content is required")

        create_comment_params = CreateCommentParams(
            task_id=task_id, account_id=account_id, content=request_data["content"]
        )

        created_comment = CommentService.create_comment(params=create_comment_params)
        comment_dict = asdict(created_comment)

        return jsonify(comment_dict), 201

    @access_auth_middleware
    def get(self, task_id: str, account_id: str, comment_id: Optional[str] = None) -> ResponseReturnValue:
        if comment_id:
            comment_params = GetCommentParams(task_id=task_id, comment_id=comment_id, account_id=account_id)
            comment = CommentService.get_comment(params=comment_params)
            comment_dict = asdict(comment)
            return jsonify(comment_dict)
        else:
            # Get paginated comments for the task
            page = int(request.args.get("page", DEFAULT_PAGINATION_PARAMS.page))
            size = int(request.args.get("size", DEFAULT_PAGINATION_PARAMS.size))

            pagination_params = PaginationParams(page=page, size=size)
            get_comments_params = GetPaginatedCommentsParams(
                task_id=task_id, account_id=account_id, pagination_params=pagination_params
            )

            paginated_comments = CommentService.get_paginated_comments(params=get_comments_params)
            paginated_comments_dict = asdict(paginated_comments)

            return jsonify(paginated_comments_dict)

    @access_auth_middleware
    def patch(self, task_id: str, comment_id: str, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError(message="Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError(message="Content is required")

        update_comment_params = UpdateCommentParams(
            task_id=task_id, comment_id=comment_id, account_id=account_id, content=request_data["content"]
        )

        updated_comment = CommentService.update_comment(params=update_comment_params)
        comment_dict = asdict(updated_comment)

        return jsonify(comment_dict)

    @access_auth_middleware
    def delete(self, task_id: str, comment_id: str, account_id: str) -> ResponseReturnValue:
        delete_comment_params = DeleteCommentParams(task_id=task_id, comment_id=comment_id, account_id=account_id)

        deletion_result = CommentService.delete_comment(params=delete_comment_params)
        deletion_result_dict = asdict(deletion_result)

        return jsonify(deletion_result_dict)
