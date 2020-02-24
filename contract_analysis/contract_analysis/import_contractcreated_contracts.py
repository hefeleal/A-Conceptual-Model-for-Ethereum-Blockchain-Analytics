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
    
    generation = 1
    while not is_generation_empty(db, generation):
        run_query_for_generation(db, w3, generation)
        generation += 1

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

def run_query_for_generation(db, w3, generation):
    batch_size = 50000
    offset = 0
    while True:
        c = db.cursor()
        if generation == 0:
            query = f"""
                SELECT address
                FROM contractCode, contract
                WHERE hasCreateOpcode = 1
                AND contractHash = hash
                LIMIT {batch_size}
                OFFSET {offset};
                """
        else:
            query = f"""
                SELECT address
                FROM contractCode, contractCreatedContract
                WHERE hasCreateOpcode = 1
                AND contractHash = hash
                AND generation = {generation}
                LIMIT {batch_size}
                OFFSET {offset};
                """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        insert_set = []
        while result != None:
            nonce = 0 # check nonce 0 in any case
            possible_address = eth_util.calculate_contract_address(result[0], nonce)
            code = w3.eth.getCode(Web3.toChecksumAddress(possible_address)).hex()
            if code != "0x":
                # print(result[0], possible_address, nonce, code)
                insert_set.append(
                    (result[0], possible_address, nonce, code)
                )
            # if we found code behind contract with nonce x, also check nonces
            # until x+num_contracts_to_check_after_last_one_found. If a new one
            # is found in that set, reset the counter
            num_contracts_to_check_after_last_one_found = 500
            max_nonce_to_check = num_contracts_to_check_after_last_one_found
            while nonce < max_nonce_to_check:
                nonce += 1
                possible_address = eth_util.calculate_contract_address(result[0], nonce)
                code = w3.eth.getCode(Web3.toChecksumAddress(possible_address)).hex()
                if code != "0x":
                    # print(result[0], possible_address, nonce, code)
                    insert_set.append(
                        (result[0], possible_address, nonce, code)
                    )
                    max_nonce_to_check = nonce + num_contracts_to_check_after_last_one_found
            result = c.fetchone()
        for entry in insert_set:
            insert_into_db(db, generation, *entry)
        offset += batch_size

def insert_into_db(db, parent_generation, parent_addr, new_addr, nonce, code):
    c = db.cursor()
    codeHash = eth_util.calculate_code_hash(code)
    opcodes = eth_util.bytecode_to_opcodes(code)
    c.execute("""INSERT INTO contractCode (hash, code, hasCreateOpcode, occurrences)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE occurrences=occurrences+1;""", (codeHash, code, ("CREATE" in opcodes), 1))
    c.execute("""INSERT INTO contractCreatedContract (address, contractHash, creatorAddress, nonceUsed, generation, origin)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE address=address;""", (new_addr, codeHash, parent_addr, nonce, parent_generation+1, 0))
    db.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import contract-created contracts into the DB. Faster than update_max_nonce.py, but only works on an empty contractCreatedContract table')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--geth-uri', type=str, dest='geth_uri', default=None, help='Geth URI')
    args = parser.parse_args()

    uri = urlparse(args.geth_uri)
    run_query(uri.path, args.user, args.password)
