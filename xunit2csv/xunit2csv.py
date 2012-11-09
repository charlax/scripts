#!/usr/bin/python

"""
Extract test name and time from xunit output generated with nosetest
`--with-xunit` option.
"""

import argparse
import csv
import xml.etree.ElementTree as etree


def main(args):
    tree = etree.parse(args.input[0])

    output = []
    for testcase in tree.iterfind("testcase"):
        row = {
                "classname": testcase.get("classname"),
                "name": testcase.get("name"),
                "time": testcase.get("time")}
        output.append(row)

    with open(args.output[0], "w") as f:
        writer = csv.DictWriter(f, ("classname", "name", "time"))
        writer.writeheader()
        writer.writerows(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert xunit file to CSV.")
    parser.add_argument("input", nargs=1, help="xunit file")
    parser.add_argument("output", nargs=1, help="csv file")
    args = parser.parse_args()
    main(args)
