from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
from .schemas import FlightBase, FlightCreate, FlightUpdate, FlightList
from src.auth import admin_required, get_current_user

router = APIRouter(prefix="/flights", tags=["flights"])

# 1. PATRÓN SINGLETON: la base de datos simulada actúa como un almacenamiento único y global 
# dentro de la app. Este objeto es accesible globalmente en las rutas y mantiene su estado 
# durante la ejecución del servidor.

flights_db = {}

class Flight:
    def __init__(self, flight_id: str, destination: str, departure: str, flight_type: str, aircraft: str, seats: int, flight_datetime: datetime):
        self.flight_id = flight_id
        self.destination = destination
        self.departure = departure
        self.flight_type = flight_type
        self.aircraft = aircraft
        self.seats = seats
        self.flight_datetime = flight_datetime
        self.state = "reserved"

    def to_dict(self) -> dict:
        return {
            "flight_id": self.flight_id,
            "destination": self.destination,
            "departure": self.departure,
            "flight_type": self.flight_type,
            "aircraft": self.aircraft,
            "seats": self.seats,
            "flight_datetime": self.flight_datetime,
            "state": self.state
        }

    def update(self, data: FlightUpdate):
        if data.destination:
            self.destination = data.destination
        if data.departure:
            self.departure = data.departure
        if data.flight_type:
            self.flight_type = data.flight_type
        if data.aircraft:
            self.aircraft = data.aircraft
        if data.seats is not None:
            self.seats = data.seats
        if data.flight_datetime is not None:
            self.flight_datetime = data.flight_datetime

    def confirm(self):
        self.state = "confirmed"
        return "Vuelo confirmado."

    def cancel(self):
        if self.state == "confirmed":
            return "Cannot cancel a confirmed flight."
        self.state = "cancelled"
        return "Vuelo cancelado."

# 2. PATRÓN FACTORY: FlightFactory encapsula la lógica de creación de nuevas instancias de Flight. 
# Esto permite desacoplar la creación del objeto de su uso y facilita la expansión o 
# modificación futura de cómo se inicializan los vuelos.

# SOLID. "S" = PRINCIPIO DE UNICA RESPONSABILIDAD: FlightFactory se dedica exclusivamente a la creación de instancias de Flight.
class FlightFactory:
    @staticmethod
    def create_flight(flight_data: FlightCreate):
        return Flight(
            flight_id=flight_data.flight_id,
            destination=flight_data.destination,
            departure=flight_data.departure,
            flight_type=flight_data.flight_type,
            aircraft=flight_data.aircraft,
            seats=flight_data.seats,
            flight_datetime=flight_data.flight_datetime
        )


# ENDPOINTS 

# 3. PATRÓN PROXY EN EL DEPENDS
# Cada endpoint que requiere verificación de que el usuario sea administrador está delegando 
# la responsabilidad de verificar si el usuario tiene permisos de administrador antes de permitirle 
# realizar lo que manda la función que lo llama.

# SOLID. "D" = PRINCIPIO DE INVERSIÓN DE DEPENDENCIA: Este principio se puede observar en el uso de 
# dependencias inyectadas como Depends(admin_required) para controlar el acceso a las funciones. 
# Este diseño permite que los detalles de alto nivel (En este caso, la lógica de los endpoints) no 
# dependan directamente de los detalles de bajo nivel (lógica de autenticación y autorización), 
# sino a través de abstracciones (la función admin_required).

@router.post("/create", response_model=str, dependencies=[Depends(admin_required)])
def create_flight(request: FlightCreate):
    if request.flight_id in flights_db:
        raise HTTPException(status_code=400, detail=f"Vuelo con Id {request.flight_id} ya existe.")
    flight = FlightFactory.create_flight(request)
    flights_db[request.flight_id] = flight
    return f"Vuelo {request.flight_id} creado exitosamente."

@router.get("/search", response_model=List[FlightBase], dependencies=[Depends(admin_required)])
def search_flights(
    flight_id: Optional[str] = None,
    destination: Optional[str] = None,
    departure: Optional[str] = None,
    flight_type: Optional[str] = None,
    aircraft: Optional[str] = None,
    seats: Optional[int] = Query(None, ge=0),
    flight_datetime: Optional[datetime] = None
):
    results = []
    for flight in flights_db.values():
        if flight_id and flight.flight_id != flight_id:
            continue
        if destination and flight.destination != destination:
            continue
        if departure and flight.departure != departure:
            continue
        if flight_type and flight.flight_type != flight_type:
            continue
        if aircraft and flight.aircraft != aircraft:
            continue
        if seats is not None and flight.seats != seats:
            continue
        if flight_datetime and flight.flight_datetime != flight_datetime:
            continue
        results.append(flight.to_dict())

    if not results:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado.")

    return results

@router.put("/update", response_model=str, dependencies=[Depends(admin_required)])
def update_flight(request: FlightUpdate):
    flight = flights_db.get(request.flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado.")
    flight.update(request)
    return f"Vuelo {request.flight_id} actualizado exitosamente."

@router.get("/get_all", response_model=FlightList, dependencies=[Depends(admin_required)])
def list_flights():
    flights_list = [flight.to_dict() for flight in flights_db.values()]
    return FlightList(flights=flights_list)

@router.post("/confirm/{flight_id}", response_model=str, dependencies=[Depends(admin_required)])
def confirm_flight(flight_id: str):
    flight = flights_db.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado.")
    return flight.confirm()

@router.post("/cancel/{flight_id}", response_model=str, dependencies=[Depends(admin_required)])
def cancel_flight(flight_id: str):
    flight = flights_db.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado.")
    return flight.cancel()
