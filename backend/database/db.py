from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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

    stores = relationship("MerchantStore", back_populates="merchant", cascade="all, delete-orphan")
    order_histories = relationship("OrderHistory", back_populates="merchant")
    store_addresses = relationship("StoreAddress", back_populates="merchant")

class MerchantStore(Base):
    __tablename__ = "merchant_stores"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    store_name = Column(String(255), nullable=False)
    currency_id = Column(Integer, ForeignKey('crypto_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)
    public_api_key = Column(String(255), nullable=False)
    private_api_key = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    trafic_access = Column(Boolean, default=False)
    access = Column(Boolean, default=True)
    
    merchant = relationship("Merchant", back_populates="stores")
    store_commissions = relationship("StoreCommission", back_populates="store")
    store_gateways = relationship("StoreGateway", back_populates="store")
    balance_stores = relationship("BalanceStore", back_populates="store")
    balance_store_history = relationship("BalanceStoreHistory", back_populates="store")
    store_addresses = relationship("StoreAddress", back_populates="store")
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
    currency_id = Column(Integer, ForeignKey('crypto_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    
    store = relationship("MerchantStore", back_populates="balance_stores")
    currency = relationship("CryptoCurrency")

class BalanceStoreHistory(Base):
    __tablename__ = "balance_store_history"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('crypto_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    store = relationship("MerchantStore", back_populates="balance_store_history")
    currency = relationship("CryptoCurrency")

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

    store = relationship("MerchantStore", back_populates="store_addresses")
    merchant = relationship("Merchant", back_populates="store_addresses")
    currency = relationship("FiatCurrency")

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
    
    trader_commissions = relationship("TraderCommission", back_populates="trader")
    trader_addresses = relationship("TraderAddress", back_populates="trader")
    balance_traders = relationship("BalanceTrader", back_populates="trader")
    balans_trader_history = relationship("BalansTraderHistory", back_populates="trader")
    req_traders = relationship("ReqTrader", back_populates="trader")
    order_histories = relationship("OrderHistory", back_populates="trader")

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
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False, default="check")
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="trader_addresses")
    currency = relationship("FiatCurrency")

class BalanceTrader(Base):
    __tablename__ = "balance_traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    balance = Column(DECIMAL(20, 2), nullable=False)

    trader = relationship("Trader", back_populates="balance_traders")
    currency = relationship("FiatCurrency")

class BalansTraderHistory(Base):
    __tablename__ = "balans_trader_history"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    operation_type = Column(String(50), nullable=False)
    network = Column(String(50), nullable=False)
    amount = Column(DECIMAL(20, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="balans_trader_history")
    fiat = relationship("FiatCurrency", foreign_keys=[fiat_id])
    currency = relationship("FiatCurrency", foreign_keys=[currency_id])

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

    trader = relationship("Trader", back_populates="req_traders")
    method = relationship("PaymentMethod")
    bank = relationship("BanksTrader")
    avalible_requisites = relationship("AvalibleRequisites", back_populates="requisite")
    order_histories = relationship("OrderHistory", back_populates="requisite")

class OrderHistory(Base):
    __tablename__ = "order_history"
    id = Column(Integer, primary_key=True, index=True)
    hash_id = Column(String(255), nullable=False)
    trader_id = Column(Integer, ForeignKey('traders.id', ondelete='CASCADE'), nullable=False)
    merchant_id = Column(Integer, ForeignKey('merchants.id', ondelete='CASCADE'), nullable=False)
    gateway_id = Column(Integer, ForeignKey('store_gateways.id', ondelete='CASCADE'), nullable=False)
    store_id = Column(Integer, ForeignKey('merchant_stores.id', ondelete='CASCADE'), nullable=False)
    requisite_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    order_type = Column(String(50), nullable=False)
    exchange_rate = Column(DECIMAL(20, 8), nullable=False)
    amount_currency = Column(DECIMAL(20, 8), nullable=False)
    total_fiat = Column(DECIMAL(20, 2), nullable=False)
    store_commission = Column(DECIMAL(20, 2), nullable=False)
    trader_commission = Column(DECIMAL(20, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    trader = relationship("Trader", back_populates="order_histories")
    merchant = relationship("Merchant", back_populates="order_histories")
    store = relationship("MerchantStore", back_populates="order_histories")
    gateway = relationship("StoreGateway", back_populates="order_histories")
    requisite = relationship("ReqTrader", back_populates="order_histories", foreign_keys=[requisite_id])
    method = relationship("PaymentMethod", back_populates="order_histories")
    bank = relationship("BanksTrader", back_populates="order_histories")
    currency = relationship("FiatCurrency", foreign_keys=[currency_id])
    fiat = relationship("FiatCurrency", foreign_keys=[fiat_id])

class AvalibleRequisites(Base):
    __tablename__ = "avalible_requisites"
    id = Column(Integer, primary_key=True, index=True)
    requisite_id = Column(Integer, ForeignKey('req_traders.id', ondelete='CASCADE'), nullable=False)
    upper_limit = Column(DECIMAL(20, 2), nullable=False)
    lower_limit = Column(DECIMAL(20, 2), nullable=False)
    total_limit = Column(DECIMAL(20, 2), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    requisite = relationship("ReqTrader", back_populates="avalible_requisites")

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
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
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
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
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
    fiat_id = Column(Integer, ForeignKey('fiat_currencies.id', ondelete='CASCADE'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    method_id = Column(Integer, ForeignKey('payment_methods.id', ondelete='CASCADE'), nullable=False)
    access = Column(Boolean, default=True)

    bank = relationship("BanksTrader", back_populates="avalible_bank_methods")
    method = relationship("PaymentMethod", back_populates="avalible_bank_methods")
    fiat = relationship("FiatCurrency")

class FiatCurrency(Base):
    __tablename__ = "fiat_currencies"
    id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)
    
    traders = relationship("Trader", foreign_keys="[Trader.currency_id]", backref="currency")
    traders_fiat = relationship("Trader", foreign_keys="[Trader.fiat_id]", backref="fiat_currency")
    trader_addresses = relationship("TraderAddress", back_populates="currency")
    balans_trader_history_fiat = relationship("BalansTraderHistory", foreign_keys="[BalansTraderHistory.fiat_id]", backref="fiat")
    balans_trader_history_currency = relationship("BalansTraderHistory", foreign_keys="[BalansTraderHistory.currency_id]", backref="currency")
    balance_traders = relationship("BalanceTrader", back_populates="currency")
    store_addresses = relationship("StoreAddress", back_populates="currency")

class CryptoCurrency(Base):
    __tablename__ = "crypto_currencies"
    id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    access = Column(Boolean, default=True)
    
    merchant_stores = relationship("MerchantStore", backref="crypto_currency")
    balance_stores = relationship("BalanceStore", back_populates="currency")
    balance_store_history = relationship("BalanceStoreHistory", back_populates="currency")

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(50), unique=True, nullable=False)
    public_name = Column(String(255), nullable=True)
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
    
    