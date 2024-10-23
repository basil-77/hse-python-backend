
# test main.py

import pytest
import base64
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserEntity
from lecture_4.demo_service.core.users import UserService, UserRole, UserInfo, UserEntity
from lecture_4.demo_service.api.utils import requires_author
from lecture_4.demo_service.api.utils import initialize
from fastapi.security import HTTPBasicCredentials
from lecture_4.demo_service.api.utils import requires_author, requires_admin
from fastapi import HTTPException
from http import HTTPStatus
from lecture_4.demo_service.api.contracts import UserResponse

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def user_service_auth():
    service = UserService(
        password_validators=[lambda pwd: len(pwd) > 8, lambda pwd: any(char.isdigit() for char in pwd)]
    )
    service.register(
        UserInfo(
            username="admin",
            name="admin",
            birthdate="1990-01-01",
            role=UserRole.ADMIN,
            password="superSecretAdminPassword123",
        )
    )
    return service

@pytest.fixture
def client(user_service):
    app = create_app()
    initialize(app)
    app.state.user_service = user_service
    return TestClient(app)

@pytest.fixture
def valid_user_data():
    return {
        "username": "test_user",
        "name": "Test Name",
        "email": "test@example.com",
        "birthdate": "1990-01-01",
        "password": "strong_password"
    }


def admin_user_data():
    return {
        "username": "admin_user",
        "name": "Admin",
        "email": "admin@example.com",
        "birthdate": "1980-01-01",
        "password": "admin_pass",
        "role": UserRole.ADMIN,
    }

@pytest.fixture()
def regular_user_data():
    return {
        "username": "regular_user",
        "name": "Regular",
        "email": "regular@example.com",
        "birthdate": "1990-01-01",
        "password": "regular_pass",
        "role": UserRole.USER,
    }

# test users.py
async def test_register_user2(client, valid_user_data):
    response = client.post("/user-register", json=valid_user_data)
    assert response.status_code == HTTPStatus.OK
    assert "uid" in response.json()

async def test_register_user_name_exists(client, valid_user_data):
    response = client.post("/user-register", json=valid_user_data)
    assert response.status_code == HTTPStatus.OK
    response = client.post("/user-register", json=valid_user_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

async def test_register_user_name_bad_password(client, user_service_auth):
    data = {
        "username": "test_user",
        "name": "Test Name",
        "email": "test@example.com",
        "birthdate": "1990-01-01",
        "password": "weak"
    }
    client.app.state.user_service = user_service_auth
    response = client.post("/user-register", json=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

async def test_register_user_invalid_data2(client):
    response = client.post("/user-register", json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_get_user_by_id2(client, user_service, valid_user_data):
    response = client.post('/user-register', json=valid_user_data)
    user_id = response.json()['uid']
    assert response.status_code == HTTPStatus.OK
    assert user_id == 1
    response = user_service.get_by_id(user_id)
    assert response.uid == user_id


async def test_get_user_by_username2(client, user_service, valid_user_data):
    client.post('/user-register', json=valid_user_data)

    response = user_service.get_by_username(valid_user_data["username"])
    assert response.info.username == valid_user_data['username']


async def test_get_user_both_id_and_username2(client):
    client.app.dependency_overrides[requires_author] = lambda: None
    response = client.post("/user-get", params={"id": 1, "username": "test_user"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_get_user_neither_id_nor_username2(client):
    client.app.dependency_overrides[requires_author] = lambda: None
    response = client.post("/user-get")
    assert response.status_code == HTTPStatus.BAD_REQUEST

async def test_get_user_oher(client, valid_user_data):
    response = client.post("/user-register", json=valid_user_data)
    user_id = response.json()['uid']
    assert response.status_code == HTTPStatus.OK
    client.app.dependency_overrides[requires_author] = (lambda:  client.app.state.user_service.get_by_id(user_id))
    responce = client.post('/user-get', params={'id': user_id})
    assert responce.status_code == HTTPStatus.OK
    response = client.post('/user-get', params={'username': valid_user_data["username"]})
    assert responce.status_code == HTTPStatus.OK

    user_admin = UserEntity(
        uid="1234",
        info={
            "username": "admin_user",
            "name": "Admin User",
            "email": "test_user@example.com",
            "birthdate": "1990-01-01",
            "role" : UserRole.ADMIN,
            "password": "secret_password"
        }
    )
    user_response = UserResponse.from_user_entity(user_admin)
    client.app.dependency_overrides[requires_author] = (lambda:  user_admin)
    response = client.post('/user-get', params={"id": 222, 'author': user_admin}, auth=("admin_user", "secret_password"))
    assert response.status_code == HTTPStatus.NOT_FOUND

async def test_user_promote(client, valid_user_data):
    client.app.dependency_overrides[requires_admin] = lambda: None
    response = client.post("/user-register", json=valid_user_data)
    assert response.status_code == HTTPStatus.OK       
    response = client.post(f'/user-promote?id={response.json()['uid']}')
    assert response.status_code == HTTPStatus.OK

#@pytest.fixture()
async def test_get_by_username_not_exists():
    user_service = UserService()
    response = user_service.get_by_username(username='Unknown')
    assert response == None


async def test_user_grant_admin(client, valid_user_data):
    response = client.post('/user-register', json=valid_user_data)
    user_id = response.json()['uid']
    assert response.status_code == HTTPStatus.OK
    response = client.app.state.user_service.grant_admin(user_id)
    assert response == None
    try:
        response = client.app.state.user_service.grant_admin(111)
    except Exception as e:
        assert e.args[0] == 'user not found'

#test contracts.py
def test_from_user_entity():
    user_entity = UserEntity(
        uid="123",
        info={
            "username": "test_user",
            "name": "Test User",
            "email": "test_user@example.com",
            "birthdate": "1990-01-01",
            "password": "secret_password"
        }
    )

    user_response = UserResponse.from_user_entity(user_entity)

    assert user_response.uid == 123
    assert user_response.username == "test_user"
    assert user_response.name == "Test User"
    assert not hasattr(user_response, "password")



@pytest.fixture()
def test_users_router(client):
    response = client.post("/user-register", json={"username": "test_user"})
    assert response.status_code == HTTPStatus.OK
    assert "id" in response.json()


async def test_user_role():
    user_role = UserRole.USER
    assert user_role == UserRole.USER

#test utils.py
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.utils import initialize

app = FastAPI()

# exceptions
@app.get("/trigger-error")
async def trigger_error():
    raise ValueError("Test error")

@pytest.fixture()
def test_value_error_handler():
    response = client.get("/trigger-error")
    assert response.status_code == 400
    assert response.json() == {"detail": "Test error"}

# ini app
def test_initialize():
    lifespan_context = initialize(app)
    assert lifespan_context is not None


@pytest.mark.asyncio
async def test_user_service(client):
    async with initialize(client.app):
        service = client.app.state.user_service
        assert service is not None
        assert isinstance(service, UserService)



def test_requires_author_success(user_service_auth):
    credentials = HTTPBasicCredentials(username="admin", password="superSecretAdminPassword123")
    entity = requires_author(credentials, user_service_auth)
    assert entity is not None
    assert entity.info.username == "admin"
    try:
        credentials = HTTPBasicCredentials(username="admin", password="---")
        entity = requires_author(credentials, user_service_auth)
    except Exception as e:
        assert e.args[0] == HTTPStatus.UNAUTHORIZED


@pytest.fixture()
def test_requires_author_invalid_password(client, user_service):
    credentials = HTTPBasicCredentials(username="admin", password="wrongPassword")
    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, user_service)
    assert exc_info.value.status_code == 401


def test_requires_admin_success():
    admin_user = UserEntity(
        uid=1,
        info=UserInfo(
            username="admin",
            name="Admin User",
            birthdate="1970-01-01",
            role=UserRole.ADMIN,
            password="password123"
        )
    )
    result = requires_admin(admin_user)
    assert result == admin_user

def test_requires_admin_forbidden():
    regular_user = UserEntity(
        uid=2,
        info=UserInfo(
            username="user",
            name="Regular User",
            birthdate="1980-01-01",
            role=UserRole.USER,
            password="password123"
        )
    )
    with pytest.raises(HTTPException) as exc_info:
        requires_admin(regular_user)

    assert exc_info.value.status_code == 403