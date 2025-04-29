from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional

Base = declarative_base()

def utcnow():
    # Возвращает aware datetime в UTC (с tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

# Пример каскадного удаления (оставлен в комментарии):
# Column(Integer, ForeignKey('table.id', ondelete='CASCADE'))
    

# =====================
# === МЕРЧАНТЫ (Merchants)
# =====================
class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    two_factor_auth_token = Column(String(32), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    access = Column(Boolean, default=True)

    stores = relationship("MerchantStore", back_populates="merchant", cascade="all, delete-orphan")
    order_histories = relationship("OrderHistory", back_populates="merchant")
    store_addresses = relationship("StoreAddress", back_populates="merchant")

class MerchantStore(Base):
    __tablename__ = "merchant_stores"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_name = Column(String(255), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    balance = Column(DECIMAL(20, 8), nullable=False)
    public_api_key = Column(String(255), nullable=False)
    private_api_key = Column(String(255), nullable=False)
    lower_limit = Column(DECIMAL(20, 2), nullable=False)
    upper_limit = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    trafic_access = Column(Boolean, default=False)
    access = Column(Boolean, default=True)
    pay_in_enabled = Column(Boolean, default=True)
    pay_out_enabled = Column(Boolean, default=True)
    
    merchant = relationship("Merchant", back_populates="stores")
    crypto_currency = relationship("CryptoCurrency", back_populates="merchant_stores")
    fiat_currency = relationship("FiatCurrency", back_populates="merchant_stores")
    store_commissions = relationship("StoreCommission", back_populates="store", cascade="all, delete-orphan")
    store_gateways = relationship("StoreGateway", back_populates="store", cascade="all, delete-orphan")
    balance_stores = relationship("BalanceStore", back_populates="store", cascade="all, delete-orphan")
    balance_store_history = relationship("BalanceStoreHistory", back_populates="store", cascade="all, delete-orphan")
    store_addresses = relationship("StoreAddress", back_populates="store", cascade="all, delete-orphan")
    order_histories = relationship("OrderHistory", back_populates="store")

class StoreCommission(Base):
    __tablename__ = "store_commissions"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    commission_payin = Column(DECIMAL(20, 2), nullable=False)
    commission_payout = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    store = relationship("MerchantStore", back_populates="store_commissions")

class StoreGateway(Base):
    __tablename__ = "store_gateways"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(50), nullable=False) #redirect, api

    store = relationship("MerchantStore", back_populates="store_gateways")
    order_histories = relationship("OrderHistory", back_populates="gateway")

class BalanceStore(Base):
    __tablename__ = "balance_stores"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    balance = Column(DECIMAL(20, 8), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    
    store = relationship("MerchantStore", back_populates="balance_stores")
    crypto_currency = relationship("CryptoCurrency", back_populates="balance_stores")

class BalanceStoreHistory(Base):
    __tablename__ = "balance_store_history"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    balance = Column(DECIMAL(20, 8), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    store = relationship("MerchantStore", back_populates="balance_store_history")
    crypto_currency = relationship("CryptoCurrency", back_populates="balance_store_history")

class StoreAddress(Base):
    __tablename__ = "store_addresses"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    address = Column(String(255), nullable=False)
    fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    status = Column(String(50), nullable=False, default="check", index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    store = relationship("MerchantStore", back_populates="store_addresses")
    merchant = relationship("Merchant", back_populates="store_addresses")
    fiat_currency = relationship("FiatCurrency", back_populates="store_addresses")

# =====================
# === ТРЕЙДЕРЫ (Traders)
# =====================
class Trader(Base):
    __tablename__ = "traders"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    preferred_fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=True)
    verification_level = Column(String(50), nullable=False, default="UNVERIFIED")
    pay_in = Column(Boolean, default=False)
    pay_out = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    trafic_priority = Column(Integer, nullable=False, default=5)
    in_work = Column(Boolean, default=True)
    trafic_access = Column(Boolean, default=False)
    access = Column(Boolean, default=True)
    two_factor_auth_token = Column(String(32), nullable=True)
    time_zone_id = Column(Integer, ForeignKey('time_zones.id'), nullable=False)
    
    preferred_fiat_currency = relationship("FiatCurrency", foreign_keys=[preferred_fiat_currency_id])
    crypto_currency = relationship("CryptoCurrency", back_populates="traders")
    time_zone = relationship("TimeZone", back_populates="traders")
    trader_commissions = relationship("TraderCommission", back_populates="trader", cascade="all, delete-orphan")
    trader_addresses = relationship("TraderAddress", back_populates="trader", cascade="all, delete-orphan")
    balance_trader_fiat_history = relationship("BalanceTraderFiatHistory", back_populates="trader", cascade="all, delete-orphan")
    balance_trader_crypto_history = relationship("BalanceTraderCryptoHistory", back_populates="trader", cascade="all, delete-orphan")
    req_traders = relationship("ReqTrader", back_populates="trader")
    order_histories = relationship("OrderHistory", back_populates="trader")

    __table_args__ = (
        Index('ix_trader_priority_lookup', 'in_work', 'trafic_priority'),
    )

class TraderCommission(Base):
    __tablename__ = "trader_commissions"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    commission_payin = Column(DECIMAL(20, 2), nullable=False)
    commission_payout = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="trader_commissions")

class TraderAddress(Base):
    __tablename__ = "trader_addresses"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    address = Column(String(255), nullable=False)
    fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    status = Column(String(50), nullable=False, default="check", index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="trader_addresses")
    fiat_currency = relationship("FiatCurrency", back_populates="trader_addresses")

class BalanceTrader(Base):
    __tablename__ = "balance_traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)

    trader = relationship("Trader", back_populates="balance_traders")
    fiat_currency = relationship("FiatCurrency", back_populates="balance_traders")

class BalanceTraderFiatHistory(Base):
    __tablename__ = "balance_trader_fiat_history"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    operation_type = Column(String(50), nullable=False, index=True)
    network = Column(String(50), nullable=True)
    amount = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="balance_trader_fiat_history")
    fiat = relationship("FiatCurrency", foreign_keys=[fiat_id])

class BalanceTraderCryptoHistory(Base):
    __tablename__ = "balance_trader_crypto_history"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    operation_type = Column(String(50), nullable=False, index=True)
    network = Column(String(50), nullable=False)
    amount = Column(DECIMAL(20, 8), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="balance_trader_crypto_history")
    crypto_currency = relationship("CryptoCurrency", back_populates="trader_balance_history")

class ReqTrader(Base):
    __tablename__ = "req_traders"
    id = Column(Integer, primary_key=True, index=True)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False, index=True)
    owner_of_requisites_id = Column(Integer, ForeignKey('owner_of_requisites.id'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)
    req_number = Column(String, nullable=False)
    status = Column(String(50), default="approve", index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    fiat = relationship("FiatCurrency")
    trader = relationship("Trader", back_populates="req_traders")
    owner_of_requisites = relationship("OwnerOfRequisites", back_populates="requisites")
    method = relationship("PaymentMethod", back_populates="req_traders")
    bank = relationship("BanksTrader", back_populates="req_traders")

    order_histories = relationship("OrderHistory", back_populates="requisite")
    full_requisites_settings = relationship("FullRequisitesSettings", back_populates="requisite", uselist=False, cascade="all, delete-orphan")

class OwnerOfRequisites(Base):
    __tablename__ = "owner_of_requisites"
    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    requisites = relationship("ReqTrader", back_populates="owner_of_requisites")

class FullRequisitesSettings(Base):
    __tablename__ = "full_requisites_settings"
    id = Column(Integer, primary_key=True, index=True)
    requisite_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    pay_in = Column(Boolean, default=False)
    pay_out = Column(Boolean, default=False)
    lower_limit = Column(DECIMAL(20, 2), nullable=False)
    upper_limit = Column(DECIMAL(20, 2), nullable=False)
    total_limit = Column(DECIMAL(20, 2), nullable=False)
    turnover_limit_minutes = Column(Integer, nullable=False)
    turnover_day_max = Column(DECIMAL(20, 2), nullable=False) 
    requisite = relationship("ReqTrader", back_populates="full_requisites_settings")

class OrderHistory(Base):
    __tablename__ = "order_history"
    id = Column(Integer, primary_key=True, index=True)
    incoming_order_id = Column(Integer, ForeignKey('incoming_orders.id'), nullable=True, unique=True)
    hash_id = Column(String(255), nullable=False, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False, index=True)
    requisite_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False, index=True)
    gateway_id = Column(Integer, ForeignKey('store_gateways.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False, index=True)
    method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    order_type = Column(String(50), nullable=False, index=True)
    exchange_rate = Column(DECIMAL(20, 8), nullable=False)
    amount_currency = Column(DECIMAL(20, 8), nullable=False)
    total_fiat = Column(DECIMAL(20, 2), nullable=False)
    store_commission = Column(DECIMAL(20, 2), nullable=False)
    trader_commission = Column(DECIMAL(20, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending', index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    incoming_order = relationship("IncomingOrder", back_populates="assigned_order")
    trader = relationship("Trader", back_populates="order_histories")
    merchant = relationship("Merchant", back_populates="order_histories")
    store = relationship("MerchantStore", back_populates="order_histories")
    gateway = relationship("StoreGateway", back_populates="order_histories")
    requisite = relationship("ReqTrader", back_populates="order_histories")
    method = relationship("PaymentMethod", back_populates="order_histories")
    bank = relationship("BanksTrader", back_populates="order_histories")
    crypto_currency = relationship("CryptoCurrency")
    fiat = relationship("FiatCurrency", foreign_keys=[fiat_id])

class IncomingOrder(Base):
    __tablename__ = "incoming_orders"

    id = Column(Integer, primary_key=True, index=True)

    # --- Request Details ---
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    gateway_id = Column(Integer, ForeignKey('store_gateways.id'), nullable=True)
    target_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=True)
    target_bank_id = Column(Integer, ForeignKey('banks.id'), nullable=True)

    # --- Currency, Amount, Rate and Commission ---
    fiat_currency_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    crypto_currency_id = Column(Integer, ForeignKey('crypto_currencies.id'), nullable=False)
    total_fiat = Column(DECIMAL(20, 2), nullable=False)
    amount_currency = Column(DECIMAL(20, 8), nullable=False)
    exchange_rate = Column(DECIMAL(20, 8), nullable=False)
    store_commission = Column(DECIMAL(20, 2), nullable=False)
    order_type = Column(String(50), nullable=False, index=True) # 'pay_in', 'pay_out'

    # --- Processing State ---
    status = Column(String(50), default='new', nullable=False, index=True) # new, processing, assigned, failed, retrying
    retry_count = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(TIMESTAMP(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # --- Assignment Link ---
    assigned_order = relationship("OrderHistory", back_populates="incoming_order", uselist=False) # Added uselist=False for one-to-one

    # --- Timestamps ---
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # --- Relationships (Define explicitly if needed for direct access) ---
    merchant = relationship("Merchant")
    store = relationship("MerchantStore")
    gateway = relationship("StoreGateway")
    fiat_currency = relationship("FiatCurrency")
    crypto_currency = relationship("CryptoCurrency")
    target_method = relationship("PaymentMethod")
    target_bank = relationship("BanksTrader")

    # --- Indexes (using __table_args__) ---
    __table_args__ = (
        Index('ix_incoming_orders_status_created', status, created_at),
        # Add other indexes if needed, e.g., on merchant_id, store_id
        Index('ix_incoming_orders_merchant_store', merchant_id, store_id),
    )

# =====================
# === ПОДДЕРЖКА и АДМИНЫ (Support & Admins)
# =====================
class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    super_admin = Column(Boolean, default=False)
    access = Column(Boolean, default=True)
    two_fa_code = Column(String(32), nullable=True)

class Support(Base):
    __tablename__ = "supports"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    access_to = Column(Text, nullable=False)
    access = Column(Boolean, default=True)
    two_fa_code = Column(String(32), nullable=True)

# =====================
# === ОБЩИЕ/СПРАВОЧНИКИ (Common/Reference)
# =====================
class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(10), nullable=False)
    fiat = Column(String(10), nullable=False)
    buy_rate = Column(DECIMAL(20, 8), nullable=False)
    sell_rate = Column(DECIMAL(20, 8), nullable=False)
    median_rate = Column(DECIMAL(20, 8), nullable=False)
    source = Column(String(255), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class BanksTrader(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, index=True)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    bank_name = Column(String(100), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    interbank = Column(Boolean, default=False, nullable=False)
    access = Column(Boolean, default=True)

    req_traders = relationship("ReqTrader", back_populates="bank")
    order_histories = relationship("OrderHistory", back_populates="bank")
    avalible_bank_methods = relationship("AvalibleBankMethod", back_populates="bank")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    method_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)

    req_traders = relationship("ReqTrader", back_populates="method")
    order_histories = relationship("OrderHistory", back_populates="method")
    avalible_bank_methods = relationship("AvalibleBankMethod", back_populates="method")

class AvalibleBankMethod(Base):
    __tablename__ = "avalible_bank_methods"
    id = Column(Integer, primary_key=True, index=True)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    access = Column(Boolean, default=True)

    bank = relationship("BanksTrader", back_populates="avalible_bank_methods")
    method = relationship("PaymentMethod", back_populates="avalible_bank_methods")
    fiat = relationship("FiatCurrency")

class FiatCurrency(Base):
    __tablename__ = "fiat_currencies"
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    currency_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)
    
    traders_preferred = relationship("Trader", foreign_keys="[Trader.preferred_fiat_currency_id]", back_populates="preferred_fiat_currency")
    trader_addresses = relationship("TraderAddress", back_populates="fiat_currency")
    balance_trader_fiat_history = relationship("BalanceTraderFiatHistory", foreign_keys="[BalanceTraderFiatHistory.fiat_id]", back_populates="fiat")
    balance_traders = relationship("BalanceTrader", back_populates="fiat_currency")
    store_addresses = relationship("StoreAddress", back_populates="fiat_currency")
    merchant_stores = relationship("MerchantStore", back_populates="fiat_currency")
    
    country = relationship("Country", back_populates="fiat_currencies")

class CryptoCurrency(Base):
    __tablename__ = "crypto_currencies"
    id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)
    
    merchant_stores = relationship("MerchantStore", back_populates="crypto_currency")
    balance_stores = relationship("BalanceStore", back_populates="crypto_currency")
    balance_store_history = relationship("BalanceStoreHistory", back_populates="crypto_currency")
    trader_balance_history = relationship("BalanceTraderCryptoHistory", back_populates="crypto_currency")
    traders = relationship("Trader", back_populates="crypto_currency")

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)
    
    fiat_currencies = relationship("FiatCurrency", back_populates="country")

class TimeZone(Base):
    __tablename__ = "time_zones"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # e.g., "Europe/Moscow"
    display_name = Column(String(100), nullable=False)  # e.g., "(UTC+03:00) Moscow"
    utc_offset = Column(Integer, nullable=False)  # Offset in minutes
    access = Column(Boolean, default=True)
    regions = Column(String(), nullable=True)
    traders = relationship("Trader", back_populates="time_zone")
    def __repr__(self):
        return f"<TimeZone(name='{self.name}', display_name='{self.display_name}')>"

# Add indexes for foreign keys and common filter columns
Index('ix_order_history_created_at', OrderHistory.created_at)
Index('ix_req_trader_status', ReqTrader.status)
Index('ix_trader_address_status', TraderAddress.status)
Index('ix_store_address_status', StoreAddress.status)
Index('ix_balance_trader_fiat_history_op_type', BalanceTraderFiatHistory.operation_type)
Index('ix_balance_trader_crypto_history_op_type', BalanceTraderCryptoHistory.operation_type)
    
    