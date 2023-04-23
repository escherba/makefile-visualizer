#!/usr/bin/python

import re
import sys
import json


def _skip_until_next_entry(fp):
    def _is_new_entry(string: str) -> bool:
        return string.startswith('\n')
    for line in fp:
        if _is_new_entry(line):
            return


def _parse_entries(fp):
    _target_re = re.compile(r':{1,2} *')

    def _parse_entry(graph, line):
        target, deps = _target_re.split(line, 1)
        graph[target] =[dep for dep in deps.split() if dep != '|'] 

    graph = {}
    for line in fp:
        if line.startswith('# files hash-table stats:'):
            return graph
        if line.startswith('# Not a target:'):
            _skip_until_next_entry(fp)
        elif line.startswith("# makefile (from '"):
            fp.readline()  # skip information on target specific variable value
        else:
            _parse_entry(graph, line)
            _skip_until_next_entry(fp)
    return graph


def _parse_db(fp):
    for line in fp:
        if line.startswith('# Files'):
            fp.readline()  # skip the first empty line
            return _parse_entries(fp)
    return {}


def parse_make_p(fp, graphs=None):
    if graphs is None:
        graphs = []
    for line in fp:
        if line.startswith('# Make data base, printed on '):
            graph = _parse_db(fp)
            # graph = {k: vs for k, vs in graph.items() if len(vs) > 0 and k not in [".PHONY", ".SUFFIXES"]}
            if len(graph) > 0:
                graphs.append(graph)
    if not graphs:
        raise ValueError(f"{fp} seems not connected to `LANG=C make -p`")
    return graphs


def _parse_args(args):
    num_args = len(args)
    if num_args not in [1, 2, 3]:
        cmd = args[0]
        print("# parse Makefile database and print dependency graph in JSON format")
        print(f"LANG=C gmake -p | {cmd} | json_to_dot.py | dot -Tpdf >| workflow.pdf")
        sys.exit(1)


def _get_iostreams(args):
    num_args = len(args)
    input_stream = sys.stdin
    output_stream = sys.stdout
    if num_args == 2:
        input_stream = open(args[1], "r")
    elif num_args == 3:
        input_stream = open(args[1], "r")
        output_stream = open(args[2], "w")
    return input_stream, output_stream


def main(args):
    _parse_args(args)
    input_stream, output_stream = _get_iostreams(args)
    json.dump(parse_make_p(input_stream), output_stream)


if __name__ == '__main__':
    main(sys.argv)
