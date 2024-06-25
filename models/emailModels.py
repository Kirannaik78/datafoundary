from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import URL

DATABASE_URL = URL.create(
    drivername='mysql+pymysql',
    username="root",
    password="kiran@99",
    host="localhost",
    port=3306,
    database="email_db"
)

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    id = Column(String(255), primary_key=True)
    from_email = Column(String(255))
    subject = Column(Text)
    body = Column(Text)
    received_datetime = Column(DateTime)
    is_read = Column(Boolean, default=False)
    folder = Column(String(50), default='Inbox')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
