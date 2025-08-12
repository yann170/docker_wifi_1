from sqlmodel import create_engine, SQLModel,Session
import os
from dotenv import load_dotenv
from models import User, Package, Voucher, Transaction


load_dotenv()  

DATABASE_URL= os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


def create_table_in_db():
    SQLModel.metadata.create_all(engine)