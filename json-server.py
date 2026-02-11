import json
from http.server import HTTPServer
from nss_handler import HandleRequests, status

from views import create_user, login_user, get_all_users, get_single_user

class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for shipping ships"""

    def do_GET(self):
        """Handle GET requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)

        query_params = url.get("query_params", {})

        if url["requested_resource"].lower() == "users":
            if url["pk"] != 0:
                # Gets the requested order by the id
                response_body = get_all_users(query_params)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            

            response_body = get_all_users(query_params)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        else:
            return self.response("Resource not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)


    def do_PUT(self):
        """Handle PUT requests from clients"""
        pass

    def do_DELETE(self):
        """Handle the delete requests from clients"""
        pass

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
                return self.response("Invalid email", status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value)
                    

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
