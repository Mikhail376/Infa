import struct
import sys

# Исключение парсера
class ParseError(Exception):
    pass

#  Бинарный ридер
class BReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.len = len(data)

    def read(self, n: int) -> bytes:
        if self.pos + n > self.len:
            raise ParseError("Unexpected EOF")
        res = self.data[self.pos:self.pos + n]
        self.pos += n
        return res

    def read_u8(self) -> int:
        return struct.unpack(">B", self.read(1))[0]

    def read_u16(self) -> int:
        return struct.unpack(">H", self.read(2))[0]

    def read_i32(self) -> int:
        return struct.unpack(">i", self.read(4))[0]

    def read_str(self) -> str:
        length = self.read_u16()
        if length == 0:
            return ""
        return self.read(length).decode("utf-8")

#  Рекурсивное чтение msgpack-подобного формата
def read_obj(reader: BReader):
    t = reader.read(1)
    if t == b'D':  # dict
        n = reader.read_u16()
        res = {}
        for _ in range(n):
            key = reader.read_str()
            val = read_obj(reader)
            res[key] = val
        return res
    elif t == b'L':  # list
        n = reader.read_u16()
        return [read_obj(reader) for _ in range(n)]
    elif t == b'S':  # string
        return reader.read_str()
    elif t == b'I':  # int
        return reader.read_i32()
    elif t == b'B':  # bool
        bval = reader.read_u8()
        return bool(bval)
    else:
        raise ParseError(f"Unknown type byte {t}")

# JSON-сериализация вручную
def json_escape(s: str) -> str:
    res = []
    for ch in s:
        code = ord(ch)
        if ch == '"': res.append('\\"')
        elif ch == '\\': res.append('\\\\')
        elif ch == '\b': res.append('\\b')
        elif ch == '\f': res.append('\\f')
        elif ch == '\n': res.append('\\n')
        elif ch == '\r': res.append('\\r')
        elif ch == '\t': res.append('\\t')
        elif code < 0x20: res.append('\\u%04x' % code)
        else: res.append(ch)
    return ''.join(res)

def to_json(obj, indent=0):
    pad = ' ' * (indent * 4)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            key = '"' + json_escape(str(k)) + '"'
            val = to_json(v, indent + 1)
            items.append(f"{pad}    {key}: {val}")
        if not items: return "{}"
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    elif isinstance(obj, list):
        items = [pad + "    " + to_json(i, indent + 1) for i in obj]
        if not items: return "[]"
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, int):
        return str(obj)
    else:
        return '"' + json_escape(str(obj)) + '"'

# Основные функции
def parse_bin_file_to_struct(path):
    with open(path, "rb") as f:
        data = f.read()
    reader = BReader(data)
    magic = reader.read(4)
    if magic != b"MSGP":
        raise ParseError("Invalid file format")
    version = reader.read_u8()
    if version != 1:
        raise ParseError("Unsupported version")
    return read_obj(reader)

def save_json(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

#  Точка входа
def main():
    if len(sys.argv) >= 2:
        in_path = sys.argv[1]
    else:
        in_path = "schedule_msgpack_like.bin"
    out_path = "schedule_from_bin.json"

    try:
        parsed = parse_bin_file_to_struct(in_path)
    except FileNotFoundError:
        print("File not found:", in_path, file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print("Parse error:", e, file=sys.stderr)
        sys.exit(2)

    json_text = to_json(parsed, indent=0) + "\n"
    save_json(json_text, out_path)
    print("JSON создан:", out_path)

if __name__ == "__main__":
    main()
