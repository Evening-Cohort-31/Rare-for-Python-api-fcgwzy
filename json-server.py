import json
from http.server import HTTPServer
from nss_handler import HandleRequests, status

from views import (
    create_category,
    get_all_categories,
    delete_category,
    update_category,
    get_single_category,
)
from views import create_user, login_user, get_all_users, get_user_by_id, update_user, update_user_avatar, user_is_admin
from views import create_tag, get_all_tags, delete_tag, update_tag
from views import (
    create_post,
    get_all_posts,
    get_single_users_post,
    get_post_details,
    delete_post,
    update_post_tags,
    edit_post,
    get_posts_by_subscriptions,
    search_posts,
    search_posts_by_tag,
)
from views import (
    create_comment,
    get_all_comments_for_post,
    get_all_users_comments,
    update_comment,
    delete_comment
)
from views import create_subscription, get_all_subscriptions, end_subscription


class JSONServer(HandleRequests):

    def do_GET(self):
        """Handle GET requests from a client"""
        url = self.parse_url(self.path)
        query_params = url.get("query_params", {})

        if url["requested_resource"].lower() == "users":
            if url["pk"] != 0:
                response_body = get_user_by_id(url["pk"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_users(query_params)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"].lower() == "posts":
            user_id = query_params.get("user_id") or query_params.get("userId")
            follower_id = query_params.get("follower_id")

            if url["pk"] != 0:
                response_body = get_post_details(url["pk"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            user_id = query_params.get("user_id") or query_params.get("userId")
            follower_id = query_params.get("follower_id")

            if "search" in query_params: 
                response_body = search_posts(query_params["search"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            
            if "tag" in query_params:
                response_body = search_posts_by_tag(query_params["tag"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            if follower_id:
                response_body = get_posts_by_subscriptions(follower_id)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            if user_id:
                response_body = get_single_users_post(user_id)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_posts()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"].lower() == "categories":
            if url["pk"] != 0:
                response_body = get_single_category(url["pk"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            response_body = get_all_categories()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"].lower() == "tags":
            response_body = get_all_tags()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"].lower() == "subscriptions":
            response_body = get_all_subscriptions(query_params)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"].lower() == "comments":
            post_id = (
                query_params.get("post_id") or query_params.get("postId") or url["pk"]
            )
            if post_id != 0:
                response_body = get_all_comments_for_post(post_id)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            response_body = get_all_users_comments()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        return self.response(
            "Resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )

    def do_PUT(self):
        """Handle PUT requests from clients"""
        url = self.parse_url(self.path)
        pk = url.get("pk")
        resource = url.get("requested_resource").lower()

        if pk == "undefined":
            return self.response(
                "ID in URL is undefined", status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA
            )
        
        if resource == "subscriptions":
            success = end_subscription(pk)
        
            if success:
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)
            return self.response("Subscription not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)

        content_len = int(self.headers.get("content-length", 0))
        raw_body = self.rfile.read(content_len)
        request_body = json.loads(raw_body)

        if resource == "posts" and pk != 0:
            success = edit_post(pk, request_body)
            tag_ids = request_body.get("tag_ids", [])
            update_post_tags(url["pk"], tag_ids)
            if success:
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)
            return self.response(
                "Post not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND
            )

        if resource == "comments":
            success = update_comment(pk, request_body)
            if success:
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)
            return self.response(
                "Comment not found",
                status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
            )

        if resource == "categories" and url["pk"] != 0:
            update_category(url["pk"], request_body)
            return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)

        if resource == "users" and pk != 0:
            if "profile_image_url" in request_body:
                success = update_user_avatar(pk, request_body)
            else:
                success = update_user(pk, request_body)
            if success:
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)
            return self.response(
                "User not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

        if resource == "tags" and url["pk"] != 0:
            auth_header = self.headers.get("Authorization")
            if not auth_header:
                return self.response("Unauthorized", 401)
            try:
                token = auth_header.split(" ")[1]
                user_id = int(token)
            except (IndexError, ValueError, TypeError):
                return self.response("Invalid Authorization Header", 401)
            if not user_is_admin(user_id):
                return self.response("Forbidden: Admins only", 403)
            success = update_tag(url["pk"], request_body)
            if success:
                return self.response("", 204)
            return self.response("Not Found", 404)


        return self.response(
            "Resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )

    def do_DELETE(self):
        """Handle the delete requests from clients"""
        url = self.parse_url(self.path)
        pk = url["pk"]

        if url["requested_resource"].lower() == "posts":
            if pk != 0:
                delete_post(pk)
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value)

        elif url["requested_resource"].lower() == "categories":
            if pk != 0:
                successfully_deleted = delete_category(pk)
                if successfully_deleted:
                    return self.response(
                        "", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
                    )
                return self.response(
                    "Resource not found",
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )

        elif url["requested_resource"].lower() == "tags":
            if pk == 0:
                return self.response("Tag ID required", 400)
            auth_header = self.headers.get("Authorization")
            if not auth_header:
                return self.response("Unauthorized", 401)
            try:
                token = auth_header.split(" ")[1]
                user_id = int(token)
            except (IndexError, ValueError, TypeError):
                return self.response("Invalid Authorization Header", 401)
            if not user_is_admin(token):
                return self.response("Forbidden: Admins only", 403)
            success = delete_tag(pk)
            if success:
                return self.response("", 204)
            else:
                return self.response("Not Found", 404)

        elif url["requested_resource"].lower() == "comments":
            if pk != 0:
                successfully_deleted = delete_comment(pk)
                if successfully_deleted:
                    return self.response(
                        "", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
                    )
                return self.response(
                    "Resource not found",
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )

        return self.response(
            "Resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )

    def do_POST(self):
        """Handles POST request from client"""
        url = self.parse_url(self.path)

        content_len = int(self.headers.get("content-length", 0))
        request_body = self.rfile.read(content_len)
        request_body = json.loads(request_body)

        resource = url["requested_resource"]

        if resource == "register":
            response_json = create_user(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "login":
            authenticated_user = login_user(request_body)
            if authenticated_user:
                return self.response(authenticated_user, status.HTTP_200_SUCCESS.value)
            else:
                return self.response(
                    "Invalid email", status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value
                )

        if resource == "categories":
            response_json = create_category(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "comments":
            response_json = create_comment(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "tags":
            response_json = create_tag(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "posts":
            auth_header = self.headers.get("Authorization")
            if not auth_header:
                return self.response("Unauthorized", 401)
            try:
                token = auth_header.split(" ")[1]
                user_id = int(token)
            except (IndexError, ValueError, TypeError):
                return self.response("Invalid Authorization Header", 401)
            response_json = create_post(request_body, user_id)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "subscriptions":
            response_json = create_subscription(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        return self.response(
            "Requested resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )


def main():
    host = ""
    port = 8088
    HTTPServer((host, port), JSONServer).serve_forever()


if __name__ == "__main__":
    main()