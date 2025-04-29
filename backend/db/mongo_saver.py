from langgraph.checkpoint.mongodb import MongoDBSaver
import uuid
from datetime import datetime
from db.mongo_connector import get_mongo_client
from typing import Any

client = get_mongo_client()
db = client.get_database('chatbotdb')
mongo_memory = MongoDBSaver(db)

def saveMessage(result: Any, agent: str):
    history_log = []

    for msg in result.all_messages():
        msg_type = msg.__class__.__name__
        timestamp = getattr(msg, "timestamp", datetime.utcnow())

        if hasattr(msg, "content") and isinstance(msg.content, str):
            content = msg.content
        elif hasattr(msg, "parts") and isinstance(msg.parts, list):
            content_parts = []
            for part in msg.parts:
                part_content = getattr(part, "content", None)
                if part_content is None:
                    if hasattr(part, "args"):
                        part_content = str(part.args)
                    else:
                        part_content = str(part)
                else:
                    if isinstance(part_content, list):
                        part_content = "\n".join(str(p) for p in part_content)
                    else:
                        part_content = str(part_content)
                content_parts.append(part_content)
            content = "\n".join(content_parts)
        else:
            content = str(msg)

        entry = {
            "timestamp": timestamp.isoformat(),
            "type": msg_type,
            "content": content
        }

        history_log.append(entry)

    chat_record = {
        "chat_id": str(uuid.uuid4()),
        "agent": agent,
        "history": history_log
    }

    mongo_memory.db["chatbotdb"].insert_one(chat_record)
