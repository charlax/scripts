#!/usr/bin/env python

"""
Metaprogramming script to generate SQL inserts for a country table.
"""

import os
import re
import csv
import argparse
from datetime import datetime

import json
import yaml


# This file is used to get countries that should be inserted
COUNTRIES_TO_UPDATE_FILENAME = "existing_countries.csv"
SQL_TEMPLATE_INSERT = "INSERT INTO country (label, iso2, iso3, currency_code, telephone_code, telephone_international_prefix, telephone_national_prefix, distance_unit, name, created_at, updated_at) VALUES ({label}, {alpha2}, {alpha3}, {currency}, {country_code}, {international_prefix}, {national_prefix}, 'km', {name_json}, {now}, {now});"
SQL_TEMPLATE_UPDATE = "UPDATE country SET telephone_international_prefix={international_prefix}, telephone_national_prefix={national_prefix}, updated_at={now} WHERE id={id_};"


def sqlize(env):
    """Use SQL values and add quotes.

    Use this only for meta-programming! SQL injection is possible.
    """

    for key in env.keys():
        if env[key] is None:
            env[key] = "NULL"
        else:
            env[key] = "'%s'" % env[key]

        env[key] = env[key].encode("utf-8", "replace")


def labelize(name):
    """Clean a country name."""

    name = name.replace(" ", "_").lower().encode("ascii", "replace")
    name = re.sub("\W", "", name)

    return name


def main(args):
    with open(args.input_filename) as f:
        content = yaml.load(f.read())

    countries_to_update = {}
    if COUNTRIES_TO_UPDATE_FILENAME and os.path.exists(COUNTRIES_TO_UPDATE_FILENAME):
        with open(COUNTRIES_TO_UPDATE_FILENAME) as f:
            reader = csv.DictReader(f)

            for row in reader:
                countries_to_update[row["iso2"].strip()] = row["id"]

    now = datetime.utcnow().replace(microsecond=0)
    sql = {"insert": [], "update": []}
    for alpha2, country in content.items():
        env = country
        env["now"] = now
        env["label"] = labelize(country["name"])
        env["country_code"] = "+" + env["country_code"]
        env["name_json"] = json.dumps({"en": country["names"][0]})
        sqlize(env)

        if alpha2 in countries_to_update.keys():
            env["id_"] = countries_to_update[alpha2]
            sql["update"].append(SQL_TEMPLATE_UPDATE.format(**env))
        else:
            sql["insert"].append(SQL_TEMPLATE_INSERT.format(**env))

    sql = "\n".join(sql["insert"] + sql["update"])

    if not args.output_filename:
        print sql

    else:
        with open(args.output_filename, "w") as f:
            f.write(sql)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert countries yaml file to SQL.")
    parser.add_argument("input_filename", nargs="?", help="yaml file",
            default="countries.yaml")
    parser.add_argument("output_filename", nargs="?", help="SQL file")
    args = parser.parse_args()
    main(args)
