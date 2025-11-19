
import struct
import sys

# Исключение парсера
class ParseError(Exception):
    pass

# Бинарный ридер
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

#Рекурсивное чтение msgpack-подобного формата
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

# XML сериализация вручную
def xml_escape(s: str) -> str:
    # простая экранировка для XML
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

def to_xml(obj, tag="root", indent=0):
    pad = " " * (indent * 4)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            key_tag = xml_escape(str(k))
            val_xml = to_xml(v, tag=key_tag, indent=indent + 1)
            items.append(f"{pad}<{key_tag}>\n{val_xml}\n{pad}</{key_tag}>")
        return "\n".join(items)
    elif isinstance(obj, list):
        items = [to_xml(i, tag="item", indent=indent + 1) for i in obj]
        return "\n".join([f"{pad}<item>\n{item}\n{pad}</item>" for item in items])
    elif isinstance(obj, bool):
        return f"{pad}{str(obj).lower()}"
    elif isinstance(obj, int):
        return f"{pad}{obj}"
    else:
        return f"{pad}{xml_escape(str(obj))}"

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

def save_xml(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

#Точка входа
def main():
    if len(sys.argv) >= 2:
        in_path = sys.argv[1]
    else:
        in_path = "schedule_msgpack_like.bin"
    out_path = "schedule_from_bin.xml"

    try:
        parsed = parse_bin_file_to_struct(in_path)
    except FileNotFoundError:
        print("File not found:", in_path, file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print("Parse error:", e, file=sys.stderr)
        sys.exit(2)

    xml_text = "<root>\n" + to_xml(parsed, indent=1) + "\n</root>"
    save_xml(xml_text, out_path)
    print("XML создан:", out_path)

if __name__ == "__main__":
    main()
