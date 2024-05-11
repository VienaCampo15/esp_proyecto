from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Reservation(BaseModel):
    id: int
    passenger_email: EmailStr
    flight_id: str
    seat_number: Optional[str] = None
    status: str = "reserved"

# 4. PATRÓN REPOSITORIO
# Su objetivo principal es abstraer la lógica de acceso a los datos de la lógica del negocio, 
# proporcionando una interfaz más limpia y orientada a objetos para interactuar con los datos. 

class ReservationRepository:
    def __init__(self):
        self.reservations = {} 

    def add_reservation(self, reservation: Reservation):
        if reservation.id in self.reservations:
            raise HTTPException(status_code=400, detail="Reservación ya existente.")
        self.reservations[reservation.id] = reservation

    def get_reservation(self, reservation_id: int) -> Optional[Reservation]:
        return self.reservations.get(reservation_id, None)

    def update_reservation(self, reservation: Reservation):
        if reservation.id not in self.reservations:
            raise HTTPException(status_code=404, detail="Reservación no encontrada.")
        self.reservations[reservation.id] = reservation

    def list_all(self) -> List[Reservation]:
        return list(self.reservations.values())

# SOLID. "O" = PRINCIPIO ABIERTO/CERRADO
reservation_repository = ReservationRepository()

# 5. PATRÓN FACHADA (FACADE): BookingManager actúa como una fachada para las operaciones 
# relacionadas con las reservas. Proporciona una interfaz simplificada a la capa de presentación 
# abstrayendo las interacciones más complejas con ReservationRepository.

class BookingManager:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    def create_reservation(self, reservation: Reservation):
        self.repository.add_reservation(reservation)

    def update_reservation(self, reservation: Reservation):
        self.repository.update_reservation(reservation)

    def cancel_reservation(self, reservation_id: int):
        reservation = self.repository.get_reservation(reservation_id)
        if reservation:
            reservation.status = "cancelled"
            self.repository.update_reservation(reservation)
        else:
            raise HTTPException(status_code=404, detail="Reservación no encontrada.")

    def list_all_reservations(self) -> List[Reservation]:
        return self.repository.list_all()

router = APIRouter(prefix="/bookings", tags=["bookings"])

booking_manager = BookingManager(reservation_repository)

# ENDPOINTS
@router.post("/reservations/", response_model=Reservation)
def create_reservation(reservation: Reservation):
    booking_manager.create_reservation(reservation)
    return reservation

@router.post("/reservations/{reservation_id}/cancel/")
def cancel_reservation(reservation_id: int):
    booking_manager.cancel_reservation(reservation_id)
    return {"message": "Reservación cancelada."}

@router.get("/reservations/", response_model=List[Reservation])
def list_reservations():
    return booking_manager.list_all_reservations()
