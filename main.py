from fastapi import FastAPI

from src.flights.router import router as flights_router
from src.bookings.router import router as bookings_router
from src.users.router import router as users_router

app = FastAPI()
app.include_router(flights_router)
app.include_router(bookings_router)
app.include_router(users_router)