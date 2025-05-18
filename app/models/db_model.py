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

session = Table(
    "session",
    metadata_obj,
    Column("id", Integer, primary_key=True),
)

chat_message = Table(
    "chat_message",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("session.id"), nullable=False),
    Column("role", String, nullable=False),
    Column("message", String, nullable=False),
    Column("time_created", DateTime, nullable=False, server_default=func.now()),
)
