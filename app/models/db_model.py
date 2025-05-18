from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
)

metadata_obj = MetaData()

chat_session = Table(
    "chat_session",
    metadata_obj,
    Column("id", Integer, primary_key=True),
)

chat_message = Table(
    "chat_message",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("chat_session_id", ForeignKey("chat_session.id"), nullable=False),
    Column("role", String, nullable=False),
    Column("message", String, nullable=False),
    Column("time_created", DateTime, nullable=False, server_default=func.now()),
)
