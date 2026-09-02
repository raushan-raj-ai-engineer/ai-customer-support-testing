import pytest
from fastapi.testclient import (
    TestClient,
)

from app.main import app
from app.services.ticket_service import (
    ticket_service,
)


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_tickets():

    ticket_service.reset()

    yield

    ticket_service.reset()
