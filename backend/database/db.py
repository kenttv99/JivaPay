from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

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
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    two_factor_auth_token = Column(String(32), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    access = Column(Boolean, default=True)

class MerchantStore(Base):
    __tablename__ = "merchant_stores"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_name = Column(String(255), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)
    public_api_key = Column(String(255), nullable=False)
    private_api_key = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    trafic_access = Column(Boolean, default=False)
    access = Column(Boolean, default=True)

class StoreGateway(Base):
    __tablename__ = "store_gateways"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(50), nullable=False) #redirect, api

class BalanceStore(Base):
    __tablename__ = "balance_stores"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class StoreAddress(Base):
    __tablename__ = "store_addresses"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    address = Column(String(255), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False, default="check")
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

# =====================
# === ТРЕЙДЕРЫ (Traders)
# =====================
class Trader(Base):
    __tablename__ = "traders"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
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
    time_zone_id = Column(Integer, ForeignKey('time_zones.id', ondelete='CASCADE'), nullable=False)

class TraderAddress(Base):
    __tablename__ = "trader_addresses"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    address = Column(String(255), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False, default="check")
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class BalanceTrader(Base):
    __tablename__ = "balance_traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)

class BalansHistoryTrader(Base):
    __tablename__ = "balans_history_traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    operation_type = Column(String(50), nullable=False)
    network = Column(String(50), nullable=False)
    commission = Column(DECIMAL(20, 2), nullable=False)
    amount = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class ReqTrader(Base):
    __tablename__ = "req_traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    req_number = Column(String, nullable=False)
    fio = Column(String, nullable=False)
    status = Column(String(50), default="approve")
    lower_limit = Column(DECIMAL(20, 2), nullable=False)
    upper_limit = Column(DECIMAL(20, 2), nullable=False)
    total_limit = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class OrderHistory(Base):
    __tablename__ = "order_history"
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String(255), nullable=False)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    requeset_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    order_type = Column(String(50), nullable=False)
    amount_currency = Column(DECIMAL(20, 8), nullable=False)
    total_fiat = Column(DECIMAL(20, 2), nullable=False)
    merchant_commission = Column(DECIMAL(20, 2), nullable=False)
    trader_commission = Column(DECIMAL(20, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class WorkBalansHistory(Base):
    __tablename__ = "work_balans_history"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    exchange_rate = Column(DECIMAL(20, 8), nullable=False)
    operation_type = Column(String(50), nullable=False)
    amount_currency = Column(DECIMAL(20, 8), nullable=False)
    amount_fiat = Column(DECIMAL(20, 2), nullable=False)
    commission = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

class AvalibleRequesets(Base):
    __tablename__ = "avalible_requests"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    upper_limit = Column(DECIMAL(20, 2), nullable=False)
    lower_limit = Column(DECIMAL(20, 2), nullable=False)
    total_limit = Column(DECIMAL(20, 2), nullable=False)

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
    bank_name = Column(String(100), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    interbank = Column(Boolean, default=False, nullable=False)
    access = Column(Boolean, default=True)

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    method_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)

class AvalibleBankMethod(Base):
    __tablename__ = "avalible_bank_methods"
    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    access = Column(Boolean, default=True)

class FiatCurrency(Base):
    __tablename__ = "fiat_currencies"
    id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)

class TimeZone(Base):
    __tablename__ = "time_zones"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # e.g., "Europe/Moscow"
    display_name = Column(String(100), nullable=False)  # e.g., "(UTC+03:00) Moscow"
    utc_offset = Column(Integer, nullable=False)  # Offset in minutes
    access = Column(Boolean, default=True)
    regions = Column(String(), nullable=True)
    def __repr__(self):
        return f"<TimeZone(name='{self.name}', display_name='{self.display_name}')>"
    
    