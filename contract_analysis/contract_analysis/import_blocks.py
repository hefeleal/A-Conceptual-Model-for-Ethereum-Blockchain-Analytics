#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
from typing import Iterable
from datetime import datetime
from urllib.parse import urlparse
from web3 import Web3

import eth_util

def save_blocks(db, w3, origin, blocks: Iterable):
    cursor = db.cursor()
    block_insert_set = []
    contractTransaction_insert_set = []
    contractCode_insert_set = []
    contract_insert_set = []
    for block in blocks:
        block_insert_set.append(
            (int(block['number'], 16), block['hash'], datetime.fromtimestamp(int(block['timestamp'], 16)))
        )
        for tx in block['transactions']:
            if tx['to'] == None:
                contractTransaction_insert_set.append(
                    (tx['hash'], tx['value'], int(tx['nonce'], 16), tx['input'], int(tx['transactionIndex'], 16),
                        tx['gas'], tx['gasPrice'], int(block['number'], 16), tx['from'], tx['to'])
                )
                contract_address = eth_util.calculate_contract_address(tx['from'], int(tx['nonce'], 16))
                classified_parts = eth_util.extract_contract_code(tx['input'])
                actually_deployed_code = w3.eth.getCode(Web3.toChecksumAddress(contract_address)).hex()
                if actually_deployed_code == "0x":
                    contract_is_selfdestructed = True
                    code_to_save = classified_parts[1]
                else:
                    contract_is_selfdestructed = False
                    code_to_save = actually_deployed_code
                opcodes = eth_util.bytecode_to_opcodes(code_to_save)
                codeHash = eth_util.calculate_code_hash(code_to_save)
                contractCode_insert_set.append(
                    (codeHash, code_to_save, ("CREATE" in opcodes), 1)
                )
                contract_insert_set.append(
                    (contract_address, codeHash, tx['hash'], classified_parts[0], classified_parts[2], contract_is_selfdestructed, origin)
                )
    cursor.executemany("""INSERT INTO block (blockNumber, hash, timestamp)
        VALUES (%s, %s, %s)""", block_insert_set)
    cursor.executemany("""INSERT INTO contractTransaction (hash, txValue, nonce, input, txIndex, gas, gasPrice, blockNumber, txFrom, txTo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", contractTransaction_insert_set)
    cursor.executemany("""INSERT INTO contractCode (hash, code, hasCreateOpcode, occurrences)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE occurrences=occurrences+1;""", contractCode_insert_set)
    cursor.executemany("""INSERT INTO contract (address, contractHash, transactionHash, contractCreationCode, constructorArguments, selfdestructed, origin)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE address=address;""", contract_insert_set)
    db.commit()

def get_blocks(provider, start, end):
    for n in range(start, end):
        yield get_block(provider, n)

def get_block(provider, block_num):
    data = provider.make_request("eth_getBlockByNumber", [hex(block_num), True])["result"]
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import transactions and contracts into the MySQL database')
    parser.add_argument('--start-block', type=int, dest='min_block', default=6000000, help='start block number')
    parser.add_argument('--end-block', type=int, dest='max_block', default=6400000, help='end block number')
    parser.add_argument('--batch-size', type=int, dest='batch_size', default=500, help='batch size')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    parser.add_argument('--origin', type=int, dest='origin', default=0, help='Origin Network (0=Mainnet)')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)
    provider = Web3.IPCProvider(uri.path, timeout=60)
    w3 = Web3(provider)
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    for block_number in range(args.min_block, args.max_block, args.batch_size):
        blocks = get_blocks(provider, block_number, block_number + args.batch_size)
        save_blocks(db, w3, args.origin, blocks)
        print("inserted blocks {} to {}".format(block_number, block_number+args.batch_size), flush=True)
