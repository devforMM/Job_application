from sqlalchemy import create_engine,Integer,Text,Column,ForeignKey
from sqlalchemy.orm import relationship,sessionmaker,declarative_base
import os

from dotenv import load_dotenv

load_dotenv()


db_user=os.getenv("DataBase_user")
db_password=os.getenv("DataBase_password")
database_name=os.getenv("DataBase_name")
test_db_name=os.getenv("DataBase_test")


DB_URL = f"postgresql+psycopg://{db_user}:{db_password}@127.0.0.1:5432/{database_name}"
engine=create_engine(url=DB_URL)
SessionMaker=sessionmaker(bind=engine,autoflush=False)
base=declarative_base()

TEST_DB_URL = f"postgresql+psycopg://{db_user}:{db_password}@127.0.0.1:5432/{test_db_name}"
test_engine=create_engine(url=TEST_DB_URL)
Test_SessionMaker=sessionmaker(bind=engine,autoflush=False)




class User(base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,autoincrement=True)
    first_name=Column(Text,nullable=False)
    last_name=Column(Text,nullable=False)
    email=Column(Text,unique=True,nullable=False)
    password=Column(Text,nullable=False)
    phone_number=Column(Text,nullable=False)
    applications=relationship("Application",back_populates="user",foreign_keys="Application.user_id")

class Application(base):
    __tablename__="applications"
    id=Column(Integer,autoincrement=True,primary_key=True)
    job_position=Column(Text,nullable=False)
    company=Column(Text,nullable=False)
    status=Column(Text,nullable=True)
    Date=Column(Text,nullable=False)
    Cv_path=Column(Text,nullable=False)
    Website=Column(Text,nullable=False)
    Job_type=Column(Text,nullable=False)
    job_location=Column(Text,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    user=relationship("User",back_populates="applications",foreign_keys=user_id)



base.metadata.create_all(bind=engine)
base.metadata.create_all(bind=test_engine)






