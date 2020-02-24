#!/usr/bin/python3
# coding=utf-8

import argparse
from urllib.parse import urlparse
from web3 import Web3
import datetime
import collections

import eth_util

tx_list = []

class Transaction():
    def __init__(self, tx_hash, tx_from, tx_to, gas_price, tx_input, timestamp):
        self.tx_hash = tx_hash
        self.tx_from = tx_from
        self.tx_to = tx_to
        self.gas_price = gas_price
        self.tx_input = tx_input
        self.timestamp = timestamp

    def __str__(self):
        return self.tx_hash

def run_script(ipc_path, duration):
    provider = Web3.IPCProvider(ipc_path, timeout=60)
    w3 = Web3(provider)
    contract_ranking = collections.Counter()
    frontrunner_ranking = collections.Counter()
    start_time = datetime.datetime.now()
    while (datetime.datetime.now() - start_time).seconds < duration:
        mempool_txs = w3.eth.getBlock("pending").transactions
        timestamp = datetime.datetime.now()
        for tx_hash in mempool_txs:
            w3_tx = w3.eth.getTransaction(tx_hash)
            if w3_tx != None and w3_tx.blockNumber == None:
                new_tx = Transaction(w3_tx.hash, w3_tx["from"], w3_tx.to, w3_tx.gasPrice, w3_tx.input, timestamp)
                is_new_transaction = True
                front_running_string = None
                for old in tx_list:
                    if old.tx_hash == new_tx.tx_hash:
                        is_new_transaction = False
                        break
                    # same recipient, same function, at least 50% higher gas price, at least 3 sec later timestamp
                    elif (old.tx_to == new_tx.tx_to and old.tx_input[:10] == new_tx.tx_input[:10]
                    and 1.5*old.gas_price <= new_tx.gas_price and (new_tx.timestamp - old.timestamp).seconds >= 3):
                        front_running_string = "Possible Front Running in contract {}\n - original tx: {} (at {}, gasPrice: {})\n - frontrunner: {} (at {}, gasPrice: {})\n".format(
                            old.tx_to, old.tx_hash.hex(), old.timestamp, old.gas_price, new_tx.tx_hash.hex(), new_tx.timestamp, new_tx.gas_price)
                        contract_ranking[old.tx_to] += 1
                        frontrunner_ranking[new_tx.tx_hash.hex()] += 1
                if is_new_transaction:
                    tx_list.append(new_tx)
                    if front_running_string != None:
                        print(front_running_string, flush=True)
        prune_transactions(w3)
    i = 1
    for r in contract_ranking.most_common():
        print("{:02}. {} - {}".format(i, r[1], r[0]))
        i += 1
        if i > 99:
            break
    print("In total {} contracts".format(len(contract_ranking)))
    i = 1
    for r in frontrunner_ranking.most_common():
        print("{:02}. {} - {}".format(i, r[1], r[0]))
        i += 1
        if i > 99:
            break
    print("In total {} frontrunners".format(len(frontrunner_ranking)))

# delete transactions that are already mined in a block or are older than 5 minutes
def prune_transactions(w3):
    timestamp = datetime.datetime.now()
    i = 0
    while i < len(tx_list):
        w3_tx = w3.eth.getTransaction(tx_list[i].tx_hash)
        if w3_tx != None and w3_tx.blockNumber != None:
            tx_list.pop(i)
        elif (timestamp - tx_list[i].timestamp).seconds > 300:
            tx_list.pop(i)
        else:
            i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect instances of Front Running')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    parser.add_argument('--duration', type=int, dest='duration', default=3600, help='For how many seconds the script should run')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)
    run_script(uri.path, args.duration)
