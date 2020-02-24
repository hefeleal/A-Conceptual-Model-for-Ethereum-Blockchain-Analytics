#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
from urllib.parse import urlparse
from web3 import Web3

import eth_util

def run_query(ipc_path, db):
    provider = Web3.IPCProvider(ipc_path, timeout=60)
    w3 = Web3(provider)
    c = db.cursor()
    query = f"""
        SELECT address, SUM(c) s FROM (
            SELECT creatorAddress AS address, COUNT(*) c
            FROM contractCreatedContract
            GROUP BY creatorAddress
            UNION
            SELECT txFrom AS address, COUNT(*) c
            FROM contract, contractTransaction
            WHERE transactionHash = hash
            GROUP BY txFrom
        ) subquery
        GROUP BY address
        ORDER BY s DESC
        LIMIT 100;
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        creator_balance = w3.eth.getBalance(Web3.toChecksumAddress(result[0]))
        created_contracts_balance = get_total_created_contracts_balance(db, w3, result[0])
        print("{} (balance: {}) created {} contracts with total balance {}".format(result[0], creator_balance, result[1], created_contracts_balance), flush=True)
        result = c.fetchone()

def get_total_created_contracts_balance(db, w3, creator):
    total = 0
    batch_size = 100000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT address
            FROM contractCreatedContract
            WHERE creatorAddress = "{creator}"
            UNION
            SELECT address
            FROM contract, contractTransaction
            WHERE transactionHash = hash
            AND txFrom = "{creator}"
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            total += w3.eth.getBalance(Web3.toChecksumAddress(result[0]))
            result = c.fetchone()
        offset += batch_size
    return total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gets the balances of contracts that were created by a single contract')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    run_query(uri.path, db)
