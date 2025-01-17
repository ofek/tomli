"""Utilities for tests that are in the "burntsushi" format."""

import datetime
from typing import Any


def convert(obj):  # noqa: C901
    if isinstance(obj, str):
        return {"type": "string", "value": obj}
    elif isinstance(obj, bool):
        return {"type": "boolean", "value": str(obj).lower()}
    elif isinstance(obj, int):
        return {"type": "integer", "value": str(obj)}
    elif isinstance(obj, float):
        return {"type": "float", "value": str(obj)}
    elif isinstance(obj, datetime.datetime):
        val = normalize_datetime_str(obj.isoformat())
        if obj.tzinfo:
            return {"type": "offset datetime", "value": val}
        return {"type": "local datetime", "value": val}
    elif isinstance(obj, datetime.time):
        return {
            "type": "local time",
            "value": str(obj),
        }
    elif isinstance(obj, datetime.date):
        return {
            "type": "local date",
            "value": str(obj),
        }
    elif isinstance(obj, list):
        return {
            "type": "array",
            "value": [convert(i) for i in obj],
        }
    elif isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    raise Exception("unsupported type")


def normalize(d: dict) -> dict:
    normalized: Any = {}
    for k, v in d.items():
        if isinstance(v, list):
            normalized[k] = [normalize(item) for item in v]
        elif isinstance(v, dict):
            if "type" in v and "value" in v:
                if v["type"] == "float":
                    normalized[k] = v.copy()
                    normalized[k]["value"] = normalize_float_str(normalized[k]["value"])
                elif v["type"] in {"offset datetime", "local datetime"}:
                    normalized[k] = v.copy()
                    normalized[k]["value"] = normalize_datetime_str(
                        normalized[k]["value"]
                    )
                else:
                    normalized[k] = v
            else:
                normalized[k] = v
        else:
            raise AssertionError("Burntsushi fixtures should be dicts/lists only")
    return normalized


def normalize_datetime_str(dt_str: str) -> str:
    if dt_str[-1].lower() == "z":
        dt_str = dt_str[:-1] + "+00:00"

    date = dt_str[:10]
    rest = dt_str[11:]

    if "+" in rest:
        sign = "+"
    elif "-" in rest:
        sign = "-"
    else:
        sign = ""

    if sign:
        time, _, offset = rest.partition(sign)
    else:
        time = rest
        offset = ""

    time = time.rstrip("0") if "." in time else time
    return date + "T" + time + sign + offset


def normalize_float_str(float_str: str) -> str:
    return str(float(float_str))
