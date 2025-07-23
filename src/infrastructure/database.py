"""
Database service implementation using SQLite with SQLAlchemy async.
Handles all database operations with proper connection pooling and error handling.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, update, delete
from typing import Optional, List, Dict, Any, AsyncGenerator
from src.core.config import get_settings
from src.domain.exceptions import DatabaseError
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import os

logger = logging.getLogger(__name__)
settings = get_settings()

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete-orphan")
    service_requests = relationship("ServiceRequest", back_populates="customer", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    vehicle_model: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="bookings")

class ServiceRequest(Base):
    __tablename__ = 'service_requests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vehicle_model: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='requested')
    estimated_completion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="service_requests")

class Interaction(Base):
    __tablename__ = 'interactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('customers.id'), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="interactions")

class DatabaseService:
    """Database service with SQLite async support"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    async def connect(self):
        """Initialize SQLite database connection"""
        try:
            # Ensure data directory exists
            db_dir = os.path.dirname(settings.DB_PATH)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Create async engine
            self._engine = create_async_engine(
                f"sqlite+aiosqlite:///{settings.DB_PATH}",
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_recycle=300
            )

            # Create tables
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
            logger.info(f"Connected to SQLite database at {settings.DB_PATH}")
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise DatabaseError("Failed to connect to database", original_error=e)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session"""
        if self._session_factory is None:
            await self.connect()
        
        if self._session_factory is None:
            raise DatabaseError("Session factory not initialized")
            
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self):
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Disposed SQLite engine")

    # Customer Operations
    async def create_customer(self, customer_data: Dict[str, Any]) -> int:
        """Create a new customer record"""
        async with self.session() as session:
            try:
                customer = Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data.get('phone'),
                    created_at=datetime.utcnow()
                )
                session.add(customer)
                await session.commit()
                await session.refresh(customer)
                return customer.id
            except Exception as e:
                logger.error(f"Failed to create customer: {str(e)}")
                raise DatabaseError("Failed to create customer", original_error=e)

    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Retrieve customer by ID"""
        async with self.session() as session:
            try:
                stmt = select(Customer).where(Customer.id == customer_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Failed to retrieve customer: {str(e)}")
                raise DatabaseError("Failed to retrieve customer", original_error=e)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Retrieve customer by email"""
        async with self.session() as session:
            try:
                stmt = select(Customer).where(Customer.email == email)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Failed to retrieve customer by email: {str(e)}")
                raise DatabaseError("Failed to retrieve customer", original_error=e)

    async def update_customer(self, customer_id: int, update_data: Dict[str, Any]) -> bool:
        """Update customer data"""
        async with self.session() as session:
            try:
                stmt = update(Customer).where(Customer.id == customer_id).values(**update_data)
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                logger.error(f"Failed to update customer: {str(e)}")
                raise DatabaseError("Failed to update customer", original_error=e)

    # Booking Operations
    async def create_booking(self, booking_data: Dict[str, Any]) -> int:
        """Create a new test drive booking"""
        async with self.session() as session:
            try:
                booking = Booking(
                    customer_id=booking_data['customer_id'],
                    vehicle_model=booking_data['vehicle_model'],
                    preferred_date=booking_data['preferred_date'],
                    location=booking_data['location'],
                    status='pending',
                    created_at=datetime.utcnow()
                )
                session.add(booking)
                await session.commit()
                await session.refresh(booking)
                return booking.id
            except Exception as e:
                logger.error(f"Failed to create booking: {str(e)}")
                raise DatabaseError("Failed to create booking", original_error=e)

    async def get_booking(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        async with self.session() as session:
            try:
                stmt = select(Booking).where(Booking.id == booking_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Failed to retrieve booking: {str(e)}")
                raise DatabaseError("Failed to retrieve booking", original_error=e)

    async def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Update booking status"""
        async with self.session() as session:
            try:
                stmt = update(Booking).where(Booking.id == booking_id).values(status=status)
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                logger.error(f"Failed to update booking status: {str(e)}")
                raise DatabaseError("Failed to update booking status", original_error=e)

    async def get_bookings_for_date(self, date: datetime, location: Optional[str] = None) -> List[Booking]:
        """Get all bookings for a specific date and location"""
        async with self.session() as session:
            try:
                stmt = select(Booking).where(
                    Booking.preferred_date >= date.replace(hour=0, minute=0, second=0, microsecond=0),
                    Booking.preferred_date < date.replace(hour=23, minute=59, second=59, microsecond=999999)
                )
                if location:
                    stmt = stmt.where(Booking.location == location)
                
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Failed to retrieve bookings: {str(e)}")
                raise DatabaseError("Failed to retrieve bookings", original_error=e)

    # Service Request Operations
    async def create_service_request(self, service_data: Dict[str, Any]) -> int:
        """Create a new service request"""
        async with self.session() as session:
            try:
                service = ServiceRequest(
                    customer_id=service_data['customer_id'],
                    service_type=service_data['service_type'],
                    description=service_data['description'],
                    preferred_date=service_data['preferred_date'],
                    vehicle_model=service_data['vehicle_model'],
                    status='requested',
                    created_at=datetime.utcnow()
                )
                session.add(service)
                await session.commit()
                await session.refresh(service)
                return service.id
            except Exception as e:
                logger.error(f"Failed to create service request: {str(e)}")
                raise DatabaseError("Failed to create service request", original_error=e)

    async def get_service_request(self, service_id: int) -> Optional[ServiceRequest]:
        """Get service request by ID"""
        async with self.session() as session:
            try:
                stmt = select(ServiceRequest).where(ServiceRequest.id == service_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Failed to retrieve service request: {str(e)}")
                raise DatabaseError("Failed to retrieve service request", original_error=e)

    async def update_service_status(self, service_id: int, update_data: Dict[str, Any]) -> bool:
        """Update service request status"""
        async with self.session() as session:
            try:
                stmt = update(ServiceRequest).where(ServiceRequest.id == service_id).values(**update_data)
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                logger.error(f"Failed to update service status: {str(e)}")
                raise DatabaseError("Failed to update service status", original_error=e)

    # Interaction Operations
    async def create_interaction(self, interaction_data: Dict[str, Any]) -> int:
        """Create a new interaction record"""
        async with self.session() as session:
            try:
                interaction = Interaction(
                    customer_id=interaction_data.get('customer_id'),
                    type=interaction_data['type'],
                    content=interaction_data.get('content'),
                    language=interaction_data.get('language'),
                    sentiment_score=interaction_data.get('sentiment_score'),
                    created_at=datetime.utcnow()
                )
                session.add(interaction)
                await session.commit()
                await session.refresh(interaction)
                return interaction.id
            except Exception as e:
                logger.error(f"Failed to create interaction: {str(e)}")
                raise DatabaseError("Failed to create interaction", original_error=e)

    async def get_customer_interactions(self, customer_id: int, limit: int = 10) -> List[Interaction]:
        """Get recent interactions for a customer"""
        async with self.session() as session:
            try:
                stmt = select(Interaction).where(
                    Interaction.customer_id == customer_id
                ).order_by(Interaction.created_at.desc()).limit(limit)
                
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Failed to retrieve customer interactions: {str(e)}")
                raise DatabaseError("Failed to retrieve customer interactions", original_error=e)

    # Health Check
    async def health_check(self) -> bool:
        """Check if database is accessible"""
        try:
            async with self.session() as session:
                await session.execute(select(1))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

# Create singleton instance
db_service = DatabaseService()
