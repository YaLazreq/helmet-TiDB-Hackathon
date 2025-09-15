from fastapi import FastAPI, HTTPException, WebSocket
import asyncio
import json
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.mcp.db_client import connect_db_mcp
from run_supervisor import run_supervisor_agent

load_dotenv()


app = FastAPI(title="Simple Tasks API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    'host': os.getenv('TIDB_HOST'),
    'port': os.getenv('TIDB_PORT'),
    'database': os.getenv('TIDB_DATABASE'),
    'user': os.getenv('TIDB_USER'),
    'password': os.getenv('TIDB_PASSWORD')
}

connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

async def notify_clients(message):
    if connected_clients:
        await asyncio.gather(
            *[client.send_text(json.dumps(message)) for client in connected_clients],
            return_exceptions=True
        )

# Modèles Pydantic pour les messages
class MessageCreate(BaseModel):
    client_id: str
    conversation_id: str
    text: Optional[str] = None
    audioUrl: Optional[str] = None
    audioDuration: Optional[int] = None
    sender: str  # 'me' ou 'helmet'
    type: str    # 'text' ou 'audio'

class MessageResponse(BaseModel):
    id: int
    text: Optional[str] = None
    audioUrl: Optional[str] = None
    audioDuration: Optional[int] = None
    sender: str
    timestamp: str
    type: str

class DataCreate(BaseModel):
    ding: str

class PromptSupervisor(BaseModel):
    message: str

def get_db_connection():
    """Crée une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Erreur de connexion MySQL: {e}")
        return None

@app.get("/")
def root():
    return {"message": "API Tasks - FastAPI + MySQL"}

@app.get("/all_users")
def get_all_users_ids():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        cursor.close()
        connection.close()

        return {"users": users, "count": len(users)}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}")
    
@app.get("/tasks")
def get_all_tasks():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {"tasks": tasks, "count": len(tasks)}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tâches: {str(e)}")

@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Tâche avec l'ID {task_id} non trouvée")
            
        return {"task": task}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la tâche: {str(e)}")

@app.get("/notifications")
def get_notifications():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Notifications")
        notifications = cursor.fetchall()
        cursor.close()
        connection.close()

        return {"notifications": notifications, "count": len(notifications)}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des notifications: {str(e)}")

@app.get("/messages/{client_id}/{conversation_id}")
def get_conversation_messages(client_id: str, conversation_id: str):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            id,
            text,
            audio_url as audioUrl,
            audio_duration as audioDuration,
            sender,
            timestamp,
            type
        FROM messages 
        WHERE client_id = %s AND conversation_id = %s 
        ORDER BY timestamp ASC
        """
        cursor.execute(query, (client_id, conversation_id))
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
        
        for message in messages:
            if message['timestamp']:
                message['timestamp'] = message['timestamp'].isoformat()
        
        return {"messages": messages, "count": len(messages)}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des messages: {str(e)}")

@app.post("/messages")
def create_message(message: MessageCreate):
    """Crée un nouveau message"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO messages (client_id, conversation_id, text, audio_url, audio_duration, sender, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            message.client_id,
            message.conversation_id,
            message.text,
            message.audioUrl,
            message.audioDuration,
            message.sender,
            message.type
        ))
        
        message_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        
        return {"message": "Message créé avec succès", "id": message_id}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du message: {str(e)}")

@app.post("/call_supervisor")
async def call_supervisor(data: PromptSupervisor):
    await connect_db_mcp()
    result = await run_supervisor_agent(data.message)
    return {"status": "success", "result": result}

@app.post("/notify_db_update")
async def notify_db_update(data: DataCreate):
    await notify_clients(data.model_dump())
    return {"status": "notification sent"}


@app.get("/health")
def health_check():
    """Vérification de la santé de l'API et de la connexion DB"""
    connection = get_db_connection()
    if not connection:
        return {"status": "unhealthy", "database": "disconnected"}
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        
        return {"status": "healthy", "database": "connected"}
        
    except Error as e:
        return {"status": "unhealthy", "database": f"error: {str(e)}"}
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)