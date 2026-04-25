class HashTable:
    DELETED = "<DELETED>"

    def __init__(self, size=30):
        self.size = size
        self.table = [None] * size

    def hash_function(self, key):
        return sum(ord(char) for char in key.lower()) % self.size

    def create(self, key, value):
        index = self.hash_function(key)

        for i in range(self.size):
            current_index = (index + i) % self.size
            item = self.table[current_index]

            if item is None or item == self.DELETED:
                self.table[current_index] = (key, value)
                return True

            if item[0].lower() == key.lower():
                return False

        return False

    def read(self, key):
        index = self.hash_function(key)

        for i in range(self.size):
            current_index = (index + i) % self.size
            item = self.table[current_index]

            if item is None:
                return None

            if item != self.DELETED and item[0].lower() == key.lower():
                return item[1]

        return None

    def update(self, key, new_value):
        index = self.hash_function(key)

        for i in range(self.size):
            current_index = (index + i) % self.size
            item = self.table[current_index]

            if item is None:
                return False

            if item != self.DELETED and item[0].lower() == key.lower():
                self.table[current_index] = (key, new_value)
                return True

        return False

    def delete(self, key):
        index = self.hash_function(key)

        for i in range(self.size):
            current_index = (index + i) % self.size
            item = self.table[current_index]

            if item is None:
                return False

            if item != self.DELETED and item[0].lower() == key.lower():
                self.table[current_index] = self.DELETED
                return True

        return False

    def display(self):
        print("\nТекущая хеш-таблица:")
        for i, item in enumerate(self.table):
            if item is None:
                print(f"{i}: пусто")
            elif item == self.DELETED:
                print(f"{i}: удалено")
            else:
                print(f"{i}: {item[0]} — {item[1]}")


def fill_initial_physics_data(hash_table):
    initial_data = {
        "Сила": "Физическая величина, характеризующая воздействие одного тела на другое.",
        "Масса": "Физическая величина, являющаяся мерой инертности тела.",
        "Скорость": "Физическая величина, показывающая изменение положения тела за единицу времени.",
        "Ускорение": "Физическая величина, показывающая изменение скорости тела за единицу времени.",
        "Энергия": "Физическая величина, характеризующая способность тела или системы совершать работу.",
        "Работа": "Физическая величина, равная произведению силы на перемещение в направлении действия силы.",
        "Мощность": "Физическая величина, равная работе, выполненной за единицу времени.",
        "Импульс": "Физическая величина, равная произведению массы тела на его скорость.",
        "Давление": "Физическая величина, равная отношению силы к площади поверхности.",
        "Температура": "Физическая величина, характеризующая степень нагретости тела.",
        "Плотность": "Физическая величина, равная отношению массы тела к его объему.",
        "Заряд": "Физическая величина, характеризующая способность тел участвовать в электромагнитном взаимодействии.",
        "Напряжение": "Физическая величина, равная работе электрического поля по перемещению заряда.",
        "Сопротивление": "Физическая величина, характеризующая способность проводника препятствовать прохождению электрического тока.",
        "Ток": "Упорядоченное движение заряженных частиц.",
        "Магнитное поле": "Форма материи, через которую осуществляется взаимодействие между движущимися электрическими зарядами.",
        "Гравитация": "Фундаментальное взаимодействие, проявляющееся во взаимном притяжении тел.",
        "Инерция": "Свойство тела сохранять состояние покоя или равномерного прямолинейного движения.",
        "Колебание": "Процесс периодического изменения физической величины.",
        "Волна": "Процесс распространения колебаний в пространстве с переносом энергии."
    }

    for key, value in initial_data.items():
        hash_table.create(key, value)


def menu():
    physics_terms = HashTable(size=30)
    fill_initial_physics_data(physics_terms)

    while True:
        print("\n===== ХЕШ-ТАБЛИЦА: ФИЗИКА =====")
        print("1. Показать хеш-таблицу")
        print("2. Добавить новый термин")
        print("3. Найти термин")
        print("4. Изменить определение термина")
        print("5. Удалить термин")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            physics_terms.display()

        elif choice == "2":
            key = input("Введите название физического термина: ")
            value = input("Введите определение термина: ")

            if physics_terms.create(key, value):
                print("Термин успешно добавлен.")
            else:
                print("Ошибка: термин уже существует или хеш-таблица заполнена.")

        elif choice == "3":
            key = input("Введите термин для поиска: ")
            result = physics_terms.read(key)

            if result is not None:
                print(f"{key}: {result}")
            else:
                print("Термин не найден.")

        elif choice == "4":
            key = input("Введите термин, который нужно изменить: ")
            new_value = input("Введите новое определение: ")

            if physics_terms.update(key, new_value):
                print("Определение успешно изменено.")
            else:
                print("Термин не найден.")

        elif choice == "5":
            key = input("Введите термин для удаления: ")

            if physics_terms.delete(key):
                print("Термин успешно удалён.")
            else:
                print("Термин не найден.")

        elif choice == "0":
            print("Работа программы завершена.")
            break

        else:
            print("Ошибка: выберите пункт меню от 0 до 5.")


if __name__ == "__main__":
    menu()