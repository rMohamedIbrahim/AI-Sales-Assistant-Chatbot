"""
API routes for handling test drive bookings and related operations.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, date, time
from src.models.schemas import (
    BookingCreate, BookingResponse, BookingUpdate, CustomerCreate, 
    CustomerResponse, APIResponse, ErrorResponse, BookingStatus
)
from src.infrastructure.database import db_service
from src.services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/test-drive", response_model=BookingResponse)
async def book_test_drive(booking: BookingCreate):
    """
    Book a test drive for a specific vehicle.
    
    - **customer_id**: ID of the customer making the booking
    - **vehicle_model**: Model of the vehicle for test drive
    - **preferred_date**: Preferred date and time for test drive
    - **location**: Location for the test drive
    """
    try:
        # Verify customer exists
        customer = await db_service.get_customer(booking.customer_id)
        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        # Check if the preferred date is in the future
        if booking.preferred_date <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Preferred date must be in the future"
            )

        # Create booking
        booking_data = booking.model_dump()
        booking_id = await db_service.create_booking(booking_data)
        
        # Get created booking
        created_booking = await db_service.get_booking(booking_id)
        if not created_booking:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created booking"
            )

        # Send confirmation email if customer has email
        if customer.email:
            try:
                await notification_service.send_booking_confirmation(
                    email=customer.email,
                    booking_details={
                        'id': booking_id,
                        'vehicle_model': booking.vehicle_model,
                        'preferred_date': booking.preferred_date,
                        'location': booking.location,
                        'status': 'confirmed'
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send booking confirmation email: {e}")

        # Convert to response model
        return BookingResponse(
            id=created_booking.id,
            customer_id=created_booking.customer_id,
            vehicle_model=created_booking.vehicle_model,
            preferred_date=created_booking.preferred_date,
            location=created_booking.location,
            status=BookingStatus(created_booking.status),
            created_at=created_booking.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to book test drive: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process booking request"
        )

@router.get("/availability/{date}")
async def get_available_slots(
    date: str,
    location: Optional[str] = None
):
    """
    Get available test drive slots for a specific date
    """
    try:
        # Convert date string to datetime
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Business hours
        BUSINESS_HOURS = {
            'start': time(9, 0),  # 9 AM
            'end': time(18, 0),   # 6 PM
            'slot_duration': 60    # 60 minutes
        }
        
        # Get existing bookings for the date
        existing_bookings = await db_service.get_bookings_for_date(
            booking_date,
            location
        )
        
        # Calculate available slots
        available_slots = []
        current_time = BUSINESS_HOURS['start']
        
        while current_time < BUSINESS_HOURS['end']:
            slot = current_time.strftime("%H:%M")
            
            # Check if slot is available
            if not any(
                booking['preferred_time'] == slot
                for booking in existing_bookings
            ):
                available_slots.append(slot)
            
            # Move to next slot
            hours, minutes = divmod(
                current_time.hour * 60 + current_time.minute + BUSINESS_HOURS['slot_duration'],
                60
            )
            current_time = time(hours, minutes)
        
        return {
            "date": date,
            "location": location,
            "available_slots": available_slots
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Failed to get available slots: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve available slots"
        )

@router.get("/status/{booking_id}")
async def get_booking_status(booking_id: int):
    """
    Get status of a specific booking
    """
    try:
        booking = await db_service.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )
        
        return {
            "booking_id": booking_id,
            "status": booking.status,
            "details": {
                "date": booking.preferred_date.isoformat(),
                "vehicle": booking.vehicle_model,
                "location": booking.location
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get booking status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve booking status"
        )
