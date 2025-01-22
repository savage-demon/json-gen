import json
import argparse
import uuid
from datetime import datetime
from typing import Any, Dict, List, Union
from faker import Faker

fake = Faker()


def generate_data(template: Union[Dict, List], parent_index: int = 1) -> Any:
    if isinstance(template, list):
        result = []
        for item in template:
            if isinstance(item, dict) and "count" in item:
                count = item["count"]
                child_template = (
                    template[template.index(item) + 1]
                    if len(template) > template.index(item) + 1
                    else {}
                )
                for i in range(count):
                    result.append(generate_data(child_template, i + 1))

        return result

    elif isinstance(template, dict):
        result = {}
        for k, v in template.items():
            result[k] = generate_data(v, parent_index)

        return result

    elif isinstance(template, str):
        result_string = replace_in_string(
            template, parent_index).replace("\n", "")
        if result_string.endswith(":to_int"):
            return int(result_string[: -len(":to_int")])

        if result_string.endswith(":to_float"):
            return float(result_string[: -len(":to_float")])

        if result_string.endswith(":to_bool"):
            return result_string[: -len(":to_bool")]

        return result_string

    return template


def parse_placeholder(placeholder: str, index: int) -> str:
    if ":" in placeholder:
        type_, params = placeholder.split(":", 1)
        params = params.split("-")
    else:
        type_ = placeholder
        params = []

    if type_ == "index":
        lpad = params[0] if params else 1
        return str(index).zfill(int(lpad))

    elif type_ == "date":
        fmt = "-".join(params) if params else "%Y-%m-%d"
        return datetime.now().strftime(fmt)

    elif type_ == "uuid":
        return str(uuid.uuid4())

    elif type_ == "email":
        return fake.email()

    elif type_ == "phone":
        return str(fake.phone_number())

    elif type_ == "int":
        min_val = int(params[0]) if params else 0
        max_val = int(params[1]) if len(params) > 1 else 1000
        return str(fake.random_int(min_val, max_val))

    elif type_ == "float":
        min_val = float(params[0]) if params else 0.0
        max_val = float(params[1]) if len(params) > 1 else 1.0
        return f"{fake.pyfloat(min_value=min_val, max_value=max_val, left_digits=4, right_digits=2)}"

    elif type_ == "address":
        return fake.address()

    elif type_ == "char":
        params = int(params[0]) if params else 1
        return fake.pystr(min_chars=params, max_chars=params)

    elif type_ == "ichar":
        params = int(params[0]) if params else 1
        min = 10**params
        max = 10 ** (params + 1)
        return str(fake.random_int(min, max - 1))

    elif type_ == "bool":
        return str(fake.pybool())

    return placeholder


def replace_in_string(s: str, index: int) -> str:
    result = []
    i = 0
    while i < len(s):
        if s[i] == "{" and "}" in s[i:]:
            end = s.index("}", i)
            placeholder = s[i + 1: end]
            result.append(parse_placeholder(placeholder, index))
            i = end + 1
        else:
            result.append(s[i])
            i += 1
    return "".join(result)


def replace_placeholders(data: Any, index: int) -> Any:
    if isinstance(data, dict):
        return {k: replace_placeholders(v, index) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_placeholders(item, index) for item in data]
    elif isinstance(data, str):
        return replace_in_string(data, index)
    return data


def main():
    parser = argparse.ArgumentParser(description="JSON Data Generator")
    parser.add_argument("input", help="Input schema file")
    parser.add_argument(
        "-o", "--output", default="output.json", help="Output file")
    args = parser.parse_args()

    with open(args.input) as f:
        schema = json.load(f)

    result = generate_data(schema)

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
