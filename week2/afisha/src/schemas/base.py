from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.infrastracture.db.models.bookings import BookingStatus


class SalesDashboard(BaseModel):
    paid_orders: int
    sold_tickets: int
    revenue: int
    average_order: int


class OccupancyDashboard(BaseModel):
    total: int
    available: int
    reserved: int
    sold: int
    occupancy_percent: float


class EventDashboard(BaseModel):
    event_title: str
    starts_at: datetime
    sales: SalesDashboard
    occupancy: OccupancyDashboard


class PaymentQuote(BaseModel):
    commission: int
    total: int
    payment_methods: list[str]
    expires_at: datetime | None = None


class ProtectionQuote(BaseModel):
    available: bool
    price: int
    covered_amount: int
    description: str | None = None


class CheckoutBooking(BaseModel):
    id: int
    event_title: str
    starts_at: datetime
    seats: list[dict[str, Any]]
    base_amount: int
    payment_commission: int
    protection_price: int | None
    with_protection: bool
    reserved_until: datetime


class CheckoutResponse(BaseModel):
    booking: CheckoutBooking
    payment: PaymentQuote
    protection: ProtectionQuote | None


class PaymentCreate(BaseModel):
    payment_method: str
    with_protection: bool = False


class PaymentCompleted(BaseModel):
    booking_id: int
    status: BookingStatus
    charged_amount: int
    transaction_id: str
