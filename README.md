# FastAPI Gemini Customer Support Chatbot Example

This repository is intended to be a simple example of a project using FastAPI, SQLAlchemy (Core), Pydantic and Gemini (Google genai). The API is a customer service chatbot intended to be an intermediary between users and human customer service, unlike a simple chatbot, we first do an analysis of the customer's mood and frustration to redirect them directly to a customer service employee if it is required.

## Usage
Create an `.env` file (you can base it on [.env.example](.env.example))
Make sure you have installed [uv](https://github.com/astral-sh/uv) (Please be aware that this project may need Python 3.12+)

    uv run fastapi dev

uv should take care of installing everything needed (including creating the virtual environment), alternatively you can first do

    uv sync

to sync and create the environment directly

    bash curl -X POST "http://127.0.0.1:8000/chat" \
    	-H "Content-Type: application/json" \
    	-d '{"message": "Hello!"}'

To continue the conversation add the session id you get back

    bash curl -X POST "http://127.0.0.1:8000/chat" \
    	-H "Content-Type: application/json" \
    	-d '{"message": "Bye!", "chat_session": 1}'

## TODO
 - [ ] **Information retrieval:** The model has no way to look up information about what users need
 - [ ] **Better prompt (especially in the main chat):** Currently the model only has instructions to help the user and how to interpret messages (and mood)
 - [ ] **Logging**
 - [ ] **Unit testing**
 - [ ] **Better error handling:** Many of the errors are not caught and most that are only give generic messages
 - [ ] **Improve handoff to human customer service:** Although it is outside the scope of this project, it might be a good idea to summarize and report back to a customer service person to streamline the process.
 - [ ] **Documentation and comments are missing**

## Limitations
At this moment the API does not have any kind of filter or security validation when accessing the LLM, which means that if you add sensitive information such as support data it could be filtered, the safest solution is to add another "layer" when acquiring the information and maybe when returning the message to verify its content.
The API also does not have any middleware or authentication since it is not designed to be deployed.
