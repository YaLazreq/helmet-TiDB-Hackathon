"""
Modern TiDB Implementation with Python - Best Practices 2025
============================================================

This implementation follows current best practices:
- SQLAlchemy 2.0+ modern style with async support
- Proper connection pooling and session management
- Type hints and Pydantic integration
- Environment-based configuration
- Comprehensive error handling and logging
- Performance optimizations for TiDB
"""

import asyncio
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass
from enum import Enum

# Core dependencies
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Boolean,
    DECIMAL,
    ForeignKey,
    Index,
    select,
    insert,
    update,
    delete,
    and_,
    or_,
    func,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.sql import text

# Optional: Pydantic for data validation
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration Management
# =============================================================================


class TiDBSettings(BaseSettings):
    """Environment-based configuration for TiDB connection"""

    # Database connection
    tidb_host: str = "localhost"
    tidb_port: int = 4000
    tidb_user: str = "root"
    tidb_password: str = ""
    tidb_database: str = "tidb_app"

    # SSL configuration for TiDB Cloud
    tidb_ssl_ca: Optional[str] = None
    tidb_ssl_verify: bool = False

    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour

    # Performance settings
    echo_sql: bool = False
    query_cache_size: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False


# =============================================================================
# Database Models (SQLAlchemy 2.0 Style)
# =============================================================================


class Base(DeclarativeBase):
    """Base class for all database models"""

    # Common columns for all tables
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


# Enums for better type safety
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    TRANSFER = "transfer"
    RETURN = "return"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SiteType(str, Enum):
    WAREHOUSE = "warehouse"
    STORE = "store"
    OFFICE = "office"
    OTHER = "other"


# Model definitions
class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[bool] = mapped_column(Boolean, default=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(100))

    # Indexes for performance
    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_email", "email"),
        Index("idx_active", "is_active"),
    )


class ProductCategory(Base):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_categories.id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Self-referential relationship for hierarchical categories
    parent: Mapped[Optional["ProductCategory"]] = relationship(
        "ProductCategory", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["ProductCategory"]] = relationship(
        "ProductCategory", back_populates="parent"
    )

    __table_args__ = (
        Index("idx_name", "name"),
        Index("idx_parent", "parent_id"),
        Index("idx_active", "is_active"),
    )


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_categories.id")
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    cost: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_stock_level: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    weight: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 3))
    dimensions: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    category: Mapped[Optional[ProductCategory]] = relationship("ProductCategory")

    __table_args__ = (
        Index("idx_sku", "sku"),
        Index("idx_category", "category_id"),
        Index("idx_price", "price"),
        Index("idx_stock", "stock_quantity"),
        Index("idx_active", "is_active"),
    )


class Site(Base):
    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    site_type: Mapped[SiteType] = mapped_column(
        ENUM(SiteType), default=SiteType.WAREHOUSE
    )

    __table_args__ = (
        Index("idx_code", "code"),
        Index("idx_type", "site_type"),
        Index("idx_active", "is_active"),
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    payment_terms: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(3, 2))

    __table_args__ = (
        Index("idx_code", "code"),
        Index("idx_name", "name"),
        Index("idx_active", "is_active"),
    )


class Order(Base):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"))
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"))
    order_type: Mapped[OrderType] = mapped_column(ENUM(OrderType), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        ENUM(OrderStatus), default=OrderStatus.PENDING
    )
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0)
    tax_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0)
    shipping_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    required_date: Mapped[Optional[date]] = mapped_column(Date)
    shipped_date: Mapped[Optional[date]] = mapped_column(Date)
    delivered_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped[Optional[User]] = relationship("User")
    site: Mapped[Optional[Site]] = relationship("Site")
    supplier: Mapped[Optional[Supplier]] = relationship("Supplier")

    __table_args__ = (
        Index("idx_order_number", "order_number"),
        Index("idx_user", "user_id"),
        Index("idx_site", "site_id"),
        Index("idx_supplier", "supplier_id"),
        Index("idx_status", "status"),
        Index("idx_order_date", "order_date"),
        Index("idx_type_status", "order_type", "status"),
    )


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id"))
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"))
    task_type: Mapped[str] = mapped_column(String(20), default="other")
    priority: Mapped[TaskPriority] = mapped_column(
        ENUM(TaskPriority), default=TaskPriority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        ENUM(TaskStatus), default=TaskStatus.PENDING
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    assignee: Mapped[Optional[User]] = relationship("User", foreign_keys=[assigned_to])
    creator: Mapped[Optional[User]] = relationship("User", foreign_keys=[created_by])
    site: Mapped[Optional[Site]] = relationship("Site")
    order: Mapped[Optional[Order]] = relationship("Order")

    __table_args__ = (
        Index("idx_assigned_to", "assigned_to"),
        Index("idx_created_by", "created_by"),
        Index("idx_site", "site_id"),
        Index("idx_status", "status"),
        Index("idx_priority", "priority"),
        Index("idx_due_date", "due_date"),
        Index("idx_status_assignee", "status", "assigned_to"),
    )


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    category_id: Optional[int] = None
    price: Decimal
    cost: Optional[Decimal] = None
    stock_quantity: int = 0
    min_stock_level: int = 0


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    sku: str
    category_id: Optional[int]
    price: Decimal
    cost: Optional[Decimal]
    stock_quantity: int
    min_stock_level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Database Connection and Session Management
# =============================================================================


class TiDBManager:
    """Modern TiDB connection manager with async support"""

    def __init__(self, settings: TiDBSettings):
        self.settings = settings
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None

    def get_connection_url(self, async_driver: bool = False) -> str:
        """Build connection URL with proper SSL settings"""
        driver = "mysql+aiomysql" if async_driver else "mysql+pymysql"

        url = (
            f"{driver}://{self.settings.tidb_user}:"
            f"{self.settings.tidb_password}@{self.settings.tidb_host}:"
            f"{self.settings.tidb_port}/{self.settings.tidb_database}"
        )

        # Add SSL parameters for TiDB Cloud
        if self.settings.tidb_ssl_ca or self.settings.tidb_ssl_verify:
            params = []
            if self.settings.tidb_ssl_ca:
                params.append(f"ssl_ca={self.settings.tidb_ssl_ca}")
            if self.settings.tidb_ssl_verify:
                params.append("ssl_verify_cert=true")
                params.append("ssl_verify_identity=true")
            if params:
                url += "?" + "&".join(params)

        return url

    def create_engine(self):
        """Create synchronous database engine"""
        connect_args = {
            "charset": "utf8mb4",
            "autocommit": False,
        }

        if self.settings.tidb_ssl_ca:
            connect_args.update(
                {
                    "ssl_ca": self.settings.tidb_ssl_ca,
                    "ssl_verify_cert": True,
                    "ssl_verify_identity": True,
                }
            )

        self.engine = create_engine(
            self.get_connection_url(async_driver=False),
            connect_args=connect_args,
            poolclass=QueuePool,
            pool_size=self.settings.pool_size,
            max_overflow=self.settings.max_overflow,
            pool_timeout=self.settings.pool_timeout,
            pool_recycle=self.settings.pool_recycle,
            echo=self.settings.echo_sql,
            future=True,  # Use SQLAlchemy 2.0 style
        )

        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        logger.info("Synchronous database engine created")
        return self.engine

    def create_async_engine(self):
        """Create asynchronous database engine"""
        connect_args = {
            "charset": "utf8mb4",
            "autocommit": False,
        }

        self.async_engine = create_async_engine(
            self.get_connection_url(async_driver=True),
            connect_args=connect_args,
            poolclass=QueuePool,
            pool_size=self.settings.pool_size,
            max_overflow=self.settings.max_overflow,
            pool_timeout=self.settings.pool_timeout,
            pool_recycle=self.settings.pool_recycle,
            echo=self.settings.echo_sql,
        )

        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine, expire_on_commit=False
        )

        logger.info("Asynchronous database engine created")
        return self.async_engine

    async def create_tables(self):
        """Create all database tables"""
        if not self.async_engine:
            self.create_async_engine()

        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions"""
        if not self.async_session_factory:
            self.create_async_engine()

        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    def get_sync_session(self):
        """Get synchronous session"""
        if not self.session_factory:
            self.create_engine()
        return self.session_factory()

    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def close(self):
        """Clean up database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# =============================================================================
# Repository Pattern with Modern SQLAlchemy
# =============================================================================


class BaseRepository:
    """Base repository with common CRUD operations"""

    def __init__(self, db_manager: TiDBManager, model_class):
        self.db = db_manager
        self.model = model_class

    async def create(self, data: BaseModel) -> Dict[str, Any]:
        """Create new record"""
        async with self.db.get_session() as session:
            db_obj = self.model(**data.model_dump(exclude_unset=True))
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return self._to_dict(db_obj)

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj) if obj else None

    async def get_multi(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple records with pagination and filtering"""
        async with self.db.get_session() as session:
            stmt = select(self.model)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]

    async def update(self, id: int, data: BaseModel) -> Optional[Dict[str, Any]]:
        """Update existing record"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()

            if not obj:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)

            await session.commit()
            await session.refresh(obj)
            return self._to_dict(obj)

    async def delete(self, id: int) -> bool:
        """Delete record by ID"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()

            if not obj:
                return False

            await session.delete(obj)
            await session.commit()
            return True

    def _to_dict(self, obj) -> Dict[str, Any]:
        """Convert SQLAlchemy object to dictionary"""
        if obj is None:
            return None
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class UserRepository(BaseRepository):
    """User-specific repository operations"""

    def __init__(self, db_manager: TiDBManager):
        super().__init__(db_manager, User)

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.username == username)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj) if obj else None

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.email == email)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj) if obj else None


class ProductRepository(BaseRepository):
    """Product-specific repository operations"""

    def __init__(self, db_manager: TiDBManager):
        super().__init__(db_manager, Product)

    async def get_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.sku == sku)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj) if obj else None

    async def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Get products with stock below minimum level"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(
                self.model.stock_quantity <= self.model.min_stock_level
            )
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]

    async def get_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get products by category"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(
                and_(
                    self.model.category_id == category_id, self.model.is_active == True
                )
            )
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]


class OrderRepository(BaseRepository):
    """Order-specific repository operations"""

    def __init__(self, db_manager: TiDBManager):
        super().__init__(db_manager, Order)

    async def get_by_status(self, status: OrderStatus) -> List[Dict[str, Any]]:
        """Get orders by status"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.status == status)
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]

    async def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get orders by user"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.user_id == user_id)
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]


class TaskRepository(BaseRepository):
    """Task-specific repository operations"""

    def __init__(self, db_manager: TiDBManager):
        super().__init__(db_manager, Task)

    async def get_by_assignee(self, user_id: int) -> List[Dict[str, Any]]:
        """Get tasks assigned to user"""
        async with self.db.get_session() as session:
            stmt = select(self.model).where(self.model.assigned_to == user_id)
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]

    async def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        async with self.db.get_session() as session:
            today = datetime.now().date()
            stmt = select(self.model).where(
                and_(
                    self.model.due_date < today,
                    self.model.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            result = await session.execute(stmt)
            return [self._to_dict(obj) for obj in result.scalars().all()]


# =============================================================================
# Application Service Layer
# =============================================================================


class TiDBApp:
    """Main application class with service layer"""

    def __init__(self, settings: TiDBSettings = None):
        self.settings = settings or TiDBSettings()
        self.db_manager = TiDBManager(self.settings)
        self.repositories = {}

    async def initialize(self):
        """Initialize application and create database tables"""
        # Create async engine
        self.db_manager.create_async_engine()

        # Create tables
        await self.db_manager.create_tables()

        # Initialize repositories
        self.repositories = {
            "users": UserRepository(self.db_manager),
            "products": ProductRepository(self.db_manager),
            "product_categories": BaseRepository(self.db_manager, ProductCategory),
            "sites": BaseRepository(self.db_manager, Site),
            "suppliers": BaseRepository(self.db_manager, Supplier),
            "orders": OrderRepository(self.db_manager),
            "tasks": TaskRepository(self.db_manager),
        }

        logger.info("TiDB application initialized successfully")

        # Run health check
        health_ok = await self.db_manager.health_check()
        if not health_ok:
            raise RuntimeError("Database health check failed")

    def get_repository(self, name: str) -> BaseRepository:
        """Get repository by name"""
        return self.repositories.get(name)

    async def close(self):
        """Clean up resources"""
        await self.db_manager.close()


# =============================================================================
# Performance Optimization Functions
# =============================================================================


class TiDBOptimizer:
    """Performance optimization utilities for TiDB"""

    def __init__(self, db_manager: TiDBManager):
        self.db = db_manager

    async def analyze_tables(self):
        """Run ANALYZE TABLE for better query optimization"""
        tables = [
            "users",
            "products",
            "product_categories",
            "sites",
            "suppliers",
            "orders",
            "tasks",
        ]

        async with self.db.get_session() as session:
            for table in tables:
                await session.execute(text(f"ANALYZE TABLE {table}"))
                logger.info(f"Analyzed table: {table}")

    async def get_table_stats(self) -> Dict[str, Dict]:
        """Get table statistics for monitoring"""
        stats = {}
        tables = [
            "users",
            "products",
            "product_categories",
            "sites",
            "suppliers",
            "orders",
            "tasks",
        ]

        async with self.db.get_session() as session:
            for table in tables:
                result = await session.execute(
                    text(
                        f"""
                    SELECT 
                        table_name,
                        table_rows,
                        data_length,
                        index_length,
                        (data_length + index_length) as total_size
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                    """
                    )
                )
                row = result.fetchone()
                if row:
                    stats[table] = {
                        "rows": row.table_rows,
                        "data_size": row.data_length,
                        "index_size": row.index_length,
                        "total_size": row.total_size,
                    }

        return stats

    async def optimize_queries(self):
        """Run query optimization recommendations"""
        recommendations = []

        async with self.db.get_session() as session:
            # Check for unused indexes
            result = await session.execute(
                text(
                    """
                SELECT DISTINCT 
                    TABLE_NAME, 
                    INDEX_NAME 
                FROM information_schema.statistics 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND INDEX_NAME != 'PRIMARY'
            """
                )
            )

            indexes = result.fetchall()
            for index in indexes:
                # This is a simplified check - in practice you'd want more sophisticated analysis
                recommendations.append(
                    f"Review index usage: {index.TABLE_NAME}.{index.INDEX_NAME}"
                )

        return recommendations


# =============================================================================
# Bulk Operations for Better Performance
# =============================================================================


class BulkOperations:
    """Optimized bulk operations for TiDB"""

    def __init__(self, db_manager: TiDBManager):
        self.db = db_manager

    async def bulk_insert_products(self, products: List[ProductCreate]) -> List[int]:
        """Bulk insert products with optimized performance"""
        async with self.db.get_session() as session:
            # Use bulk insert for better performance
            product_dicts = [p.model_dump() for p in products]

            # Insert in batches to avoid timeout
            batch_size = 1000
            inserted_ids = []

            for i in range(0, len(product_dicts), batch_size):
                batch = product_dicts[i : i + batch_size]

                # Use SQLAlchemy's bulk insert
                stmt = insert(Product).values(batch)
                result = await session.execute(stmt)

                # Get inserted IDs (TiDB specific)
                first_id = result.lastrowid
                batch_ids = list(range(first_id, first_id + len(batch)))
                inserted_ids.extend(batch_ids)

            await session.commit()
            logger.info(f"Bulk inserted {len(products)} products")

            return inserted_ids

    async def bulk_update_stock(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update product stock levels"""
        async with self.db.get_session() as session:
            updated_count = 0

            for update_data in updates:
                stmt = (
                    update(Product)
                    .where(Product.sku == update_data["sku"])
                    .values(stock_quantity=update_data["stock_quantity"])
                )
                result = await session.execute(stmt)
                updated_count += result.rowcount

            await session.commit()
            logger.info(f"Bulk updated stock for {updated_count} products")

            return updated_count


# =============================================================================
# Example Usage and Best Practices Demo
# =============================================================================


# async def main():
#     """Example usage demonstrating best practices"""

#     # Load configuration from environment
#     settings = TiDBSettings()

#     # Initialize application
#     app = TiDBApp(settings)

#     # try:
#         # Initialize database and repositories
#         await app.initialize()

#         # Example: Create users
#         user_repo = app.get_repository("users")

#         # Create sample users
#         users_data = [
#             UserCreate(
#                 username="john_doe",
#                 email="john@example.com",
#                 password_hash="hashed_password_123",
#                 first_name="John",
#                 last_name="Doe",
#             ),
#             UserCreate(
#                 username="jane_smith",
#                 email="jane@example.com",
#                 password_hash="hashed_password_456",
#                 first_name="Jane",
#                 last_name="Smith",
#             ),
#         ]

#         created_users = []
#         for user_data in users_data:
#             user = await user_repo.create(user_data)
#             created_users.append(user)
#             logger.info(f"Created user: {user['username']}")

#         # Example: Create product category
#         category_repo = app.get_repository("product_categories")
#         category_data = {
#             "name": "Electronics",
#             "description": "Electronic devices and accessories",
#             "is_active": True,
#         }

#         # Create category using raw data (BaseRepository handles it)
#     #     from pydantic import BaseModel

#     #     class CategoryCreate(BaseModel):
#     #         name: str
#     #         description: Optional[str] = None
#     #         parent_id: Optional[int] = None
#     #         is_active: bool = True

#     #     category = await category_repo.create(CategoryCreate(**category_data))
#     #     logger.info(f"Created category: {category['name']}")

#     #     # Example: Bulk create products
#     #     bulk_ops = BulkOperations(app.db_manager)
#     #     products_data = [
#     #         ProductCreate(
#     #             name=f"Product {i}",
#     #             sku=f"PROD-{i:04d}",
#     #             price=Decimal("99.99"),
#     #             cost=Decimal("59.99"),
#     #             category_id=category["id"],
#     #             stock_quantity=100,
#     #             min_stock_level=10,
#     #         )
#     #         for i in range(1, 101)  # Create 100 products
#     #     ]

#     #     inserted_ids = await bulk_ops.bulk_insert_products(products_data)
#     #     logger.info(f"Bulk created {len(inserted_ids)} products")

#     #     # Example: Query operations
#     #     product_repo = app.get_repository("products")

#     #     # Get products by category
#     #     products_in_category = await product_repo.get_by_category(category["id"])
#     #     logger.info(f"Found {len(products_in_category)} products in category")

#     #     # Get low stock products
#     #     low_stock = await product_repo.get_low_stock_products()
#     #     logger.info(f"Found {len(low_stock)} low stock products")

#     #     # Example: Performance monitoring
#     #     optimizer = TiDBOptimizer(app.db_manager)

#     #     # Analyze tables for query optimization
#     #     await optimizer.analyze_tables()

#     #     # Get table statistics
#     #     stats = await optimizer.get_table_stats()
#     #     for table_name, table_stats in stats.items():
#     #         logger.info(
#     #             f"Table {table_name}: {table_stats['rows']} rows, {table_stats['total_size']} bytes"
#     #         )

#     #     # Example: Advanced querying with filters
#     #     filtered_users = await user_repo.get_multi(
#     #         skip=0, limit=50, filters={"is_active": True}
#     #     )
#     #     logger.info(f"Found {len(filtered_users)} active users")

#     #     # Example: Update operations
#     #     if created_users:
#     #         user_id = created_users[0]["id"]
#     #         update_data = BaseModel()
#     #         update_data.first_name = "Updated John"

#     #         # Note: This is a simplified example. In practice, you'd use proper Pydantic models
#     #         # updated_user = await user_repo.update(user_id, update_data)
#     #         # logger.info(f"Updated user: {updated_user['first_name']}")

#     #     logger.info("Example operations completed successfully!")

#     # except Exception as e:
#     #     logger.error(f"Application error: {e}")
#     #     raise
#     # finally:
#     #     # Clean up resources
#     #     await app.close()
