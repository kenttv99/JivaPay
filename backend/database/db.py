from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

def utcnow():
    # Возвращает aware datetime в UTC (с tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

# =====================
# === РОЛИ ПОЛЬЗОВАТЕЛЕЙ (Roles)
# =====================
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    applies_to: Mapped[Optional[str]] = mapped_column(String(50)) # 'admin', 'support', 'all'

    users: Mapped[List["User"]] = relationship(back_populates="role")

# =====================
# === АУДИТ ЛОГ (Audit Log) - ПЕРЕМЕЩЕНО ВЫШЕ User
# =====================
class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id', name='fk_audit_user_id'), nullable=True) # User might be null for system actions
    ip_address: Mapped[Optional[str]] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(255), index=True)
    target_entity: Mapped[Optional[str]] = mapped_column(String(100))
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs") # Made Optional to match user_id

    __table_args__ = (
        Index('ix_audit_logs_target', 'target_entity', 'target_id'),
    )

# =====================
# === ПОЛЬЗОВАТЕЛИ (Users) - Общая таблица
# =====================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    role: Mapped["Role"] = relationship(back_populates="users")

    # Relationships to specific profile tables
    merchant_profile: Mapped[Optional["Merchant"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trader_profile: Mapped[Optional["Trader"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    admin_profile: Mapped[Optional["Admin"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    support_profile: Mapped[Optional["Support"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # New TeamLead profile (manages traders)
    teamlead_profile: Mapped[Optional["TeamLead"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")

# =====================
# === МЕРЧАНТЫ (Merchants)
# =====================
class Merchant(Base):
    __tablename__ = "merchants"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    two_factor_auth_token: Mapped[Optional[str]] = mapped_column(String(32))
    verification_level: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped["User"] = relationship(back_populates="merchant_profile")
    stores: Mapped[List["MerchantStore"]] = relationship(back_populates="merchant", cascade="all, delete-orphan")
    incoming_orders: Mapped[List["IncomingOrder"]] = relationship(back_populates="merchant")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="merchant")
    # Дружественная связь к BalanceStore через промежуточную таблицу merchant_stores.
    balance_stores: Mapped[List["BalanceStore"]] = relationship(
        "BalanceStore",
        secondary="merchant_stores",
        primaryjoin="Merchant.id == MerchantStore.merchant_id",
        secondaryjoin="BalanceStore.store_id == MerchantStore.id",
        viewonly=True,
        lazy="dynamic",
    )
    store_addresses: Mapped[List["StoreAddress"]] = relationship(back_populates="merchant") # Assuming relationship exists

class MerchantStore(Base):
    __tablename__ = "merchant_stores"
    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    fiat_currency_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    public_api_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True) # Made unique
    private_api_key: Mapped[str] = mapped_column(String(255), nullable=False) # Needs hashing in app logic
    lower_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=0)
    upper_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=10000)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    trafic_access: Mapped[bool] = mapped_column(Boolean, default=False)
    access: Mapped[bool] = mapped_column(Boolean, default=True)
    pay_in_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    pay_out_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    callback_url: Mapped[Optional[str]] = mapped_column(String(512))
    secret_key: Mapped[Optional[str]] = mapped_column(String(255)) # Needs secure handling
    gateway_require_customer_id_param: Mapped[bool] = mapped_column(Boolean, default=False)
    gateway_require_amount_param: Mapped[bool] = mapped_column(Boolean, default=False)

    merchant: Mapped["Merchant"] = relationship(back_populates="stores")
    crypto_currency: Mapped["CryptoCurrency"] = relationship(back_populates="merchant_stores")
    fiat_currency: Mapped["FiatCurrency"] = relationship(back_populates="merchant_stores")
    store_commissions: Mapped[List["StoreCommission"]] = relationship(back_populates="store", cascade="all, delete-orphan")
    store_gateways: Mapped[List["StoreGateway"]] = relationship(back_populates="store", cascade="all, delete-orphan")
    balance_stores: Mapped[List["BalanceStore"]] = relationship(back_populates="store", cascade="all, delete-orphan")
    balance_store_history: Mapped[List["BalanceStoreHistory"]] = relationship(back_populates="store") # Removed cascade
    store_addresses: Mapped[List["StoreAddress"]] = relationship(back_populates="store", cascade="all, delete-orphan")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="store")
    incoming_orders: Mapped[List["IncomingOrder"]] = relationship(back_populates="store")

class StoreCommission(Base):
    __tablename__ = "store_commissions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    commission_payin: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    commission_payout: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    store: Mapped["MerchantStore"] = relationship(back_populates="store_commissions")

class StoreGateway(Base):
    __tablename__ = "store_gateways"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # redirect, api

    store: Mapped["MerchantStore"] = relationship(back_populates="store_gateways")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="gateway")

class BalanceStore(Base):
    __tablename__ = "balance_stores"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    store: Mapped["MerchantStore"] = relationship(back_populates="balance_stores")
    crypto_currency: Mapped["CryptoCurrency"] = relationship(back_populates="balance_stores")

class BalanceStoreHistory(Base):
    __tablename__ = "balance_store_history"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('order_history.id')) # Link to order
    balance_change: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'payout_completed', 'fee'
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    store: Mapped["MerchantStore"] = relationship(back_populates="balance_store_history")
    crypto_currency: Mapped["CryptoCurrency"] = relationship(back_populates="balance_store_history")
    order: Mapped[Optional["OrderHistory"]] = relationship(back_populates="balance_store_history")

class StoreAddress(Base):
    __tablename__ = "store_addresses"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    merchant_id: Mapped[int] = mapped_column(ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    fiat_currency_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="check", index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    store: Mapped["MerchantStore"] = relationship(back_populates="store_addresses")
    merchant: Mapped["Merchant"] = relationship(back_populates="store_addresses")
    fiat_currency: Mapped["FiatCurrency"] = relationship(back_populates="store_addresses")

# =====================
# === ТРЕЙДЕРЫ (Traders)
# =====================
class Trader(Base):
    __tablename__ = "traders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    preferred_fiat_currency_id: Mapped[Optional[int]] = mapped_column(ForeignKey('fiat_currencies.id'))
    crypto_currency_id: Mapped[Optional[int]] = mapped_column(ForeignKey('crypto_currencies.id')) # Usually one per trader?
    verification_level: Mapped[str] = mapped_column(String(50), default="UNVERIFIED")
    pay_in: Mapped[bool] = mapped_column(Boolean, default=False)
    pay_out: Mapped[bool] = mapped_column(Boolean, default=False)
    trafic_priority: Mapped[int] = mapped_column(Integer, default=5, index=True) # Priority for selection
    in_work: Mapped[bool] = mapped_column(Boolean, default=True, index=True) # Is trader active?
    two_factor_auth_token: Mapped[Optional[str]] = mapped_column(String(32))
    time_zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey('time_zones.id'))
    base_pay_in_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=0) # Base limit set before token creation
    base_pay_out_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=0) # Base limit set before token creation
    # Link to TeamLead supervising this trader (nullable)
    team_lead_id: Mapped[Optional[int]] = mapped_column(ForeignKey('teamleads.id', ondelete='SET NULL'), index=True)

    user: Mapped["User"] = relationship(back_populates="trader_profile")
    preferred_fiat_currency: Mapped[Optional["FiatCurrency"]] = relationship(foreign_keys=[preferred_fiat_currency_id])
    crypto_currency: Mapped[Optional["CryptoCurrency"]] = relationship()
    time_zone: Mapped[Optional["TimeZone"]] = relationship(back_populates="traders")
    # Relationship back to TeamLead
    team_lead: Mapped[Optional["TeamLead"]] = relationship(back_populates="traders", foreign_keys=[team_lead_id])

    trader_commissions: Mapped[List["TraderCommission"]] = relationship(back_populates="trader", cascade="all, delete-orphan")
    trader_addresses: Mapped[List["TraderAddress"]] = relationship(back_populates="trader", cascade="all, delete-orphan")
    balance_trader_fiat_history: Mapped[List["BalanceTraderFiatHistory"]] = relationship(back_populates="trader") # Removed cascade
    balance_trader_crypto_history: Mapped[List["BalanceTraderCryptoHistory"]] = relationship(back_populates="trader") # Removed cascade
    req_traders: Mapped[List["ReqTrader"]] = relationship(back_populates="trader", cascade="all, delete-orphan")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="trader")
    balance_traders: Mapped[List["BalanceTrader"]] = relationship(back_populates="trader", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_trader_priority_lookup', 'in_work', 'trafic_priority'), # Keep this index
    )

class TraderCommission(Base):
    __tablename__ = "trader_commissions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    commission_payin: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    commission_payout: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    trader: Mapped["Trader"] = relationship(back_populates="trader_commissions")

class TraderAddress(Base):
    __tablename__ = "trader_addresses"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    fiat_currency_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="check", index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    trader: Mapped["Trader"] = relationship(back_populates="trader_addresses")
    fiat_currency: Mapped["FiatCurrency"] = relationship(back_populates="trader_addresses")

class BalanceTrader(Base):
    __tablename__ = "balance_traders"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_currency_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    trader: Mapped["Trader"] = relationship(back_populates="balance_traders")
    fiat_currency: Mapped["FiatCurrency"] = relationship(back_populates="balance_traders")

class BalanceTraderFiatHistory(Base):
    __tablename__ = "balance_trader_fiat_history"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('order_history.id')) # Link to order
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    network: Mapped[Optional[str]] = mapped_column(String(50))
    balance_change: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    description: Mapped[Optional[str]] = mapped_column(Text)

    trader: Mapped["Trader"] = relationship(back_populates="balance_trader_fiat_history")
    fiat: Mapped["FiatCurrency"] = relationship(foreign_keys=[fiat_id], back_populates="balance_trader_fiat_history")
    order: Mapped[Optional["OrderHistory"]] = relationship(back_populates="balance_trader_fiat_history")

    __table_args__ = (Index('ix_balance_trader_fiat_history_op_type', 'operation_type'),)

class BalanceTraderCryptoHistory(Base):
    __tablename__ = "balance_trader_crypto_history"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('order_history.id')) # Link to order
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    network: Mapped[str] = mapped_column(String(50), nullable=False) # Network mandatory for crypto
    balance_change: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    description: Mapped[Optional[str]] = mapped_column(Text)

    trader: Mapped["Trader"] = relationship(back_populates="balance_trader_crypto_history")
    crypto_currency: Mapped["CryptoCurrency"] = relationship(back_populates="trader_balance_history")
    order: Mapped[Optional["OrderHistory"]] = relationship(back_populates="balance_trader_crypto_history")

    __table_args__ = (Index('ix_balance_trader_crypto_history_op_type', 'operation_type'),)

class ReqTrader(Base):
    __tablename__ = "req_traders"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id', ondelete='CASCADE'), nullable=False, index=True)
    owner_of_requisites_id: Mapped[int] = mapped_column(ForeignKey('owner_of_requisites.id'), nullable=False)
    method_id: Mapped[int] = mapped_column(ForeignKey('payment_methods.id'), nullable=False)
    bank_id: Mapped[int] = mapped_column(ForeignKey('banks.id'), nullable=False)
    req_number: Mapped[str] = mapped_column(String(255), nullable=False) # Needs encryption/masking
    status: Mapped[str] = mapped_column(String(50), default="approve", index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    distribution_weight: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=5) # Default should match default trafic_priority. Actual value set on creation based on trader.trafic_priority.
    is_excluded_from_distribution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    fiat: Mapped["FiatCurrency"] = relationship()
    trader: Mapped["Trader"] = relationship(back_populates="req_traders")
    owner_of_requisites: Mapped["OwnerOfRequisites"] = relationship(back_populates="requisites")
    method: Mapped["PaymentMethod"] = relationship(back_populates="req_traders")
    bank: Mapped["BanksTrader"] = relationship(back_populates="req_traders")

    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="requisite")
    full_requisites_settings: Mapped[Optional["FullRequisitesSettings"]] = relationship(back_populates="requisite", uselist=False, cascade="all, delete-orphan") # Changed to Optional

    __table_args__ = (Index('ix_req_trader_status', 'status'),)

class OwnerOfRequisites(Base):
    __tablename__ = "owner_of_requisites"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fio: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    requisites: Mapped[List["ReqTrader"]] = relationship(back_populates="owner_of_requisites")

class FullRequisitesSettings(Base):
    __tablename__ = "full_requisites_settings"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requisite_id: Mapped[int] = mapped_column(ForeignKey('req_traders.id', ondelete='CASCADE'), unique=True, nullable=False) # Added unique=True
    pay_in: Mapped[bool] = mapped_column(Boolean, default=False)
    pay_out: Mapped[bool] = mapped_column(Boolean, default=False)
    lower_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=0)
    upper_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=10000)
    total_limit: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=100000)
    turnover_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    turnover_day_max: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False, default=50000)
    requisite: Mapped["ReqTrader"] = relationship(back_populates="full_requisites_settings")

# =====================
# === ОРДЕРА (Orders)
# =====================
class OrderHistory(Base):
    __tablename__ = "order_history"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incoming_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('incoming_orders.id'), unique=True) # Made Optional, unique still valid
    hash_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    trader_id: Mapped[int] = mapped_column(ForeignKey('traders.id'), nullable=False, index=True)
    requisite_id: Mapped[int] = mapped_column(ForeignKey('req_traders.id'), nullable=False)
    merchant_id: Mapped[int] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    gateway_id: Mapped[Optional[int]] = mapped_column(ForeignKey('store_gateways.id')) # Made Optional
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id'), nullable=False, index=True)
    method_id: Mapped[int] = mapped_column(ForeignKey('payment_methods.id'), nullable=False)
    bank_id: Mapped[int] = mapped_column(ForeignKey('banks.id'), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    order_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    exchange_rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    amount_currency: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False) # Amount in crypto for payout, or fiat for payin? Clarify usage. Usually amount_crypto / amount_fiat
    total_fiat: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    amount_crypto: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8)) # Added, represents crypto amount
    amount_fiat: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 2)) # Added, represents fiat amount
    store_commission: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    trader_commission: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    client_id: Mapped[Optional[str]] = mapped_column(String(255), index=True) # Added from description
    customer_id: Mapped[Optional[str]] = mapped_column(String(255)) # Added from incoming order
    customer_ip: Mapped[Optional[str]] = mapped_column(String(100)) # Added from incoming order
    payment_details_submitted: Mapped[bool] = mapped_column(Boolean, default=False)  # Added from description

    # Added fields for receipt URLs and cancellation details
    receipt_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    trader_receipt_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    incoming_order: Mapped[Optional["IncomingOrder"]] = relationship(back_populates="assigned_order_rel") # Renamed relationship
    trader: Mapped["Trader"] = relationship(back_populates="order_histories")
    merchant: Mapped["Merchant"] = relationship(back_populates="order_histories")
    store: Mapped["MerchantStore"] = relationship(back_populates="order_histories")
    gateway: Mapped[Optional["StoreGateway"]] = relationship(back_populates="order_histories")
    requisite: Mapped["ReqTrader"] = relationship(back_populates="order_histories")
    method: Mapped["PaymentMethod"] = relationship(back_populates="order_histories")
    bank: Mapped["BanksTrader"] = relationship(back_populates="order_histories")
    crypto_currency: Mapped["CryptoCurrency"] = relationship()
    fiat: Mapped["FiatCurrency"] = relationship(foreign_keys=[fiat_id])

    balance_store_history: Mapped[List["BalanceStoreHistory"]] = relationship(back_populates="order")
    balance_trader_fiat_history: Mapped[List["BalanceTraderFiatHistory"]] = relationship(back_populates="order")
    balance_trader_crypto_history: Mapped[List["BalanceTraderCryptoHistory"]] = relationship(back_populates="order")

    # Relationship to uploaded documents
    uploaded_documents: Mapped[List["UploadedDocument"]] = relationship("UploadedDocument", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (Index('ix_order_history_created_at', 'created_at'), Index('ix_order_history_client_id', 'client_id'),)

class IncomingOrder(Base):
    __tablename__ = "incoming_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # --- Request Details ---
    merchant_id: Mapped[int] = mapped_column(ForeignKey('merchants.id'), nullable=False) # Removed cascade
    store_id: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id'), nullable=False) # Removed cascade
    gateway_id: Mapped[Optional[int]] = mapped_column(ForeignKey('store_gateways.id'))
    target_method_id: Mapped[Optional[int]] = mapped_column(ForeignKey('payment_methods.id'))
    target_bank_id: Mapped[Optional[int]] = mapped_column(ForeignKey('banks.id'))

    # --- Currency, Amount, Rate and Commission ---
    fiat_currency_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(ForeignKey('crypto_currencies.id'), nullable=False)
    amount_fiat: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 2)) # Use amount_fiat/amount_crypto instead of total_fiat/amount_currency
    amount_crypto: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8))
    exchange_rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    store_commission: Mapped[Decimal] = mapped_column(DECIMAL(20, 2), nullable=False)
    order_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # 'pay_in', 'pay_out'

    # --- Customer Info ---
    customer_id: Mapped[Optional[str]] = mapped_column(String(255))
    customer_ip: Mapped[Optional[str]] = mapped_column(String(100))
    return_url: Mapped[Optional[str]] = mapped_column(String(512))
    callback_url: Mapped[Optional[str]] = mapped_column(String(512)) # Added callback URL
    client_id: Mapped[Optional[str]] = mapped_column(String(255), index=True) # Added from description

    # --- Processing State ---
    status: Mapped[str] = mapped_column(String(50), default='new', nullable=False, index=True) # new, processing, assigned, failed, retrying
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    payment_details_submitted: Mapped[bool] = mapped_column(Boolean, default=False) # Added from description

    # --- Assignment Link ---
    assigned_order_rel: Mapped[Optional["OrderHistory"]] = relationship(back_populates="incoming_order") # Renamed relationship

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # --- Relationships (Define explicitly if needed for direct access) ---
    merchant: Mapped["Merchant"] = relationship(back_populates="incoming_orders")
    store: Mapped["MerchantStore"] = relationship(back_populates="incoming_orders")
    gateway: Mapped[Optional["StoreGateway"]] = relationship()
    fiat_currency: Mapped["FiatCurrency"] = relationship()
    crypto_currency: Mapped["CryptoCurrency"] = relationship()
    target_method: Mapped[Optional["PaymentMethod"]] = relationship(foreign_keys=[target_method_id])
    target_bank: Mapped[Optional["BanksTrader"]] = relationship(foreign_keys=[target_bank_id])

    # --- Indexes (using __table_args__) ---
    __table_args__ = (
        Index('ix_incoming_orders_status_created', 'status', 'created_at'),
        Index('ix_incoming_orders_merchant_store', 'merchant_id', 'store_id'),
        Index('ix_incoming_orders_client_id', 'client_id'),
    )

# =====================
# === ПОДДЕРЖКА и АДМИНЫ (Support & Admins)
# =====================
class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False) # Or first/last name
    # Permission flags
    can_manage_other_admins: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_supports: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_merchants: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_traders: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_system_settings: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_limits: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_full_logs: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_handle_appeals: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Add other specific permissions as needed

    user: Mapped["User"] = relationship(back_populates="admin_profile")

class Support(Base):
    __tablename__ = "supports"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False) # Or first/last name
    # Permission flags
    can_edit_trader_settings: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_orders: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_orders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_handle_appeals: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_sensitive_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Add other specific permissions as needed

    user: Mapped["User"] = relationship(back_populates="support_profile")

# =====================
# === ОБЩИЕ/СПРАВОЧНИКИ (Common/Reference)
# =====================
class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False) # e.g., BTC
    fiat: Mapped[str] = mapped_column(String(10), nullable=False) # e.g., USD
    buy_rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    sell_rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    median_rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class BanksTrader(Base):
    __tablename__ = "banks" # Renamed table from 'banks' for clarity? Assuming it's BanksTrader.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    public_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    interbank: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    req_traders: Mapped[List["ReqTrader"]] = relationship(back_populates="bank")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="bank")
    avalible_bank_methods: Mapped[List["AvalibleBankMethod"]] = relationship(back_populates="bank")
    fiat: Mapped["FiatCurrency"] = relationship() # Added relationship to FiatCurrency

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    method_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    public_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    req_traders: Mapped[List["ReqTrader"]] = relationship(back_populates="method")
    order_histories: Mapped[List["OrderHistory"]] = relationship(back_populates="method")
    avalible_bank_methods: Mapped[List["AvalibleBankMethod"]] = relationship(back_populates="method")
    fiat: Mapped["FiatCurrency"] = relationship() # Added relationship to FiatCurrency

class AvalibleBankMethod(Base):
    __tablename__ = "avalible_bank_methods"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fiat_id: Mapped[int] = mapped_column(ForeignKey('fiat_currencies.id'), nullable=False)
    bank_id: Mapped[int] = mapped_column(ForeignKey('banks.id'), nullable=False)
    method_id: Mapped[int] = mapped_column(ForeignKey('payment_methods.id'), nullable=False)
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    bank: Mapped["BanksTrader"] = relationship(back_populates="avalible_bank_methods")
    method: Mapped["PaymentMethod"] = relationship(back_populates="avalible_bank_methods")
    fiat: Mapped["FiatCurrency"] = relationship()

    __table_args__ = (Index('ix_avalible_bank_method_lookup', 'fiat_id', 'bank_id', 'method_id', unique=True),) # Added unique index

class FiatCurrency(Base):
    __tablename__ = "fiat_currencies"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('countries.id'), nullable=False)
    currency_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g., RUB
    currency_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False) # e.g., RUB ISO code
    public_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    traders_preferred: Mapped[List["Trader"]] = relationship(foreign_keys="[Trader.preferred_fiat_currency_id]", back_populates="preferred_fiat_currency")
    trader_addresses: Mapped[List["TraderAddress"]] = relationship(back_populates="fiat_currency")
    balance_trader_fiat_history: Mapped[List["BalanceTraderFiatHistory"]] = relationship(foreign_keys="[BalanceTraderFiatHistory.fiat_id]", back_populates="fiat")
    balance_traders: Mapped[List["BalanceTrader"]] = relationship(back_populates="fiat_currency")
    store_addresses: Mapped[List["StoreAddress"]] = relationship(back_populates="fiat_currency")
    merchant_stores: Mapped[List["MerchantStore"]] = relationship(back_populates="fiat_currency")

    country: Mapped["Country"] = relationship(back_populates="fiat_currencies")

class CryptoCurrency(Base):
    __tablename__ = "crypto_currencies"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    currency_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g., Bitcoin
    currency_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False) # e.g., BTC
    public_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    merchant_stores: Mapped[List["MerchantStore"]] = relationship(back_populates="crypto_currency")
    balance_stores: Mapped[List["BalanceStore"]] = relationship(back_populates="crypto_currency")
    balance_store_history: Mapped[List["BalanceStoreHistory"]] = relationship(back_populates="crypto_currency")
    trader_balance_history: Mapped[List["BalanceTraderCryptoHistory"]] = relationship(back_populates="crypto_currency")

class Country(Base):
    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    country_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Increased length
    country_code_iso: Mapped[str] = mapped_column(String(2), unique=True, nullable=False) # Added ISO 3166-1 alpha-2 code
    public_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    fiat_currencies: Mapped[List["FiatCurrency"]] = relationship(back_populates="country")

class TimeZone(Base):
    __tablename__ = "time_zones"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True) # e.g., "Europe/Moscow", made unique
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "(UTC+03:00) Moscow"
    utc_offset: Mapped[int] = mapped_column(Integer, nullable=False)  # Offset in minutes
    access: Mapped[bool] = mapped_column(Boolean, default=True)
    regions: Mapped[Optional[str]] = mapped_column(Text) # Changed to Text for potentially longer list

    traders: Mapped[List["Trader"]] = relationship(back_populates="time_zone")

    def __repr__(self):
        return f"<TimeZone(name='{self.name}', display_name='{self.display_name}')>"

class RequisiteDistributionSettings(Base):
    __tablename__ = "requisite_distribution_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False, default="round_robin")
    params: Mapped[Optional[dict]] = mapped_column(JSON)
    scope: Mapped[str] = mapped_column(String(100), nullable=False, default="global") # e.g., global, trader:1, method:2
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class ConfigurationSetting(Base):
    __tablename__ = "configuration_settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, index=True, comment="Unique key identifying the configuration setting")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="Value of the configuration setting (stored as text)")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="Description of the setting for administrators")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), comment="Timestamp of creation")
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), onupdate=func.now(), comment="Timestamp of last update")

    def __repr__(self):
        return f"<ConfigurationSetting(key='{self.key}', value='{self.value[:20]}...')>"


Index('ix_trader_address_status', TraderAddress.status)
Index('ix_store_address_status', StoreAddress.status)

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('order_history.id', ondelete='CASCADE'), nullable=False)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    order: Mapped["OrderHistory"] = relationship(back_populates="uploaded_documents")

# =====================
# === ТИМЛИДЫ (TeamLeads)
# =====================

class TeamLead(Base):
    """TeamLead oversees a group of traders, can enable/disable their traffic and view stats."""

    __tablename__ = "teamleads"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped["User"] = relationship(back_populates="teamlead_profile")
    traders: Mapped[List["Trader"]] = relationship(back_populates="team_lead")

    