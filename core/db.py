import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from collections.abc import Generator
import crud

Base = declarative_base()

engine = create_engine("mysql+pymysql://root:cxh123@0.0.0.0:3025/week3",echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


#def get_db_session():
#    db_session = Session()
#    try:
#        yield db_session
#    finally:
#        db_session.close()

def get_db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
