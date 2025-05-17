"""
Service for platform-related data aggregation.
"""
from typing import List, Dict, Union
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.db import BalancePlatform, CryptoCurrency
# Assuming Pydantic schema for response if needed
# from backend.schemas_enums.platform import PlatformBalanceItemSchema

class PlatformService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_platform_balances(self) -> List[Dict[str, Union[str, Decimal]]]:
        """
        Aggregates and returns the current platform balances per currency.

        Returns:
            A list of dictionaries, where each dictionary contains:
                - "currency_code": The code of the cryptocurrency (e.g., "BTC").
                - "currency_name": The name of the cryptocurrency (e.g., "Bitcoin").
                - "total_balance": The total balance for that currency.
        """
        balances_query = (
            self.db.query(
                CryptoCurrency.currency_code,
                CryptoCurrency.currency_name,
                func.sum(BalancePlatform.balance).label("total_balance")
            )
            .join(BalancePlatform, BalancePlatform.crypto_currency_id == CryptoCurrency.id)
            .group_by(CryptoCurrency.id, CryptoCurrency.currency_code, CryptoCurrency.currency_name)
            .all()
        )

        result: List[Dict[str, Union[str, Decimal]]] = []
        for row in balances_query:
            result.append({
                "currency_code": row.currency_code,
                "currency_name": row.currency_name,
                "total_balance": row.total_balance if row.total_balance is not None else Decimal("0.0")
            })
        
        return result

# Example Usage (conceptual)
if __name__ == '__main__':
    # This block is for conceptual illustration.
    # Requires a mock DB session and data to be testable.
    class MockCryptoCurrency:
        def __init__(self, id, code, name):
            self.id = id
            self.currency_code = code
            self.currency_name = name

    class MockBalancePlatform:
        def __init__(self, crypto_currency_id, balance):
            self.crypto_currency_id = crypto_currency_id
            self.balance = balance

    class MockQuery:
        def __init__(self, data):
            self._data = data
        def join(self, *args, **kwargs): return self
        def group_by(self, *args, **kwargs): return self
        def all(self): return self._data
        def label(self, name): return self # Simplified for this mock

    class MockDBSession:
        def query(self, *args):
            # Simulate query result for platform balances
            # This is highly simplified for demonstration.
            # A real test would involve setting up mock SQLAlchemy objects and query results.
            if CryptoCurrency.currency_code in args and BalancePlatform.balance in args: # very rough check
                return MockQuery([
                    type('Row', (), {'currency_code': 'BTC', 'currency_name': 'Bitcoin', 'total_balance': Decimal('10.5')})(),
                    type('Row', (), {'currency_code': 'ETH', 'currency_name': 'Ethereum', 'total_balance': Decimal('100.2')})()
                ])
            return MockQuery([])
    
    mock_db = MockDBSession()
    platform_service = PlatformService(db_session=mock_db)
    balances = platform_service.get_platform_balances()
    print("Platform Balances:", balances)
    # Expected: Platform Balances: [{'currency_code': 'BTC', 'currency_name': 'Bitcoin', 'total_balance': Decimal('10.5')}, ...] 