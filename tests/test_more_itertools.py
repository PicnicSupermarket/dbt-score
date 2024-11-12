"""Tests for vendored more_itertools functions."""
from dbt_score.more_itertools import first_true


class TestFirstTrue:
    """Tests for `first_true`."""

    def test_something_true(self):
        """Test with no keyword arguments."""
        assert first_true(range(10), 1)

    def test_nothing_true(self):
        """Test default return value."""
        assert first_true([0, 0, 0]) is None

    def test_default(self):
        """Test with a default keyword."""
        assert first_true([0, 0, 0], default="!") == "!"

    def test_pred(self):
        """Test with a custom predicate."""
        assert first_true([2, 4, 6], pred=lambda x: x % 3 == 0) == 6
