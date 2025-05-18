"""Service for managing balances and commissions."""

import logging
from decimal import Decimal
from typing import Tuple, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions

# Attempt to import models, DB utils, and exceptions
try:
    # !! These models need to be defined in backend/database/models.py !!
    from backend.database.db import (
        OrderHistory, MerchantStore, Trader,
        StoreCommission, TraderCommission,
        BalanceStore, BalanceTrader,
        BalanceStoreHistory, BalanceTraderFiatHistory, BalanceTraderCryptoHistory
        # Add relevant Enums if needed (e.g., BalanceHistoryType)
    )
    from backend.database.utils import get_object_or_none, create_object, atomic_transaction
    from backend.utils.exceptions import (
        ConfigurationError, InsufficientBalance, DatabaseError, OrderProcessingError
    )
except ImportError as e:
    # This service heavily depends on models, raise clearly if they are missing
    raise ImportError(f"Could not import required models or utils for BalanceManager: {e}. Ensure all required models are defined.")

# Добавляем импорт декоратора и определяем SERVICE_NAME
logger = get_logger(__name__)
SERVICE_NAME = "balance_manager"

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def calculate_commissions(
    order_like,
    db_session: Session,
    trader_id: Optional[int] = None,
) -> Tuple[Decimal, Decimal]:
    """Calculates store and trader commissions for a given order-like object.

    Args:
        order_like: Either an OrderHistory instance **or** an IncomingOrder instance.
        db_session: Active SQLAlchemy session.
        trader_id: Trader ID (required if order_like is IncomingOrder).

    Returns:
        A tuple containing (store_commission, trader_commission).

    Raises:
        ConfigurationError: If commission settings are missing or invalid.
        DatabaseError: For underlying database issues.
    """
    # logger.debug(f"Calculating commissions for order-like object: {order_like}")
    # 1. Определяем store_id и trader_id в зависимости от типа объекта
    if hasattr(order_like, "store_id") and hasattr(order_like, "trader_id"):
        # Это OrderHistory – у него уже есть trader_id
        store_id_val = order_like.store_id
        trader_id_val = order_like.trader_id
        order_type = order_like.order_type
        base_amount_fiat = getattr(order_like, "total_fiat", None)
        base_amount_crypto = getattr(order_like, "amount_crypto", None)
    else:
        # Предполагаем IncomingOrder; у него trader_id ещё нет
        if trader_id is None:
            raise ConfigurationError("trader_id must be provided when calculating commissions for IncomingOrder before OrderHistory exists.")
        store_id_val = order_like.store_id
        trader_id_val = trader_id
        order_type = order_like.order_type
        base_amount_fiat = getattr(order_like, "amount_fiat", None)
        base_amount_crypto = getattr(order_like, "amount_crypto", None)

    # 2. Загружаем актуальные настройки комиссий
    store_setting = (
        db_session.query(StoreCommission)
        .filter_by(store_id=store_id_val)
        .order_by(StoreCommission.updated_at.desc())
        .first()
    )
    trader_setting = (
        db_session.query(TraderCommission)
        .filter_by(trader_id=trader_id_val)
        .order_by(TraderCommission.updated_at.desc())
        .first()
    )
    if not store_setting or not trader_setting:
        logger.error("Commission settings missing for store %s or trader %s", store_id_val, trader_id_val)
        raise ConfigurationError("Commission settings not found for store or trader.")
    # 3. Вычисляем базовую сумму и ставки
    if order_type == 'pay_in':
        base_amount = base_amount_fiat or Decimal('0')
        store_rate = store_setting.commission_payin
        trader_rate = trader_setting.commission_payin
    else:
        base_amount = base_amount_crypto or Decimal('0')
        store_rate = store_setting.commission_payout
        trader_rate = trader_setting.commission_payout
    # Calculate commissions (percentage of base amount)
    store_commission = (base_amount * store_rate) / Decimal('100')
    trader_commission = (base_amount * trader_rate) / Decimal('100')
    logger.debug(
        "Calculated commissions: store_comm=%s, trader_comm=%s for order_type=%s",
        store_commission,
        trader_commission,
        order_type,
    )
    return store_commission, trader_commission

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def update_balances_for_completed_order(order_id: int, db_session: Session):
    """Updates store and trader balances and records history for a completed order.

    This function should typically be called within its own atomic transaction,
    potentially asynchronously after the order status is confirmed.

    Args:
        order_id: The ID of the completed OrderHistory.
        db_session: The SQLAlchemy session (ideally obtained via get_db_session for this specific task).

    Raises:
        InsufficientBalance: If a balance would go negative.
        DatabaseError: For underlying database issues or data inconsistencies.
        OrderProcessingError: If the order is not found or in an invalid state.
    """
    logger.info(f"Attempting to update balances for completed Order ID: {order_id}")

    try:
        with atomic_transaction(db_session):
            # 1. Load and validate order
            order = db_session.query(OrderHistory).filter_by(id=order_id).one_or_none()
            if not order:
                raise OrderProcessingError(f"OrderHistory not found: {order_id}")
            if order.status != 'completed':
                raise OrderProcessingError(f"Order {order_id} is not completed: {order.status}")
            # 2. Lock balances
            store_balance = (
                db_session.query(BalanceStore)
                .filter_by(store_id=order.store_id, crypto_currency_id=order.crypto_currency_id)
                .with_for_update()
                .one_or_none()
            )
            trader_balance = (
                db_session.query(BalanceTrader)
                .filter_by(trader_id=order.trader_id, fiat_currency_id=order.fiat_id)
                .with_for_update()
                .one_or_none()
            )
            if not store_balance or not trader_balance:
                raise DatabaseError("Balance record not found for store or trader.")
            # 3. Calculate commissions
            store_comm, trader_comm = calculate_commissions(order, db_session)
            # 4. Determine net balance changes
            net_store_change = order.amount_crypto or Decimal('0')
            net_trader_change = trader_comm
            # 5. Apply balance updates
            if store_balance.balance + net_store_change < 0:
                raise InsufficientBalance("Store balance would go negative.", account_id=order.store_id)
            store_balance.balance += net_store_change
            if trader_balance.balance + net_trader_change < 0:
                raise InsufficientBalance("Trader balance would go negative.", account_id=order.trader_id)
            trader_balance.balance += net_trader_change
            db_session.flush()
            # 6. Record history entries
            create_object(db_session, BalanceStoreHistory, {
                "store_id": store_balance.store_id,
                "crypto_currency_id": store_balance.crypto_currency_id,
                "order_id": order.id,
                "balance_change": net_store_change,
                "new_balance": store_balance.balance,
                "operation_type": "order_completed",
                "description": f"Order {order_id} completed"
            })
            create_object(db_session, BalanceTraderFiatHistory, {
                "trader_id": trader_balance.trader_id,
                "fiat_id": trader_balance.fiat_currency_id,
                "order_id": order.id,
                "operation_type": "commission",
                "network": None,
                "balance_change": net_trader_change,
                "new_balance": trader_balance.balance,
                "description": f"Commission for order {order_id}"
            })
        logger.info(f"Balances updated for Order ID: {order_id}")

    except (InsufficientBalance, ConfigurationError, OrderProcessingError, DatabaseError) as e:
        logger.error(f"Failed to update balances for Order ID {order_id}: {e}", exc_info=True)
        raise
    except Exception as e:
        # Catch any other unexpected error during balance update
        logger.critical(f"Unexpected critical error during balance update for Order ID {order_id}: {e}", exc_info=True)
        # Wrap in DatabaseError or a more specific critical error exception
        raise DatabaseError(f"Unexpected critical error during balance update: {e}") from e 