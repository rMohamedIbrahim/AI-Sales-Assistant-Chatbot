"""
API routes for handling vehicle service requests and service-related operations.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from src.models.schemas import ServiceRequest, ServiceRequestCreate, CustomerBase
from src.infrastructure.database import db_service
from src.services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/request", response_model=dict)
async def create_service_request(service_request: ServiceRequestCreate):
    """
    Create a new service request
    """
    try:
        # Verify customer exists
        customer = await db_service.get_customer(service_request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )
        
        # Create service request
        service_data = service_request.model_dump()
        service_id = await db_service.create_service_request(service_data)
        
        # Send confirmation email if customer has email
        if customer.email:
            try:
                await notification_service.send_service_notification(
                    email=customer.email,
                    service_details={
                        'type': 'confirmation',
                        'id': service_id,
                        'service_type': service_request.service_type,
                        'preferred_date': service_request.preferred_date,
                        'vehicle_model': service_request.vehicle_model
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send service confirmation email: {e}")
        
        return {
            "status": "success",
            "message": "Service request created successfully",
            "service_id": service_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create service request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process service request"
        )

@router.get("/status/{service_id}")
async def get_service_status(service_id: int):
    """
    Get status of a specific service request
    """
    try:
        service = await db_service.get_service_request(service_id)
        if not service:
            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )
        
        return {
            "service_id": service_id,
            "status": service.status,
            "details": {
                "date": service.preferred_date.isoformat(),
                "type": service.service_type,
                "description": service.description or '',
                "vehicle_model": service.vehicle_model
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve service status"
        )

@router.put("/update/{service_id}")
async def update_service_status(
    service_id: int,
    status: str,
    estimated_completion: Optional[datetime] = None,
    notes: Optional[str] = None
):
    """
    Update service request status
    """
    try:
        # Get current service request
        service = await db_service.get_service_request(service_id)
        if not service:
            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )
        
        # Update status
        update_data = {
            'status': status
        }
        if estimated_completion:
            update_data['estimated_completion'] = estimated_completion.isoformat()
        if notes:
            update_data['notes'] = notes
        
        # Update the service request
        success = await db_service.update_service_status(service_id, update_data)
        
        # Get customer for notification
        customer = await db_service.get_customer(service.customer_id)
        
        # Send notification based on status
        if customer and customer.email:
            try:
                if status == 'completed':
                    await notification_service.send_service_notification(
                        email=customer.email,
                        service_details={
                            'type': 'completion',
                            'id': service_id,
                            'service_type': service.service_type,
                            'vehicle_model': service.vehicle_model
                        }
                    )
                elif status == 'scheduled' and estimated_completion:
                    await notification_service.send_service_notification(
                        email=customer.email,
                        service_details={
                            'type': 'update',
                            'id': service_id,
                            'service_type': service.service_type,
                            'new_estimate': estimated_completion
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to send service notification: {e}")
        
        return {
            "status": "success",
            "message": "Service status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update service status"
        )
