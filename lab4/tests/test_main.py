import pytest
from main import HashTable, fill_initial_physics_data


@pytest.fixture
def table():
    return HashTable(size=30)


@pytest.fixture
def filled_table():
    table = HashTable(size=30)
    fill_initial_physics_data(table)
    return table


# ---------- INITIAL DATA ----------

def test_initial_physics_data_exists(filled_table):
    assert filled_table.read("Сила") is not None
    assert filled_table.read("Масса") is not None
    assert filled_table.read("Скорость") is not None
    assert filled_table.read("Энергия") is not None


def test_initial_data_contains_physics_definitions(filled_table):
    assert "воздействие" in filled_table.read("Сила").lower()
    assert "инертности" in filled_table.read("Масса").lower()
    assert "положения" in filled_table.read("Скорость").lower()


# ---------- CREATE ----------

def test_create_and_read(table):
    assert table.create("Кинематика", "Раздел физики, изучающий движение тел.")
    assert table.read("Кинематика") == "Раздел физики, изучающий движение тел."


def test_create_duplicate(filled_table):
    assert not filled_table.create("Сила", "Другое определение")


def test_create_until_full():
    table = HashTable(size=3)

    assert table.create("A", "1")
    assert table.create("B", "2")
    assert table.create("C", "3")
    assert not table.create("D", "4")


# ---------- READ ----------

def test_read_existing_from_initial_table(filled_table):
    result = filled_table.read("Температура")
    assert result is not None
    assert "нагретости" in result.lower()


def test_read_not_found(filled_table):
    assert filled_table.read("Неизвестный термин") is None


def test_read_case_insensitive(filled_table):
    assert filled_table.read("сила") == filled_table.read("Сила")
    assert filled_table.read("СИЛА") == filled_table.read("Сила")


# ---------- UPDATE ----------

def test_update_existing_initial_term(filled_table):
    assert filled_table.update(
        "Масса",
        "Физическая величина, характеризующая инертные свойства тела."
    )

    assert filled_table.read("Масса") == (
        "Физическая величина, характеризующая инертные свойства тела."
    )


def test_update_not_found(filled_table):
    assert not filled_table.update("Несуществующий термин", "Новое определение")


def test_update_case_insensitive(filled_table):
    assert filled_table.update("сила", "Новое определение силы.")
    assert filled_table.read("Сила") == "Новое определение силы."


# ---------- DELETE ----------

def test_delete_existing_initial_term(filled_table):
    assert filled_table.delete("Скорость")
    assert filled_table.read("Скорость") is None


def test_delete_not_found(filled_table):
    assert not filled_table.delete("Несуществующий термин")


def test_delete_case_insensitive(filled_table):
    assert filled_table.delete("сила")
    assert filled_table.read("Сила") is None


def test_delete_and_reinsert():
    table = HashTable(size=5)

    assert table.create("Сила", "Первое определение")
    assert table.delete("Сила")
    assert table.create("Сила", "Второе определение")
    assert table.read("Сила") == "Второе определение"


# ---------- COLLISIONS ----------

def test_collision_linear_probing():
    table = HashTable(size=3)

    assert table.create("A", "1")
    assert table.create("D", "2")

    assert table.read("A") == "1"
    assert table.read("D") == "2"


def test_search_through_deleted_cell():
    table = HashTable(size=3)

    table.create("A", "1")
    table.create("D", "2")

    table.delete("A")

    assert table.read("D") == "2"


def test_wrap_around_linear_probing():
    table = HashTable(size=3)

    assert table.create("A", "1")
    assert table.create("B", "2")
    assert table.create("C", "3")

    assert table.read("A") == "1"
    assert table.read("B") == "2"
    assert table.read("C") == "3"


# ---------- DISPLAY ----------

def test_display_outputs_table(capsys, filled_table):
    filled_table.display()

    captured = capsys.readouterr()

    assert "хеш-таблица" in captured.out.lower()
    assert "Сила" in captured.out
    assert "Масса" in captured.out


def test_display_after_delete(capsys):
    table = HashTable(size=5)

    table.create("Сила", "Определение")
    table.delete("Сила")
    table.display()

    captured = capsys.readouterr()

    assert "удалено" in captured.out.lower()


from unittest.mock import patch
import pytest

from main import HashTable, fill_initial_physics_data, menu


# ---------- HASH FUNCTION ----------

def test_hash_function_returns_valid_index():
    table = HashTable(size=10)

    index = table.hash_function("Сила")

    assert isinstance(index, int)
    assert 0 <= index < table.size


def test_hash_function_case_insensitive():
    table = HashTable(size=10)

    assert table.hash_function("Сила") == table.hash_function("сила")


# ---------- DISPLAY EMPTY / DELETED / FILLED ----------

def test_display_empty_table(capsys):
    table = HashTable(size=3)

    table.display()

    captured = capsys.readouterr()

    assert "0: пусто" in captured.out
    assert "1: пусто" in captured.out
    assert "2: пусто" in captured.out


def test_display_deleted_cell(capsys):
    table = HashTable(size=3)

    table.create("Сила", "Определение")
    table.delete("Сила")
    table.display()

    captured = capsys.readouterr()

    assert "удалено" in captured.out.lower()


# ---------- FULL TABLE / COLLISION BRANCHES ----------

def test_create_duplicate_after_collision():
    table = HashTable(size=3)

    table.create("A", "1")
    table.create("D", "2")

    assert not table.create("D", "другое значение")


def test_update_after_collision():
    table = HashTable(size=3)

    table.create("A", "1")
    table.create("D", "2")

    assert table.update("D", "новое")
    assert table.read("D") == "новое"


def test_delete_after_collision():
    table = HashTable(size=3)

    table.create("A", "1")
    table.create("D", "2")

    assert table.delete("D")
    assert table.read("D") is None


def test_read_stops_on_empty_cell():
    table = HashTable(size=5)

    assert table.read("Сила") is None


def test_update_stops_on_empty_cell():
    table = HashTable(size=5)

    assert not table.update("Сила", "Новое значение")


def test_delete_stops_on_empty_cell():
    table = HashTable(size=5)

    assert not table.delete("Сила")


# ---------- INITIAL DATA ----------

def test_fill_initial_physics_data_count():
    table = HashTable(size=30)

    fill_initial_physics_data(table)

    filled_cells = [
        item for item in table.table
        if item is not None and item != table.DELETED
    ]

    assert len(filled_cells) == 20


def test_fill_initial_physics_data_terms():
    table = HashTable(size=30)

    fill_initial_physics_data(table)

    assert table.read("Гравитация") is not None
    assert table.read("Магнитное поле") is not None
    assert table.read("Волна") is not None


# ---------- MENU ----------

def test_menu_exit(capsys):
    with patch("builtins.input", side_effect=["0"]):
        menu()

    captured = capsys.readouterr()

    assert "Работа программы завершена" in captured.out


def test_menu_show_table(capsys):
    with patch("builtins.input", side_effect=["1", "0"]):
        menu()

    captured = capsys.readouterr()

    assert "ХЕШ-ТАБЛИЦА: ФИЗИКА" in captured.out
    assert "Сила" in captured.out


def test_menu_add_term(capsys):
    with patch("builtins.input", side_effect=[
        "2",
        "Оптика",
        "Раздел физики, изучающий свет.",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Термин успешно добавлен" in captured.out


def test_menu_add_duplicate(capsys):
    with patch("builtins.input", side_effect=[
        "2",
        "Сила",
        "Другое определение",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "термин уже существует" in captured.out.lower()


def test_menu_find_existing_term(capsys):
    with patch("builtins.input", side_effect=[
        "3",
        "Сила",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Сила:" in captured.out


def test_menu_find_missing_term(capsys):
    with patch("builtins.input", side_effect=[
        "3",
        "Неизвестный термин",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Термин не найден" in captured.out


def test_menu_update_existing_term(capsys):
    with patch("builtins.input", side_effect=[
        "4",
        "Сила",
        "Новое определение силы.",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Определение успешно изменено" in captured.out


def test_menu_update_missing_term(capsys):
    with patch("builtins.input", side_effect=[
        "4",
        "Неизвестный термин",
        "Новое определение.",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Термин не найден" in captured.out


def test_menu_delete_existing_term(capsys):
    with patch("builtins.input", side_effect=[
        "5",
        "Сила",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Термин успешно удалён" in captured.out


def test_menu_delete_missing_term(capsys):
    with patch("builtins.input", side_effect=[
        "5",
        "Неизвестный термин",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Термин не найден" in captured.out


def test_menu_wrong_choice(capsys):
    with patch("builtins.input", side_effect=[
        "999",
        "0"
    ]):
        menu()

    captured = capsys.readouterr()

    assert "Ошибка: выберите пункт меню" in captured.out