from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # Path to swagger file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Multi User RAG Chat API"}
)

SWAGGER_JSON = {
    "swagger": "2.0",
    "info": {
        "title": "Multi-User RAG Chat API",
        "version": "1.0.0",
        "description": "API for querying text documents with user access control and conversation history",
    },
    "paths": {
        "/chat": {
            "post": {
                "summary": "Chat with the RAG system",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "user_email": {"type": "string", "example": "userA@email.com"},
                                "query": {"type": "string", "example": "What was the revenue in Q4?"},
                            },
                            "required": ["user_email", "query"],
                        },
                    }
                ],
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad Request"},
                },
            }
        },
       "/reset_context": {
            "post": {
                "summary": "Reset user conversation context",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "user_email": {"type": "string", "example": "userA@email.com"},
                            },
                            "required": ["user_email"],
                        },
                    }
                ],
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad Request"},
                },
            }
        },
    },
}