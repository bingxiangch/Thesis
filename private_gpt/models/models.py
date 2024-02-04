from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database

DATABASE_URL = "postgresql://chenbingxiang:6822688@localhost:5432/thesis"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, unique=True, index=True)
    access_level = Column(Integer)
    docs = relationship("FileDoc", back_populates="file")

class FileDoc(Base):
    __tablename__ = "file_docs"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey('files.id'))
    doc_id = Column(String)
    file = relationship("File", back_populates="docs")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    access_level = Column(Integer)

