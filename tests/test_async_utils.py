import asyncio

import pytest

from src.util.async_utils import apply_async


@pytest.mark.asyncio(scope="session")
async def test_apply_async_basic():
    """Test apply_async with a simple async function."""

    async def double(x):
        await asyncio.sleep(0.01)
        return x * 2

    test_list = [1, 2, 3, 4, 5]
    result = await apply_async(double, test_list)
    assert result == [2, 4, 6, 8, 10]


@pytest.mark.asyncio(scope="session")
async def test_apply_async_empty_list():
    """Test apply_async with an empty list."""

    async def double(x):
        await asyncio.sleep(0.01)
        return x * 2

    test_list = []
    result = await apply_async(double, test_list)
    assert result == []


@pytest.mark.asyncio(scope="session")
async def test_apply_async_error_handling():
    """Test apply_async with a function that raises an exception."""

    async def maybe_raise(x):
        await asyncio.sleep(0.01)
        if x == 3:
            raise ValueError("Error for item 3")
        return x * 2

    test_list = [1, 2, 3, 4, 5]

    with pytest.raises(ValueError, match="Error for item 3"):
        await apply_async(maybe_raise, test_list)


@pytest.mark.asyncio(scope="session")
async def test_apply_async_timeout_handling():
    """Test apply_async with a function that raises TimeoutError."""

    async def timeout_function(x):
        if x == 3:
            raise asyncio.TimeoutError("Simulated timeout")
        await asyncio.sleep(0.01)
        return x * 2

    test_list = [1, 2, 3, 4, 5]
    with pytest.raises(asyncio.TimeoutError, match="Simulated timeout"):
        await apply_async(timeout_function, test_list)
