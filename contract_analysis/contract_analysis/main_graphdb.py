#!/usr/bin/python3
# coding=utf-8

import argparse
from neo4j.exceptions import ClientError
from neo4j.v1 import GraphDatabase

import eth_util

def run_query(address, user, password):
    driver = GraphDatabase.driver(address, auth=(user, password), max_retry_time=1)
    with driver.session() as session:
        with session.begin_transaction() as tx:
            try:
                result = tx.run("""
                    MATCH (sender:Address)<-[:TX_FROM]-(tx:Transaction)-[:TX_TO]->(a:Address)
                    WHERE a.hash = 0
                    RETURN sender.hash,tx.nonce,tx.input
                    """)
                for r in result:
                    address = eth_util.calculate_contract_address(r["sender.hash"], int(r["tx.nonce"], 16))
                    code = eth_util.bytecode_to_opcodes(r["tx.input"])
                    print(address, ",".join(code))
            except ClientError as e:
                print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--neo-address', type=str, dest='address', default="bolt://localhost:7687",
                        help='Connections string for the Neo4J server')
    parser.add_argument('--neo-user', type=str, dest='user', default='neo4j', help='Neo4J Username')
    parser.add_argument('--neo-password', type=str, dest='password', default='neo4j', help='Neo4J Password')
    args = parser.parse_args()
    run_query(args.address, args.user, args.password)
