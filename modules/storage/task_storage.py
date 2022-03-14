from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()
engine = create_engine("sqlite:///tasks.db")


user_lists = Table(
    "user_lists",
    metadata,
    Column("list_id", Integer, primary_key=True, autoincrement=True),
    Column("list_name", String(80), unique=False),
    Column("user_id", Integer, unique=False),
)


user_tasks = Table(
    "user_tasks",
    metadata,
    Column("task_id", Integer, primary_key=True, autoincrement=True),
    Column("list_id", Integer, ForeignKey("user_lists.list_id"), unique=False),
    Column("data", String),
    Column("priority", Integer, unique=False),
    Column("status", Integer, unique=False),
    Column("created_datetime", String(120), unique=False),
    Column("edite_datetime", String(120), unique=False),
)

metadata.create_all(engine)
