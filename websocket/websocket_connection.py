from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json
from database_connection.database import get_db
from logging_config import logger
from security.jwt_token import verify_token_websocket
from websocket.ws_types import WebsocketType


# MAP ALL THE CLIENTS (THE ID OF THE USER ACCOUNT) TO THEIR WEBSOCKET CONNECTIONS
clients_connections: Dict[int, Set[WebSocket]] = {}

# USING ANOTHER MAP BECAUSE IF THE WEBSOCKET IS DISCONNECTED,
# THEN WE SHOULD DELETE THE CONNECTION BASED ON THE WEBSOCKET (because we don't know the user id)
websocket_connections: Dict[WebSocket, int] = {}


async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint:
    -explicitly close the ws if the token is invalid or if the client requested to unsubscribe

    :param token: the token given as query parameter
    :param websocket: the websocket
    :return: None
    """
    logger.info('Trying to connect to ws')
    # WS IN FASTAPI DOESN'T WORK WITH Depends() in order to add the db connection as dependency
    # SO WE CREATE THE DB CONNECTION MANUALLY
    db_gen = get_db()
    db = next(db_gen)
    # VERIFY THE TOKEN FOR EACH WS CONNECTION
    user_id = None
    try:
        user_id = verify_token_websocket(token, db)
        if user_id is None:
            logger.error("Token invalid")
            await websocket.close(code=1008)
            return
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass

    await websocket.accept()

    # ADD THE USER ID TO THE WEBSOCKET MAPS
    websocket_connections[websocket] = user_id
    if user_id not in clients_connections:
        clients_connections[user_id] = set()
    clients_connections[user_id].add(websocket)
    logger.info(f"ws connection established {websocket.client} to {user_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")

            if action == "":
                pass

    except WebSocketDisconnect:
        logger.info(f"Client {websocket.client} disconnected")
        # HERE WE NEED 2 MAPS (IF DISCONNECTED, ALL WE KNOW IS THE websocket, WE DON'T KNOW THE user_id)
        user_id = websocket_connections.pop(websocket, None)
        if user_id is not None:
            user_ws_set = clients_connections.get(user_id)
            if user_ws_set is not None:
                user_ws_set.discard(websocket)
                if not user_ws_set:  # IF THE SET IS EMPTY THEN REMOVE THE USER_ID FROM MAP
                    clients_connections.pop(user_id)


async def notify_client(user_id: int, data, action_type: WebsocketType):
    """
    Function used to send notifications with websocket to clients
    :param user_id: the client's user_id
    :param data: the data to be sent
    :param action_type: the type of notification
    :return: None
    """
    ws_set = clients_connections.get(user_id)
    if not ws_set:
        return

    disconnected = set()

    for ws in ws_set:
        try:
            logger.info(f"Send message: {data}; to: {ws.client}; user_id: {user_id}, type:${action_type.value}")
            await ws.send_text(json.dumps({
                "type": action_type.value,
                "payload": data
            }))
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            disconnected.add(ws)

    # IF SOME WS CONNECTION ARE LOST THEN REMOVE THEM
    for ws in disconnected:
        ws_set.discard(ws)  # REMOVE FROM clients_connections set
        websocket_connections.pop(ws, None)

    if not ws_set:  # IF THE SET BECAME EMPTY THEN REMOVE USER FROM MAP
        clients_connections.pop(user_id, None)
