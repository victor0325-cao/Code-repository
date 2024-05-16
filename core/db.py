import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from collections.abc import Generator
from typing import Annotated
from fastapi import Depends

Base = declarative_base()

engine = create_engine("mysql+pymysql://root:cxh123@0.0.0.0:3025/week3",echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

#def get_db_session() -> Generator[Session, None]:
#    with Session(engine) as session:
#        yield session

def get_db_session():
    session = Session()
    try:
        yield session
    finally:
         session.close()

SessionDep = Annotated[Session, Depends(get_db_session)]
