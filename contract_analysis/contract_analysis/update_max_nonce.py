#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
from urllib.parse import urlparse
from web3 import Web3

import eth_util

def run_query_without_update(ipc_path, db):
    provider = Web3.IPCProvider(ipc_path, timeout=60)
    w3 = Web3(provider)
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT address
            FROM eth.contractCreatedContract, eth.contractCode
            WHERE contractHash=hash
            AND hasCreateOpcode=1
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        insert_set = []
        while result != None:
            nonce = 0
            num_contracts_to_check_after_last_one_found = 500
            max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
            while nonce < max_nonce_to_check:
                possible_address = Web3.toChecksumAddress(eth_util.calculate_contract_address(result[0], nonce))
                code = w3.eth.getCode(possible_address).hex()
                if code != "0x": # found code
                    max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
                else: # check for non-zero balance for possible future nonce
                    balance = w3.eth.getBalance(possible_address)
                    if balance != 0:
                        print("Parent: {}, New Nonce: {}, New Address: {}, Balance: {}".format(result[0], nonce, possible_address, balance), flush=True)
                        max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
                nonce += 1
            result = c.fetchone()
        offset += batch_size

def run_query(ipc_path, db, generation):
    provider = Web3.IPCProvider(ipc_path, timeout=60)
    w3 = Web3(provider)
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        if generation == 0:
            query = f"""
                SELECT contract.address, IFNULL(MAX(nonceUsed), -1), contract.origin
                FROM contractCode
                JOIN contract
                ON hasCreateOpcode = 1
                AND contractHash = hash
                LEFT OUTER JOIN contractCreatedContract
                ON contract.address = contractCreatedContract.creatorAddress
                GROUP BY contract.address, contract.origin
                LIMIT {batch_size}
                OFFSET {offset};
                """
        else:
            query = f"""
                SELECT parent.address, IFNULL(MAX(child.nonceUsed), -1), parent.origin
                FROM contractCode
                JOIN contractCreatedContract parent
                ON hasCreateOpcode = 1
                AND contractHash = hash
                AND generation = {generation}
                LEFT OUTER JOIN contractCreatedContract child
                ON parent.address = child.creatorAddress
                GROUP BY parent.address, parent.origin
                LIMIT {batch_size}
                OFFSET {offset};
                """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        insert_set = []
        while result != None:
            nonce = result[1] + 1
            origin = result[2]
            num_contracts_to_check_after_last_one_found = 500
            max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
            while nonce < max_nonce_to_check:
                possible_address = Web3.toChecksumAddress(eth_util.calculate_contract_address(result[0], nonce))
                code = w3.eth.getCode(possible_address).hex()
                if code != "0x": # found higher nonce
                    insert_set.append(
                        (result[0], possible_address.lower(), nonce, code, origin)
                    )
                    max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
                else: # check for non-zero balance for possible future nonce
                    balance = w3.eth.getBalance(possible_address)
                    if balance != 0:
                        print("Parent: {}, Max Nonce: {}, New Nonce: {}, New Address: {}, Balance: {}".format(result[0], result[1], nonce, possible_address, balance), flush=True)
                        max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
                nonce += 1
            result = c.fetchone()
        for entry in insert_set:
            insert_into_db(db, generation, *entry)
        offset += batch_size

def insert_into_db(db, parent_generation, parent_addr, new_addr, nonce, code, origin):
    c = db.cursor()
    codeHash = eth_util.calculate_code_hash(code)
    opcodes = eth_util.bytecode_to_opcodes(code)
    c.execute("""INSERT INTO contractCode (hash, code, hasCreateOpcode, occurrences)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE occurrences=occurrences+1;""", (codeHash, code, ("CREATE" in opcodes), 1))
    c.execute("""INSERT INTO contractCreatedContract (address, contractHash, creatorAddress, nonceUsed, generation, origin)
        VALUES (%s, %s, %s, %s, %s, %s);""", (new_addr, codeHash, parent_addr, nonce, parent_generation+1, origin))
    db.commit()


def is_generation_empty(db, generation):
    if generation == 0:
        return False
    c = db.cursor()
    query = f"""
        SELECT count(*)
        FROM contractCreatedContract
        WHERE generation = {generation};
        """
    c.execute(query)
    result = c.fetchone()
    return result[0] == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inserts new contract-created SCs into the DB if there is now a higher nonce. Also finds contracts that are not yet created, but have money in them nevertheless')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)

    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")

    generation = 0
    while not is_generation_empty(db, generation):
        run_query(uri.path, db, generation)
        generation += 1
    # run_query_without_update(uri.path, db)
