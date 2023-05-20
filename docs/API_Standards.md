# API Standards

Every API does things a bit differently. This document specifies the high-level standards that
this project adheres to

## HTTP Status Code Meanings

HTTP status codes:

| HTTP Status               | HTTP verb meanings in the context of this project                                       |
| ------------------------- | --------------------------------------------------------------------------------------- |
| 400 Bad Request           | Means client-side input passes validation but is invalid or missing key information.    |
| 401 Unauthorized          | Means the user _is not_ authenticated and _is not_ authorized to access a resource.     |
| 403 Forbidden             | Means the user _is_ authenticated and _is not_ authorized to access a resource.         |
| 404 Not Found             | Means that the referenced resource is not found or does not exist.                      |
| 410 Gone                  | Means that the referenced resource used to exist but is no longer active.               |
| 422 Unprocessable Entity  | Means that client-side input fails field-level validation.                              |
| 500 Internal server error | Indicates a generic server error and should be fixed before code ends up in production. |
| 502 Bad Gateway           | Indicates an invalid response from an upstream server.                                  |
| 503 Service Unavailable   | Indicates that something irrecoverably broke on server side.                            |
