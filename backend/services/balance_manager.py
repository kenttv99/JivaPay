"""Service for managing balances and commissions."""

import logging
from decimal import Decimal
from typing import Tuple, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions
from backend.database.utils_async import atomic_transaction_async, create_object_async, get_entity_by_id_async, get_object_or_none_async
from backend.database.db import (
    OrderHistory, MerchantStore, Trader,
    StoreCommission, TraderCommission,
    BalanceStore, BalanceTrader,
    BalanceStoreHistory, BalanceTraderFiatHistory, BalanceTraderCryptoHistory,
    IncomingOrder, CryptoCurrency, FiatCurrency
)
from backend.utils.exceptions import (
    ConfigurationError, InsufficientBalance, DatabaseError, OrderProcessingError
)

# Добавляем импорт декоратора и определяем SERVICE_NAME
logger = get_logger(__name__)
SERVICE_NAME = "balance_manager"

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
async def calculate_commissions_async(
    order_like: Union[IncomingOrder, OrderHistory], # Explicitly Union for type safety
    db_session: AsyncSession,
    trader_id: Optional[int] = None,
) -> Tuple[Decimal, Decimal]:
    """Calculates store and trader commissions for a given order-like object asynchronously."""
    
    store_id_val: int
    trader_id_val: int
    order_type: str
    base_amount_fiat: Optional[Decimal]
    base_amount_crypto: Optional[Decimal]

    if isinstance(order_like, OrderHistory):
        store_id_val = order_like.store_id
        trader_id_val = order_like.trader_id
        order_type = order_like.order_type
        base_amount_fiat = getattr(order_like, "total_fiat", None)
        base_amount_crypto = getattr(order_like, "amount_crypto", None) # OrderHistory might use amount_crypto or amount_currency
    elif isinstance(order_like, IncomingOrder):
        if trader_id is None:
            # This check should ideally happen before calling this if trader_id is from requisite selection
            logger.error("calculate_commissions_async called for IncomingOrder without trader_id.")
            raise ConfigurationError("trader_id must be provided for IncomingOrder when calculating commissions.")
        store_id_val = order_like.store_id
        trader_id_val = trader_id
        order_type = order_like.order_type
        base_amount_fiat = getattr(order_like, "amount_fiat", None)
        base_amount_crypto = getattr(order_like, "amount_crypto", None)
    else:
        logger.error(f"Unsupported order_like type: {type(order_like)} in calculate_commissions_async")
        raise TypeError(f"Unsupported order_like type: {type(order_like)}. Expected IncomingOrder or OrderHistory.")

    if store_id_val is None or trader_id_val is None:
         # This case should be prevented by checks above or input validation
        logger.error(f"store_id ({store_id_val}) or trader_id ({trader_id_val}) is None before fetching commission settings.")
        raise ConfigurationError("store_id or trader_id is missing for commission calculation.")

    # Fetch current commission settings asynchronously
    stmt_store_setting = (
        select(StoreCommission)
        .filter_by(store_id=store_id_val)
        .order_by(StoreCommission.updated_at.desc())
        .limit(1)
    )
    result_store = await db_session.execute(stmt_store_setting)
    store_setting = result_store.scalars().first()

    stmt_trader_setting = (
        select(TraderCommission)
        .filter_by(trader_id=trader_id_val)
        .order_by(TraderCommission.updated_at.desc())
        .limit(1)
    )
    result_trader = await db_session.execute(stmt_trader_setting)
    trader_setting = result_trader.scalars().first()

    if not store_setting or not trader_setting:
        logger.error(f"Commission settings missing for store {store_id_val} or trader {trader_id_val}")
        raise ConfigurationError(f"Commission settings not found for store {store_id_val} or trader {trader_id_val}.")

    base_amount: Decimal
    store_rate: Decimal
    trader_rate: Decimal

    if order_type.lower() == 'pay_in': # Ensure case-insensitivity for order_type comparison
        base_amount = base_amount_fiat if base_amount_fiat is not None else Decimal('0')
        store_rate = store_setting.commission_payin
        trader_rate = trader_setting.commission_payin
    elif order_type.lower() == 'pay_out':
        base_amount = base_amount_crypto if base_amount_crypto is not None else Decimal('0')
        store_rate = store_setting.commission_payout
        trader_rate = trader_setting.commission_payout
    else:
        logger.error(f"Unknown order_type: {order_type} for commission calculation.")
        raise ConfigurationError(f"Unknown order_type: {order_type} for commission calculation.")

    store_commission = (base_amount * store_rate) / Decimal('100')
    trader_commission = (base_amount * trader_rate) / Decimal('100')
    
    logger.debug(
        f"Calculated commissions async: store_comm={store_commission}, trader_comm={trader_commission} for order_type={order_type}"
    )
    return store_commission, trader_commission

# Keep existing synchronous version if it's still used elsewhere (e.g., by Celery tasks or older code)
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
            if order.order_type == 'pay_in': # Магазин получает крипту
                net_store_change = order.amount_crypto if order.amount_crypto is not None else Decimal('0')
            elif order.order_type == 'pay_out': # Магазин отдает крипту
                net_store_change = -(order.amount_crypto if order.amount_crypto is not None else Decimal('0'))
            else:
                # Log error and raise exception for unknown order type
                logger.error(f"Unknown order type '{order.order_type}' for Order ID {order.id} during balance update.")
                raise OrderProcessingError(f"Unknown order type '{order.order_type}' for order {order.id}")

            net_trader_change = trader_comm # Комиссия трейдера всегда начисляется (предполагается, что она положительная)
            
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

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
async def update_balances_for_completed_order_async(order_id: int, db_session: AsyncSession):
    """Updates store and trader balances and records history for a completed order asynchronously."""
    async with atomic_transaction_async(db_session):
        order = await get_entity_by_id_async(db_session, OrderHistory, order_id)
        if not order:
            raise OrderProcessingError(f"OrderHistory not found: {order_id}")
        if order.status != 'completed':
            raise OrderProcessingError(f"Order {order_id} is not completed: {order.status}")
        
        # Lock or get/create BalanceStore
        store_balance = await get_object_or_none_async(
            db_session, 
            BalanceStore, 
            store_id=order.store_id, 
            crypto_currency_id=order.crypto_currency_id
        )
        if store_balance:
            # Lock the existing balance row. Important to do this before creating if not found.
            # Re-fetch with lock. This is one way; another is to try create and catch integrity error then lock+fetch.
            # For simplicity, let's assume get_object_or_none_async doesn't lock, so we fetch again with lock.
            stmt_lock_store_balance = select(BalanceStore).filter_by(id=store_balance.id).with_for_update()
            await db_session.execute(stmt_lock_store_balance) # Execute to apply lock
            await db_session.refresh(store_balance) # Refresh to get latest state if needed after lock
        else:
            logger.info(f"BalanceStore not found for store {order.store_id}, crypto {order.crypto_currency_id}. Creating new one.")
            store_balance = await create_object_async(
                db_session, 
                BalanceStore, 
                {
                    "store_id": order.store_id,
                    "crypto_currency_id": order.crypto_currency_id,
                    "balance": Decimal("0.0")
                }
            )
            # Newly created object is already in session, no explicit lock needed in the same way as existing.

        trader_fiat_currency_id_for_balance = order.fiat_id
        # Lock or get/create BalanceTrader
        trader_balance = await get_object_or_none_async(
            db_session, 
            BalanceTrader, 
            trader_id=order.trader_id, 
            fiat_currency_id=trader_fiat_currency_id_for_balance
        )
        if trader_balance:
            stmt_lock_trader_balance = select(BalanceTrader).filter_by(id=trader_balance.id).with_for_update()
            await db_session.execute(stmt_lock_trader_balance)
            await db_session.refresh(trader_balance)
        else:
            logger.info(f"BalanceTrader not found for trader {order.trader_id}, fiat {trader_fiat_currency_id_for_balance}. Creating new one.")
            trader_balance = await create_object_async(
                db_session, 
                BalanceTrader, 
                {
                    "trader_id": order.trader_id,
                    "fiat_currency_id": trader_fiat_currency_id_for_balance,
                    "balance": Decimal("0.0")
                }
            )

        store_comm, trader_comm = await calculate_commissions_async(order, db_session)
        
        net_store_change: Decimal
        if order.order_type.lower() == 'pay_in':
            net_store_change = order.amount_currency if order.amount_currency is not None else Decimal('0')
        elif order.order_type.lower() == 'pay_out':
            net_store_change = -(order.amount_currency if order.amount_currency is not None else Decimal('0'))
        else:
            logger.error(f"Unknown order type '{order.order_type}' for Order ID {order.id}")
            raise OrderProcessingError(f"Unknown order type '{order.order_type}' for order {order.id}")

        net_trader_change = trader_comm
        
        if store_balance.balance + net_store_change < 0:
            raise InsufficientBalance(f"Store balance would go negative. Store: {order.store_id}", account_id=order.store_id)
        store_balance.balance += net_store_change
        
        if trader_balance.balance + net_trader_change < 0:
            raise InsufficientBalance(f"Trader balance would go negative. Trader: {order.trader_id}", account_id=order.trader_id)
        trader_balance.balance += net_trader_change
        
        # db_session.add(store_balance) and db_session.add(trader_balance) are implicit if objects were modified or newly created & added by create_object_async

        await create_object_async(db_session, BalanceStoreHistory, {
            "store_id": store_balance.store_id,
            "crypto_currency_id": store_balance.crypto_currency_id,
            "order_id": order.id,
            "balance_change": net_store_change,
            "new_balance": store_balance.balance,
            "operation_type": "order_completed",
            "description": f"Order {order.id} completed ({order.order_type})"
        })
        await create_object_async(db_session, BalanceTraderFiatHistory, {
            "trader_id": trader_balance.trader_id,
            "fiat_id": trader_fiat_currency_id_for_balance,
            "order_id": order.id,
            "operation_type": "commission",
            "network": None,
            "balance_change": net_trader_change,
            "new_balance": trader_balance.balance,
            "description": f"Commission for order {order.id} ({order.order_type})"
        })
    logger.info(f"Async balances updated for Order ID: {order.id if order else order_id}")

# ... (synchronous calculate_commissions and old update_balances_for_completed_order remain for now) ... 