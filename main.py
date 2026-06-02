from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from fastapi import FastAPI
from schemas import CustomerCreate
import models 
from database import engine
from schemas import VehicleCreate, ServiceRequestCreate, ServiceStatusUpdate

models.Base.metadata.create_all(bind=engine)

SECRET_KEY = "vehicle_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

fake_user = {
    "username": "admin",
    "password": "admin123"
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

app = FastAPI()

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    if form_data.username != fake_user["username"]:
        return {"message": "Invalid username"}

    if form_data.password != fake_user["password"]:
        return{"message": "Invalid password"}
    
    token = create_access_token(
        {"sub": form_data.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/")
def home():
    return {"message": "Vehicle Service Management System"}

@app.post("/customers")
def add_customer(customer: CustomerCreate, db: Session = Depends(get_db)):

    new_customer = models.Customer(
        name=customer.name,
        phone=customer.phone,
        email=customer.email
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

@app.get("/customers")
def get_customers(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return db.query(models.Customer).filter(models.Customer.is_deleted == False).offset(skip).limit(limit).all()

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):

    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer:
        return customer

    return {"message": "Customer not found"}

@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    updated_customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        return {"message": "Customer not found"}

    customer.name = updated_customer.name
    customer.phone = updated_customer.phone
    customer.email = updated_customer.email

    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer updated successfully",
        "customer": customer
    }
    
@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        return {"message": "Customer not found"}

    customer.is_deleted = True
    db.commit()

    return {"message": "Customer deleted successfully"}

@app.get("/customers/search/{name}")
def search_customer(
    name: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Customer)\
        .filter(
            models.Customer.name.contains(name),
            models.Customer.is_deleted == False
        )\
        .all()

@app.post("/vehicles")
def add_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == vehicle.customer_id).first()
    if not customer:
        return{"message": "Customer not found"}
    
    new_vehicle = models.Vehicle(
        vehicle_number=vehicle.vehicle_number,
        brand=vehicle.brand,
        model=vehicle.model,
        customer_id=vehicle.customer_id
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle

@app.get("/vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    return db.query(models.Vehicle).filter(models.Vehicle.is_deleted == False).all()

@app.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if vehicle:
        return vehicle

    return {"message": "Vehicle not found"}

@app.put("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    updated_vehicle: VehicleCreate,
    db: Session = Depends(get_db)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if not vehicle:
        return {"message": "Vehicle not found"}

    vehicle.vehicle_number = updated_vehicle.vehicle_number
    vehicle.brand = updated_vehicle.brand
    vehicle.model = updated_vehicle.model
    vehicle.customer_id = updated_vehicle.customer_id

    db.commit()
    db.refresh(vehicle)

    return {
        "message": "Vehicle updated successfully",
        "vehicle": vehicle
    }
    
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()

    if not vehicle:
        return {"message": "Vehicle not found"}

    vehicle.is_deleted = True
    db.commit()

    return {"message": "Vehicle deleted successfully"}

@app.get("/vehicles/search/{vehicle_number}")
def search_vehicle(
    vehicle_number: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Vehicle)\
        .filter(
            models.Vehicle.vehicle_number.contains(vehicle_number)
        )\
        .all()

@app.post("/services")
def create_service(
    service: ServiceRequestCreate,
    db: Session = Depends(get_db)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == service.vehicle_id
    ).first()

    if not vehicle:
        return {"message": "Vehicle not found"}

    if service.service_cost <= 0:
        return {"message": "Service cost must be greater than 0"}

    new_service = models.ServiceRequest(
        vehicle_id=service.vehicle_id,
        service_type=service.service_type,
        service_cost=service.service_cost,
        service_date=service.service_date,
        status=service.status
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service

@app.get("/services")
def get_services(db: Session = Depends(get_db)):
    return db.query(models.ServiceRequest).all()

@app.get("/services/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id
    ).first()

    if not service:
        return {"message": "Service not found"}

    return service

@app.put("/services/{service_id}")
def update_service_status(
    service_id: int,
    updated_service: ServiceStatusUpdate,
    db: Session = Depends(get_db)
):
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id
    ).first()

    if not service:
        return {"message": "Service not found"}

    if service.status.lower() == "completed":
        return {"message": "Completed services cannot be edited"}

    service.status = updated_service.status

    db.commit()
    db.refresh(service)

    return {
        "message": "Service status updated successfully",
        "service": service
    }
    
@app.get("/customers/search/{name}")
def search_customer(
    name: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Customer).filter(
        models.Customer.name.contains(name)
    ).all()
    
@app.get("/vehicles/search/{vehicle_number}")
def search_vehicle(
    vehicle_number: str,
    db: Session = Depends(get_db)
):
    return db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_number == vehicle_number
    ).all()    
