#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import networkx as nx
from networkx.readwrite import json_graph
import json

import eth_util

def build_graph(db):
    batch_size = 10000
    offset = 0
    graph = nx.DiGraph()
    while True:
        c = db.cursor()
        query = f"""
            SELECT code, hash
            FROM contractCode
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            opcodes = eth_util.bytecode_to_opcodes(result[0])
            referenced_addresses_in_current_code = [] # array with all addresses found in this code
            for o in opcodes:
                if o[:6] == "PUSH20":
                    if (len(o[7:]) == 42 and o[7:] != "0xffffffffffffffffffffffffffffffffffffffff"
                        and o[7:] != "0x0000000000000000000000000000000000000000"):
                        referenced_addresses_in_current_code.append(o[7:])
            if len(referenced_addresses_in_current_code) > 0: # skip this lookup if no PUSH20 was found
                addresses_with_this_code = get_all_addresses_with_contract_hash(db, result[1])
                for from_node in addresses_with_this_code:
                    for to_node in referenced_addresses_in_current_code:
                        graph.add_edge(from_node, to_node)
            result = c.fetchone()
        offset += batch_size
    return graph

def save_graph_to_file(graph, filename):
    data = json_graph.node_link_data(graph)
    with open(filename, "w") as f:
        json.dump(data, f)

def load_graph_from_file(filename):
    with open(filename) as f:
        data = json.load(f)
        return json_graph.node_link_graph(data)

def get_all_addresses_with_contract_hash(db, contractHash):
    ret = []
    c = db.cursor()
    query = f"""
        SELECT address
        FROM contract
        WHERE contractHash="{contractHash}"
        UNION
        SELECT address
        FROM contractCreatedContract
        WHERE contractHash="{contractHash}";
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        ret.append(result[0])
        result = c.fetchone()
    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculates the Page Rank for all Addresses based on references in smart contract code')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()

    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    # graph = build_graph(db)
    # save_graph_to_file(graph, "graph.json")
    graph = load_graph_from_file("graph.json")
    pr = nx.pagerank(graph, max_iter=1000)
    for key, value in sorted(pr.items(), key=lambda i:i[1], reverse=True):
        print(key, value)

    
    print("number of nodes:", len(graph.nodes()))
    print("weakly connected components:", nx.number_weakly_connected_components(graph))
    print("strongly connected components:", nx.number_strongly_connected_components(graph))
    strong_components = nx.strongly_connected_components(graph)
    for c in strong_components:
        if len(c) > 1:
            print(c)
            graph.remove_edge(list(c)[0], list(c)[1])
    graph.remove_edges_from(graph.selfloop_edges())
    print("longest path:", nx.dag_longest_path(graph))
