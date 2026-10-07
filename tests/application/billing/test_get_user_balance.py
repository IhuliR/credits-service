from components.application.use_cases.billing.get_user_balance import GetUserBalance


async def test_returns_cached_value(uow, storage, balance_cache) -> None:
    storage.balances["user-1"] = 100
    balance_cache.values["user-1"] = 70

    balance = await GetUserBalance(uow, balance_cache).execute("user-1")

    assert balance == 70


async def test_loads_from_storage_and_caches(uow, storage, balance_cache) -> None:
    storage.balances["user-1"] = 100

    balance = await GetUserBalance(uow, balance_cache).execute("user-1")

    assert balance == 100
    assert balance_cache.values["user-1"] == 100


async def test_unknown_user_has_zero_balance(uow, balance_cache) -> None:
    balance = await GetUserBalance(uow, balance_cache).execute("nobody")

    assert balance == 0
