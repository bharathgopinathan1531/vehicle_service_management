from pydantic import BaseModel

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str
    
class CustomerRespomse(CustomerCreate):
    id: int
    
    class Config:
        from_attributes = True 
        
class VehicleCreate(BaseModel):
    vehicle_number: str
    brand: str
    model: str
    customer_id: int 
    
class ServiceRequestCreate(BaseModel):
    vehicle_id: int
    service_type: str
    service_cost: float
    service_date: str
    status: str 
    
class ServiceStatusUpdate(BaseModel):
    status: str                