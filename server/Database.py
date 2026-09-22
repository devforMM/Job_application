from sqlalchemy import create_engine,Integer,Text,Column,ForeignKey
from sqlalchemy.orm import relationship,sessionmaker,declarative_base


DB_URL = "postgresql+psycopg://postgres:qwerty@127.0.0.1:5432/Job_application"
engine=create_engine(url=DB_URL)
SessionMaker=sessionmaker(bind=engine,autoflush=False)
base=declarative_base()



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







