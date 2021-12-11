#!/usr/bin/python

import sys
import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='Path to JSON file (default: read from standard input)')
    parser.add_argument(
        '--prefixes', '--prefix', type=str, nargs='*', default=['src/'],
        help="Prefix to collapse (default: ['src/']")
    return parser.parse_args()


def get_strings(items):
    return [x for x in items if isinstance(x, str)]


def get_others(items):
    return [x for x in items if not isinstance(x, str)]


def unique(items):
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            result.append(x)
        seen.add(x)
    return result


def collapse_strings(items, prefixes, replace=".."):
    results = []
    for item in items:
        result = item
        for prefix in prefixes:
            if item.startswith(prefix):
                result = prefix + replace
                break
        results.append(result)
    return unique(results)


def filter_paths(obj, prefixes):
    if isinstance(obj, list):
        strings = get_strings(obj)
        others = get_others(obj)
        if strings:
            strings = collapse_strings(strings, prefixes)
        return strings + [filter_paths(x, prefixes) for x in others]
    if isinstance(obj, dict):
        return {k: filter_paths(v, prefixes) for k, v in obj.items()}
    return obj


def main(args):
    obj = json.load(args.file)
    obj = filter_paths(obj, prefixes=args.prefixes)
    json.dump(obj, sys.stdout)


if __name__ == '__main__':
    main(parse_args())
