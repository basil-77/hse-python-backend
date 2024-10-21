
# test main.py

import pytest
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_app_initialization(client):
    response = client.get("/")
    assert response.status_code == 404  

def test_app_includes_users_router(client):
    response = client.post("/user-register", json={"username": "test_user"})
    assert response.status_code == 422  



# test users.py
from http import HTTPStatus
import pytest
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

# new user
def test_register_user(client, mocker):
    mock_user_service = mocker.patch("demo_service.api.users.UserServiceDep")
    mock_user_service.return_value.register.return_value = {
        "id": 1,
        "username": "test_user",
        "role": "user"
    }
    
    response = client.post("/user-register", json={"username": "test_user"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

# get user
def test_get_user_by_id(client, mocker):
    mock_user_service = mocker.patch("demo_service.api.users.UserServiceDep")
    mock_user_service.return_value.get_by_id.return_value = {
        "id": 1,
        "username": "test_user",
        "role": "user"
    }
    
    response = client.post("/user-get?id=1")
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

def test_get_user_not_found(client, mocker):
    mock_user_service = mocker.patch("demo_service.api.users.UserServiceDep")
    mock_user_service.return_value.get_by_id.return_value = None
    
    response = client.post("/user-get?id=999")
    assert response.status_code == HTTPStatus.NOT_FOUND

# user promote
def test_promote_user(client, mocker):
    mock_user_service = mocker.patch("demo_service.api.users.UserServiceDep")
    
    response = client.post("/user-promote?id=1")
    assert response.status_code == 200


#test contracts.py
from pydantic import ValidationError
from lecture_4.demo_service.api.contracts import RegisterUserRequest, UserResponse

def test_register_user_request_valid():
    valid_data = {"username": "test_user", "email": "test@example.com"}
    user_request = RegisterUserRequest(**valid_data)
    assert user_request.username == "test_user"

def test_register_user_request_invalid():
    invalid_data = {"username": "test_user"}
    try:
        RegisterUserRequest(**invalid_data)
    except ValidationError as e:
        assert e.errors()[0]['loc'] == ('email',)

def test_user_response():
    valid_data = {"id": 1, "username": "test_user", "role": "user"}
    user_response = UserResponse(**valid_data)
    assert user_response.id == 1


#test utils.py
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.utils import value_error_handler, initialize

app = FastAPI()

# exceptions
@app.get("/trigger-error")
async def trigger_error():
    raise ValueError("Test error")

app.add_exception_handler(ValueError, value_error_handler)

client = TestClient(app)

def test_value_error_handler():
    response = client.get("/trigger-error")
    assert response.status_code == 400
    assert response.json() == {"detail": "Test error"}

# ini app
def test_initialize():
    lifespan_context = initialize(app)
    assert lifespan_context is not None



