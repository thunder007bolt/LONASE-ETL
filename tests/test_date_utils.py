from utils.date_utils import parse_date_multi, date_string_to_date


def test_parse_date_multi_handles_multiple_formats():
    assert parse_date_multi("2024-01-15").strftime("%Y-%m-%d") == "2024-01-15"
    assert parse_date_multi("15-01-2024").strftime("%Y-%m-%d") == "2024-01-15"
    assert parse_date_multi("15/01/2024").strftime("%Y-%m-%d") == "2024-01-15"


def test_date_string_to_date_invalid_returns_none():
    assert date_string_to_date("not-a-date") is None

