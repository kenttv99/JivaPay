from typing import List, Any, Optional, Type
from sqlalchemy import and_, or_

# Предполагается, что модели импортируются там, где эти фильтры используются,
# либо их нужно импортировать здесь, если они будут использоваться напрямую.
# Например:
# from backend.database.db import Trader, ReqTrader, User, FullRequisitesSettings

# Импортируем необходимые модели
from backend.database.db import User, Trader, ReqTrader # FullRequisitesSettings - пока не используется напрямую в общем фильтре

def get_active_trader_filters(user_alias: Optional[Type[User]] = None) -> List[Any]:
    """Возвращает список SQLAlchemy фильтров для активных трейдеров.
    
    Args:
        user_alias: Опциональный алиас для модели User, если он уже присоединен к запросу.
                    Если предоставлен, будет добавлен фильтр user_alias.is_active == True.
    """
    filters = [
        Trader.in_work == True,
        Trader.is_traffic_enabled_by_teamlead == True,
    ]
    if user_alias:
        filters.append(user_alias.is_active == True)
    return filters

def get_active_requisite_filters() -> List[Any]:
    """Возвращает список SQLAlchemy фильтров для активных реквизитов."""
    # Активный реквизит: статус 'approve' и не исключен из дистрибуции.
    # Также подразумевается, что связанный трейдер активен (это должно быть обеспечено в запросе,
    # который использует этот фильтр, путем объединения с фильтрами get_active_trader_filters).
    return [
        ReqTrader.status == 'approve',
        ReqTrader.is_excluded_from_distribution == False,
        # Условия на FullRequisitesSettings (например, pay_in == True) могут быть добавлены здесь
        # или в более специфических функциях фильтрации, если это необходимо.
        # Например, если бы нам нужен был фильтр "активные реквизиты для pay_in":
        # ReqTrader.full_requisites_settings.has(FullRequisitesSettings.pay_in == True)
        # Это потребует импорта FullRequisitesSettings и проверки на None для full_requisites_settings.
    ]

# Пример, как можно было бы сделать фильтр трейдера, если User всегда присоединяется:
# def get_active_trader_filters_with_user_join_assumed() -> List[Any]:
#     """
#     Возвращает фильтры для активных трейдеров, предполагая, что Trader.user уже доступен в запросе.
#     ВАЖНО: Вызывающий код должен обеспечить, что User присоединен к Trader (например, query(Trader).join(User))
#     """
#     return [
#         Trader.in_work == True,
#         Trader.is_traffic_enabled_by_teamlead == True,
#         User.is_active == True, # Это корректно, если Trader.user это User
#     ]

# Если мы хотим, чтобы фильтр сам позаботился о join (более сложный и может быть менее эффективным):
# def get_active_trader_filters_handling_join() -> List[Any]:
#     # Это потребует чтобы фильтр применялся к Query объекту, а не просто возвращал список условий
#     # или использовал exists() или subquery, что выходит за рамки простого списка фильтров.
#     # Для простоты, оставим задачу join на вызывающий код.
#     pass 