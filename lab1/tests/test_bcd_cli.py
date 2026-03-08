import pytest
import lab1_7


def test_cli_invalid_input(monkeypatch):
    inputs = iter(["abc", "123", "456", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1_7.main()


def test_cli_valid(monkeypatch):
    inputs = iter(["12", "34", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    lab1_7.main()