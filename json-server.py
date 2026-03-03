import json
from http.server import HTTPServer
from nss_handler import HandleRequests, status

from views import create_user, login_user, get_all_users, user_is_admin
from views import create_category, get_all_categories, delete_category
from views import (
    create_post,
    get_all_posts,
    get_single_users_post,
    get_post_details,
    edit_post

)
from views import create_comment, get_all_comments
from views import create_tag, get_all_tags, update_post_tags, delete_tag


class JSONServer(HandleRequests):

    def do_GET(self):
        """Handle GET requests from a client"""
        url = self.parse_url(self.path)

        response_body = ""

        query_params = url.get("query_params", {})

        if url["requested_resource"].lower() == "users":
            if url["pk"] != 0:
                # Gets the requested order by the id
                response_body = get_all_users(query_params)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_users(query_params)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"].lower() == "posts":

            # If there are query params, handle them first
            if len(query_params) > 0:

                if "user_id" in query_params:
                    response_body = get_single_users_post(query_params["user_id"])
                    return self.response(response_body, status.HTTP_200_SUCCESS.value)

            # Only treat as /posts/<id> if there are NO query params
            if url["pk"] != 0 and len(query_params) == 0:
                response_body = get_post_details(url["pk"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            # Default: all posts
            response_body = get_all_posts()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"].lower() == "categories":
            if url["pk"] != 0:
                # Gets the requested order by the id
                response_body = get_all_categories()
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_categories()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"].lower() == "comments":
            if url["pk"] != 0:
                # Gets the requested order by the id
                response_body = get_all_comments()
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_comments()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"].lower() == "tags":
            if url["pk"] != 0:
                response_body = get_all_tags()
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            response_body = get_all_tags()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        else:
            return self.response(
                "Resource not found",
                status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
            )

    def do_PUT(self):
        """Handle PUT requests from clients"""
        url = self.parse_url(self.path)
        pk = url.get("pk")
        resource = url.get("requested_resource").lower()

        # Handle the "undefined" string sent by React to avoid server crash

        if pk == "undefined":
            return self.response("ID in URL is undefined", status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA)

        if resource == "posts" and pk != 0:
            content_len = int(self.headers.get("content-length", 0))
            request_body = json.loads(self.rfile.read(content_len))

            # 1. Update the Post itself
            success = edit_post(pk, request_body)

            # 2. Update the Tags
            tag_ids = request_body.get("tag_ids", [])
            update_post_tags(pk, tag_ids)

            if success:
                return self.response("", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value) 
            
            return self.response("Post not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)
        
        return self.response(
                "Resource not found",
                status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
            )

    def do_DELETE(self):
        """Handle the delete requests from clients"""
        url = self.parse_url(self.path)
        pk = url["pk"]

        if url["requested_resource"].lower() == "categories":
            if pk != 0:
                successfully_deleted = delete_category(pk)
                if successfully_deleted:
                    return self.response(
                        "", status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
                    )

                return self.response(
                    "Response resource not found",
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
            except IndexError:
                return self.response("Invalid Authorization Header", 401)

            if not user_is_admin(token):
                return self.response("Forbidden: Admins only", 403)

            success = delete_tag(pk)

            if success:
                return self.response("", 204)
            else:
                return self.response("Not Found", 404)

    def do_POST(self):
        """Handles POST request from client"""

        # Parse the URL
        url = self.parse_url(self.path)

        # Get the request body
        content_len = int(self.headers.get("content-length", 0))
        request_body = self.rfile.read(content_len)
        request_body = json.loads(request_body)

        resource = url["requested_resource"]

        # Route to the function

        if resource == "register":
            response_json = create_user(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "login":
            authenticated_user = login_user(request_body)

            if authenticated_user:
                return self.response(authenticated_user, status.HTTP_200_SUCCESS.value)
            else:
                # If no user found, return a 400 or 401
                return self.response(
                    "Invalid email", status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value
                )

        if resource == "categories":
            response_json = create_category(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "comments":
            response_json = create_comment(request_body)

        if resource == "tags":
            response_json = create_tag(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        if resource == "posts":
            response_json = create_post(request_body)
            return self.response(response_json, status.HTTP_201_SUCCESS_CREATED.value)

        return self.response(
            "Requested resource not found",
            status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
        )


#
# THE CODE BELOW THIS LINE IS NOT IMPORTANT FOR REACHING YOUR LEARNING OBJECTIVES
#
def main():
    host = ""
    port = 8088
    HTTPServer((host, port), JSONServer).serve_forever()


if __name__ == "__main__":
    main()
