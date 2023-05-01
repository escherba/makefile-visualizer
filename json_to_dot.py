#!/usr/bin/python

import sys
import json
from collections import defaultdict


class Id(object):

    def __init__(self):
        super().__init__()
        self._id = 0

    @property
    def id(self):
        self._id += 1
        return self._id


OTHER = {"color": "#82B366", "fillcolor": "#D5E8D4"}  # green
INTERMEDIATE = {"color": "#D79B00", "fillcolor": "#FFE6CC"}  # orange
FINAL = {"color": "#6C8EBF", "fillcolor": "#DAE8FC"}  # blue
SOURCE = {"color": "#666666", "fillcolor": "#F5F5F5"}  # grey
ORPHAN = {"color": "#9673A6", "fillcolor": "#E1D5E7"}  # purple

def print_single_graph(graph, i, skiptargets=None):
    name_to_node = {}

    def _escape(s):
        return '"{}"'.format(s.replace('"', r'\"'))

    def _register_node(name, i, color="black", fillcolor="none"):
        if not (name in name_to_node):
            node = 'n{}'.format(i.id)
            name_to_node[name] = node
            print(f'{node}[label={name}, style="solid,filled", color="{color}", fillcolor="{fillcolor}"]')

    print("subgraph cluster{}{{peripheries=0 ".format(i.id))

    if skiptargets is None:
        skiptargets = []

    phony_str = _escape(".PHONY")
    parents = []
    for target, deps in graph.items():
        parents.append(_escape(target))

    inverse_graph = defaultdict(set)
    for target, deps in graph.items():
        for dep in deps:
            inverse_graph[_escape(dep)].add(_escape(target))

    roots = set(parents)
    for target, deps in graph.items():
        if target in skiptargets:
            continue
        for dep in deps:
            dep_str = _escape(dep)
            if dep_str in roots:
                roots.remove(dep_str)

    for target, deps in graph.items():
        if any(target in graph.get(skip, []) for skip in skiptargets) and not deps:
            continue
        if target in skiptargets:
            continue

        target_str = _escape(target)
        if target_str in roots:
            _register_node(target_str, i, **FINAL)
        elif phony_str in inverse_graph[target_str]:
            _register_node(target_str, i, **OTHER)
        else:
            _register_node(target_str, i, **INTERMEDIATE)
        target_node = name_to_node[target_str]
        for dep in deps:
            if target in skiptargets:
                continue
            dep_str = _escape(dep)
            if dep_str not in parents:
                _register_node(dep_str, i, **SOURCE)
            elif not graph[dep]:
                _register_node(dep_str, i, **ORPHAN)
            elif phony_str in inverse_graph[dep_str]:
                _register_node(dep_str, i, **OTHER)
            else:
                _register_node(dep_str, i, **INTERMEDIATE)
            print('{} -> {}'.format(target_node, name_to_node[dep_str]))
    print("}")


def _parse_args(args):
    if len(args) not in [1, 2]:
        print('# convert a dependency graph stored in JSON format to DOT format')
        print('{} < deps.json | dot -Tpdf >| workflow.pdf'.format(args[0]))
        sys.exit(1)


def _get_iostream(args):
    num_args = len(args)
    input_stream = sys.stdin
    if num_args == 2:
        input_stream = open(args[1], "r")
    return input_stream


def main(args):
    _parse_args(args)
    print("""
digraph G {
    graph [rankdir=LR]
    node [shape=box,
    style=solid
    ]
    edge [color="#00000088",
    dir=back
    ]
    """)
    i = Id()
    skiptargets = [".PHONY", ".SUFFIXES", ".DELETE_ON_ERROR"]
    input_stream = _get_iostream(args)
    for graph in json.load(input_stream):
        print_single_graph(graph, i, skiptargets=skiptargets)
    print("}")


if __name__ == '__main__':
    main(sys.argv)
