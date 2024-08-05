from datetime import datetime
from unittest.mock import patch

import pytest

from utils import (
    ValidationError,
    calc_reminder_date,
    get_previous_user_message,
    parse_reminder_command,
    parse_validate_reminder_command,
    validate_reminder_date,
)


def test_parse_validate_reminder_command():
    with pytest.raises(ValidationError):
        parse_validate_reminder_command(" 100000h ")

    with pytest.raises(ValidationError):
        parse_reminder_command(" -12h ")

    with pytest.raises(ValidationError):
        parse_validate_reminder_command(" h ")

    with patch("utils.datetime") as mock:
        mock.now.return_value = datetime.fromisoformat("2024-07-15")
        with pytest.raises(ValidationError):
            parse_validate_reminder_command("150m")
        date = parse_validate_reminder_command("  5m ")
        assert date == datetime.fromisoformat("2024-12-15")
        date = parse_validate_reminder_command("  1h ")
        assert date == datetime.fromisoformat("2024-07-15 01:00:00")


def test_parse_message():
    n, p = parse_reminder_command(" 5d  ")
    assert n == 5
    assert p == "d"

    n, p = parse_reminder_command(" 5000h ")
    assert n == 5000
    assert p == "h"

    n, p = parse_reminder_command(" 100d ")
    assert n == 100
    assert p == "d"

    n, p = parse_reminder_command(" 99999h ")
    assert n == 99999
    assert p == "h"

    with pytest.raises(ValidationError):
        parse_reminder_command(" 100000h ")

    with pytest.raises(ValidationError):
        parse_reminder_command(" 1.02h ")

    with pytest.raises(ValidationError):
        parse_reminder_command(" -12h ")

    with pytest.raises(ValidationError):
        parse_reminder_command(" h ")

    with pytest.raises(ValidationError):
        parse_reminder_command(" 1 ")


def test_calc_reminder_date():
    date = calc_reminder_date(
        datetime.fromisoformat("2024-07-01 00:00:00"), 5, "h"
    )
    assert date == datetime.fromisoformat("2024-07-01 05:00:00")

    date = calc_reminder_date(datetime.fromisoformat("2024-07-01"), 10, "d")
    assert date == datetime.fromisoformat("2024-07-11")

    date = calc_reminder_date(datetime.fromisoformat("2024-07-01"), 2, "w")
    assert date == datetime.fromisoformat("2024-07-15")

    date = calc_reminder_date(datetime.fromisoformat("2024-01-01"), 10, "m")
    assert date == datetime.fromisoformat("2024-11-01")


def test_validate_reminder_date():
    with patch("utils.datetime") as mock:
        mock.now.return_value = datetime.fromisoformat("2024-07-15")
        validate_reminder_date(datetime.fromisoformat("2034-07-15"))
        with pytest.raises(ValidationError):
            validate_reminder_date(datetime.fromisoformat("2034-07-16"))


def test_get_previous_user_message():
    messages = [
        {"message": {"id": 0, "from": {"id": 1}}},
        {"message": {"id": 1, "from": {"id": 1}}},
        {"message": {"id": 2, "from": {"id": 1}}},
        {"message": {"id": 3, "from": {"id": 1}}},
        {"message": {"id": 4, "from": {"id": 2}}},
        {"message": {"id": 5, "from": {"id": 3}}},
    ]
    message = get_previous_user_message(messages, 2, 1)
    assert message["message"]["id"] == 1

    message = get_previous_user_message(messages, 1, 1)
    assert message["message"]["id"] == 0

    message = get_previous_user_message(messages, 0, 1)
    assert message is None

    message = get_previous_user_message(messages, 5, 3)
    assert message is None
