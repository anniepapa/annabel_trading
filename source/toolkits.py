import json
import csv
import pytz
from datetime import datetime
from decimal import Decimal, ROUND_UP
from operator import itemgetter


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
    identifier = (
        "iDEAL Deposit",
        "Valuta Debitering",
        "Reservation iDEAL / Sofort Deposit",
    )
    content = sorted(
        content, key=itemgetter("value_date", "balance"), reverse=True
    )

    for item in content:
        if item[key_name] in identifier:
            return item.get("balance") or item.get("")


def sort_dict_string_content(string_csv):
    content = list(csv.DictReader(string_csv.splitlines(), delimiter=","))
    content.sort(
        key=lambda x: (x["Datum"], -Decimal(x[""].replace(",", "."))),
        reverse=True,
    )
    return content
