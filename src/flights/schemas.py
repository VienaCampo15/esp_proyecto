from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# 3. PATRÓN DATA TRANSFER OBJECT (DTO)
# el Patrón Data Transfer Object (DTO) propone quE creemos clases especiales 
# para transmitir los datos, de esta forma, podemos controlar los datos que enviamos, 
# el nombre, el tipo de datos, etc, además, si estos necesitan cambiar, no tiene impacto 
# sobre la capa de servicios o datos, pues solo se utilizan para transmitir la respuesta. 

class FlightBase(BaseModel):
    flight_id: str
    destination: str
    departure: str
    flight_type: str
    aircraft: str
    seats: int
    flight_datetime: datetime
    state: Optional[str] = None

    class Config:
        orm_mode = True

class FlightCreate(FlightBase):
    pass

class FlightUpdate(BaseModel):
    flight_id: str
    destination: Optional[str] = None
    departure: Optional[str] = None
    flight_type: Optional[str] = None
    aircraft: Optional[str] = None
    seats: Optional[int] = None
    flight_datetime: Optional[datetime] = None

class FlightList(BaseModel):
    flights: List[FlightBase]
