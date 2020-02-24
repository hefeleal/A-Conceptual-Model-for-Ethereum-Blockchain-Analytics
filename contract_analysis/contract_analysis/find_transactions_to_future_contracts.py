#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
from urllib.parse import urlparse
from web3 import Web3

import eth_util

def run_query(ipc_path, user, password):
    provider = Web3.IPCProvider(ipc_path, timeout=60)
    w3 = Web3(provider)
    db = MySQLdb.connect(user=user, passwd=password, db="eth")

    threshold = 10 * eth_util.eth_in_wei
    total_number_of_tx = 0
    for nr in range(6900000):
        if nr % 100000 == 0:
            print("Blocks {} - {}:".format(nr, nr + 99999), flush=True)
        txs = w3.eth.getBlock(nr).transactions
        for t in txs:
            t_data = w3.eth.getTransaction(t)
            if t_data.value >= threshold:
                total_number_of_tx += 1
                if t_data.to != None:
                    contract_creation_blocknumber = get_block_number_for_contract(db, t_data.to)
                    if contract_creation_blocknumber != None:
                        if contract_creation_blocknumber > nr:
                            # contract was created _after_ more than 10ETH were transferred to it
                            print("{} ETH were transferred to {} on blocknumber {}, but contract was created at blocknumber {}".format(
                                t_data.value / eth_util.eth_in_wei, t_data.to, nr, contract_creation_blocknumber), flush=True)
    print("Total number of transactions with >= {} wei transferred: {}".format(threshold, total_number_of_tx))

# if addr is a user-created contract, this function returns the block number
# on which this contract was created. Otherwise returns None
def get_block_number_for_contract(db, addr):
    c = db.cursor()
    query = f"""
        SELECT blockNumber
        FROM contract, contractTransaction
        WHERE transactionHash = hash
        AND address="{addr}";
        """
    c.execute(query)
    result = c.fetchone()
    if result == None:
        return None
    return result[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finds large transactions to addresses that later turned into contracts')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)
    run_query(uri.path, args.user, args.password)
