from unittest.mock import AsyncMock

import pytest
from fastapi.websockets import WebSocket

from app.websockets import ConnectionManager


@pytest.fixture
def websocket_manager():
    return ConnectionManager()


def test_connection_manager_initialization(websocket_manager: ConnectionManager):
    assert websocket_manager.active_connections == []


@pytest.mark.asyncio
async def test_connect(websocket_manager: ConnectionManager):
    mock_websocket = AsyncMock(spec=WebSocket)

    await websocket_manager.connect(mock_websocket)

    # Ensure the websocket accept method is called
    mock_websocket.accept.assert_called_once()

    # Ensure the websocket is added to active connections
    assert mock_websocket in websocket_manager.active_connections


@pytest.mark.asyncio
async def test_disconnect(websocket_manager: ConnectionManager):
    mock_websocket = AsyncMock(spec=WebSocket)

    # Add the mock websocket to active connections
    websocket_manager.active_connections.append(mock_websocket)

    websocket_manager.disconnect(mock_websocket)

    # Ensure the websocket is removed from active connections
    assert mock_websocket not in websocket_manager.active_connections


@pytest.mark.asyncio
async def test_send_personal_message(websocket_manager: ConnectionManager):
    mock_websocket = AsyncMock(spec=WebSocket)
    message = "Hello, WebSocket!"

    await websocket_manager.send_personal_message(message, mock_websocket)

    # Ensure the websocket send_text method is called with the correct message
    mock_websocket.send_text.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_broadcast(websocket_manager: ConnectionManager):
    mock_websocket_1 = AsyncMock(spec=WebSocket)
    mock_websocket_2 = AsyncMock(spec=WebSocket)
    message = "Broadcast message"

    # Add mock websockets to active connections
    websocket_manager.active_connections.extend([mock_websocket_1, mock_websocket_2])

    await websocket_manager.broadcast(message)

    # Ensure send_text is called for each active connection
    mock_websocket_1.send_text.assert_called_once_with(message)
    mock_websocket_2.send_text.assert_called_once_with(message)
