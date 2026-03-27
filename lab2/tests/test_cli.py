from app.cli import run_cli


def test_cli_runs(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "a&b")
    run_cli()
    captured = capsys.readouterr().out

    assert "Таблица истинности" in captured
    assert "СДНФ" in captured
    assert "СКНФ" in captured
    assert "Индексная форма" in captured or "Индекс функции" in captured
    assert "Классы Поста" in captured
    assert "Полином Жегалкина" in captured
    assert "Фиктивные переменные" in captured
    assert "Производные" in captured
    assert "Минимизация" in captured