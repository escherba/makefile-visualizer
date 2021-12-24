#!/usr/bin/python

import sys
import json


class Id(object):

    def __init__(self):
        super().__init__()
        self._id = 0

    @property
    def id(self):
        self._id += 1
        return self._id


def print_single_graph(graph, i, skiptargets=None):
    name_to_node = {}

    def _escape(s):
        return '"{}"'.format(s.replace('"', r'\"'))

    def _register_node(name, i, fillcolor="none"):
        if not (name in name_to_node):
            node = 'n{}'.format(i.id)
            name_to_node[name] = node
            print(f'{node}[label={name}, style = "solid,filled", fillcolor="{fillcolor}"]')

    print("subgraph cluster{}{{".format(i.id))

    parents = []
    for target, deps in graph.items():
        target_str = _escape(target)
        parents.append(target_str)

    if skiptargets is None:
        skiptargets = []

    for target, deps in graph.items():
        if target not in skiptargets:
            target_str = _escape(target)
            _register_node(target_str, i)
            target_node = name_to_node[target_str]
        for dep in deps:
            dep_str = _escape(dep)
            if dep_str in parents:
                _register_node(dep_str, i)
            else:
                _register_node(dep_str, i, fillcolor="grey")
            if target not in skiptargets:
                print('{} -> {}'.format(target_node, name_to_node[dep_str]))
    print("}")


def _parse_args(args):
    if len(args) != 1:
        print('# convert a dependency graph stored in JSON format to DOT format')
        print('{} < deps.json | dot -Tpdf >| workflow.pdf'.format(args[0]))
        sys.exit(1)


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
    skiptargets = [".PHONY", ".SUFFIXES"]
    for graph in json.load(sys.stdin):
        print_single_graph(graph, i, skiptargets=skiptargets)
    print("}")


if __name__ == '__main__':
    main(sys.argv)
