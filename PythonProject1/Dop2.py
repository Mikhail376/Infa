
import msgpack
import json
import tomllib


# Чтение TOML и сохранение в msgpack
def toml_to_msgpack(toml_path: str, msgpack_path: str):
    # Чтение TOML
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)  # словарь Python

    # Сериализация в msgpack
    with open(msgpack_path, "wb") as f:
        msgpack.pack(data, f)

    print("Создан msgpack-файл:", msgpack_path)


#Чтение msgpack и сохранение в JSON
def msgpack_to_json(msgpack_path: str, json_path: str):
    # Чтение msgpack
    with open(msgpack_path, "rb") as f:
        data = msgpack.unpack(f, raw=False)  # raw=False чтобы строки были str, а не bytes

    # Сериализация в JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Создан JSON-файл:", json_path)


#  Точка входа
def main():
    toml_file = "schedule.toml"  # исходный TOML
    msgpack_file = "schedule.msgpack"  # бинарный формат msgpack
    json_file = "schedule.json"  # результат JSON

    toml_to_msgpack(toml_file, msgpack_file)
    msgpack_to_json(msgpack_file, json_file)


if __name__ == "__main__":
    main()
