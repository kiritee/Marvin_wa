from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import csv

# Set up the database engine
engine = create_engine('sqlite:///message_database.db')

# Create a base class for declarative models
Base = declarative_base()

# Define the model
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    waid = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def add_message(waid, role, content):
    session = Session()
    new_message = Message(waid=waid, role=role, content=content)
    session.add(new_message)
    session.commit()
    session.close()

def get_recent_messages(waid, days=3):
    session = Session()
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    messages = session.query(Message).filter(
        Message.waid == waid,
        Message.timestamp >= cutoff_date,
        Message.role != 'system'
    ).all()
    session.close()
    return [{'role': msg.role, 'content': msg.content} for msg in messages]

def export_messages_to_csv(file_name='messages.csv'):
    session = Session()
    messages = session.query(Message).all()
    session.close()

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'WAID', 'Timestamp', 'Role', 'Content'])
        for msg in messages:
            writer.writerow([msg.id, msg.waid, msg.timestamp, msg.role, msg.content[:10]])

# export_messages_to_csv()
