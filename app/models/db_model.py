from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table

metadata_obj = MetaData()

session = Table(
    "session",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
)

chat_message = Table(
    "chat_message",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", ForeignKey("session.id"), nullable=False),
    Column("role", Integer, nullable=False),
    Column("message", String, nullable=False),
    Column("order", Integer, nullable=False),
)
