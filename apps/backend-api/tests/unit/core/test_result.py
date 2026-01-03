"""Unit tests for Result monad implementation."""

import pytest

from taskman_api.core.result import Err, Ok


class TestOk:
    """Tests for Ok result type."""

    def test_ok_is_ok_returns_true(self):
        """Ok.is_ok() should return True."""
        result = Ok("success")
        assert result.is_ok() is True

    def test_ok_is_err_returns_false(self):
        """Ok.is_err() should return False."""
        result = Ok("success")
        assert result.is_err() is False

    def test_ok_unwrap_returns_value(self):
        """Ok.unwrap() should return the wrapped value."""
        result = Ok(42)
        assert result.unwrap() == 42

    def test_ok_ok_returns_value(self):
        """Ok.ok() should return the wrapped value (alias)."""
        result = Ok("test")
        assert result.ok() == "test"

    def test_ok_unwrap_err_raises(self):
        """Ok.unwrap_err() should raise ValueError."""
        result = Ok("success")
        with pytest.raises(ValueError, match="Called unwrap_err\\(\\) on an Ok value"):
            result.unwrap_err()

    def test_ok_err_raises(self):
        """Ok.err() should raise ValueError (alias)."""
        result = Ok("success")
        with pytest.raises(ValueError, match="Called err\\(\\) on an Ok value"):
            result.err()

    def test_ok_match_args(self):
        """Ok should support pattern matching via __match_args__."""
        result = Ok("matched")
        assert result.__match_args__ == ("value",)
        assert result.value == "matched"


class TestErr:
    """Tests for Err result type."""

    def test_err_is_ok_returns_false(self):
        """Err.is_ok() should return False."""
        result = Err("error")
        assert result.is_ok() is False

    def test_err_is_err_returns_true(self):
        """Err.is_err() should return True."""
        result = Err("error")
        assert result.is_err() is True

    def test_err_unwrap_raises(self):
        """Err.unwrap() should raise ValueError with error message."""
        result = Err("something went wrong")
        with pytest.raises(ValueError, match="Called unwrap\\(\\) on an Err value"):
            result.unwrap()

    def test_err_ok_raises(self):
        """Err.ok() should raise ValueError (alias)."""
        result = Err("error")
        with pytest.raises(ValueError, match="Called ok\\(\\) on an Err value"):
            result.ok()

    def test_err_unwrap_err_returns_error(self):
        """Err.unwrap_err() should return the wrapped error."""
        error = Exception("test error")
        result = Err(error)
        assert result.unwrap_err() is error

    def test_err_err_returns_error(self):
        """Err.err() should return the wrapped error (alias)."""
        result = Err("error message")
        assert result.err() == "error message"

    def test_err_match_args(self):
        """Err should support pattern matching via __match_args__."""
        result = Err("matched error")
        assert result.__match_args__ == ("error",)
        assert result.error == "matched error"


class TestResultPatternMatching:
    """Tests for Result pattern matching support."""

    def test_pattern_match_ok(self):
        """Ok should work with Python pattern matching."""
        result = Ok(100)

        match result:
            case Ok(value):
                matched_value = value
            case Err(_):
                matched_value = None

        assert matched_value == 100

    def test_pattern_match_err(self):
        """Err should work with Python pattern matching."""
        result = Err("failure")

        match result:
            case Ok(_):
                matched_error = None
            case Err(error):
                matched_error = error

        assert matched_error == "failure"
