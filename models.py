from sqlalchemy import Column, Integer, String,Float, ForeignKey, Boolean
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    
    is_deleted = Column(Boolean,default=False)
    
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String)
    brand = Column(String)
    model = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    is_deleted = Column(Boolean,default=False)
    
class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    service_type = Column(String)
    service_cost = Column(Float)
    service_date = Column(String)
    status = Column(String)   