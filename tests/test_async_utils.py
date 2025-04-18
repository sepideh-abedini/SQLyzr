"""
Unit tests for the async_utils module.

This module contains tests for the utility functions in src.util.async_utils:
- partition_list: Tests for splitting lists into chunks
- apply_async: Tests for applying an async function to a list of items with concurrency control

To run these tests:
    pytest tests/test_async_utils.py -v
"""

import asyncio
import os
import pytest

from src.util.async_utils import partition_list, apply_async, MAX_THREADS


def test_partition_list_default_size():
    """Test partition_list with default size (MAX_THREADS)."""
    test_list = list(range(10))
    result = partition_list(test_list)

    # Check that the list is partitioned correctly
    assert len(result) == (len(test_list) + MAX_THREADS - 1) // MAX_THREADS

    # Check that all elements are preserved
    flattened = [item for sublist in result for item in sublist]
    assert flattened == test_list


def test_partition_list_custom_size():
    """Test partition_list with a custom size."""
    test_list = list(range(10))
    size = 3
    result = partition_list(test_list, size)

    # Check that the list is partitioned correctly
    assert len(result) == (len(test_list) + size - 1) // size
    assert result == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    # Check that all elements are preserved
    flattened = [item for sublist in result for item in sublist]
    assert flattened == test_list


def test_partition_list_empty():
    """Test partition_list with an empty list."""
    test_list = []
    result = partition_list(test_list)
    assert result == []


def test_partition_list_size_larger_than_list():
    """Test partition_list when size is larger than the list."""
    test_list = [1, 2, 3]
    size = 10
    result = partition_list(test_list, size)
    assert result == [test_list]


@pytest.mark.asyncio
async def test_apply_async_basic():
    """Test apply_async with a simple async function."""
    async def double(x):
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return x * 2

    test_list = [1, 2, 3, 4, 5]
    result = await apply_async(double, test_list)
    assert result == [2, 4, 6, 8, 10]


@pytest.mark.asyncio
async def test_apply_async_empty_list():
    """Test apply_async with an empty list."""
    async def double(x):
        await asyncio.sleep(0.01)
        return x * 2

    test_list = []
    result = await apply_async(double, test_list)
    assert result == []


@pytest.mark.asyncio
async def test_apply_async_error_handling():
    """Test apply_async with a function that raises an exception."""
    async def maybe_raise(x):
        await asyncio.sleep(0.01)
        if x == 3:
            raise ValueError("Error for item 3")
        return x * 2

    test_list = [1, 2, 3, 4, 5]

    # The function should propagate exceptions
    with pytest.raises(ValueError, match="Error for item 3"):
        await apply_async(maybe_raise, test_list)


@pytest.mark.asyncio
async def test_apply_async_timeout_handling():
    """Test apply_async with a function that raises TimeoutError."""
    async def timeout_function(x):
        if x == 3:
            # Simulate a timeout by raising the exception directly
            raise asyncio.TimeoutError("Simulated timeout")
        await asyncio.sleep(0.01)
        return x * 2

    test_list = [1, 2, 3, 4, 5]
    result = await apply_async(timeout_function, test_list)

    # Check that non-timeout results are correct
    assert result[0] == 2
    assert result[1] == 4
    assert isinstance(result[2], asyncio.TimeoutError)
    assert result[3] == 8
    assert result[4] == 10
