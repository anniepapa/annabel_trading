import json
import pytz
from datetime import datetime
from decimal import Decimal, ROUND_UP


def pretty_table(target_table):
    return json.dumps(
        target_table,
        sort_keys=True,
        indent=4,
    )


def utc_to_cet(datetime_str):
    response_datetime = datetime.strptime(
        datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    reponse_utc = pytz.utc.localize(response_datetime)
    cet = reponse_utc.astimezone(pytz.timezone("Europe/Amsterdam"))
    return datetime.strftime(cet, "%Y-%m-%dT%H:%M:%S")


def decimalize(value, prec=".0001"):
    return Decimal(value).quantize(Decimal(prec), rounding=ROUND_UP)


def get_last_valuta_balance(content, key_name="description"):
    for item in content:
        if item[key_name] == "Valuta Debitering":
            return item.get("balance") or item.get("")
