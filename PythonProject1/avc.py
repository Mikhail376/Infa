import struct

# Вспомогательные функции
def write_u8(f, v):
    f.write(struct.pack(">B", v & 0xFF))

def write_u16(f, v):
    f.write(struct.pack(">H", v & 0xFFFF))

def write_i32(f, v):
    f.write(struct.pack(">i", int(v)))

def write_str(f, s):
    data = s.encode("utf-8")
    write_u16(f, len(data))
    f.write(data)

# Msgpack-подобная рекурсивная сериализация
def write_obj(f, obj):
    """Записывает объект в бинарный формат: dict/list/str/int/bool"""
    if isinstance(obj, dict):
        f.write(b"D")  # dict
        write_u16(f, len(obj))
        for k, v in obj.items():
            write_str(f, k)
            write_obj(f, v)
    elif isinstance(obj, list):
        f.write(b'L')  # list
        write_u16(f, len(obj))
        for item in obj:
            write_obj(f, item)
    elif isinstance(obj, str):
        f.write(b'S')  # string
        write_str(f, obj)
    elif isinstance(obj, int):
        f.write(b'I')  # int
        write_i32(f, obj)
    elif isinstance(obj, bool):
        f.write(b'B')  # bool
        write_u8(f, 1 if obj else 0)
    else:
        f.write(b'S')
        write_str(f, str(obj))

#TOML-парсер
def parse_toml_manual(path):
    data = {}
    current_day = None
    current_section = None

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # [[Day.lesson]]
            if line.startswith("[[") and line.endswith("]]"):
                inner = line.strip("[]")
                parts = [p.strip() for p in inner.split(".")]
                if len(parts) < 2:
                    continue
                day = parts[0]
                data.setdefault(day, [])
                current_section = {}
                data[day].append(current_section)
                continue

            # key = value
            if "=" in line and current_section is not None:
                key, value = map(str.strip, line.split("=", 1))
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                current_section[key] = value

    return data

# Запись в бинарный файл
def save_to_binary(data, out_path):
    with open(out_path, "wb") as f:
        f.write(b'MSGP')  # магическая сигнатура
        write_u8(f, 1)    # версия формата
        write_obj(f, data)  # рекурсивно записываем структуру

#Точка входа
def main():
    toml_path = "schedule.toml"
    bin_path = "schedule_msgpack_like.bin"

    parsed = parse_toml_manual(toml_path)
    save_to_binary(parsed, bin_path)
    print("Создан бинарный файл:", bin_path)

if __name__ == "__main__":
    main()
