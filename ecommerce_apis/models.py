from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)
    tracking_id = Column(String, ForeignKey("transits.tracking_id"))

class Transit(Base):
    __tablename__ = "transits"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)