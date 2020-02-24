#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import collections

import eth_util

erc20 = (["totalSupply()",
    "balanceOf(address)",
    "transfer(address,uint256)",
    "transferFrom(address,address,uint256)",
    "approve(address,uint256)",
    "allowance(address,address)"],
    ["Transfer(address,address,uint256)",
    "Approval(address,address,uint256)"])

erc721 = (["balanceOf(address)",
    "ownerOf(uint256)",
    "safeTransferFrom(address,address,uint256,bytes)",
    "safeTransferFrom(address,address,uint256)",
    "transferFrom(address,address,uint256)",
    "approve(address,uint256)",
    "setApprovalForAll(address,bool)",
    "getApproved(uint256)",
    "isApprovedForAll(address,address)"],
    ["Transfer(address,address,uint256)",
    "Approval(address,address,uint256)",
    "ApprovalForAll(address,address,bool)"])

def run_query(db, sig_tuple):
    function_sig_list = create_sig_list(sig_tuple[0], eth_util.calculate_function_signature_hash)
    event_sig_list = create_sig_list(sig_tuple[1], eth_util.calculate_event_signature_hash)
    total_occurrences = 0
    total_contract_codes = 0
    blocknumber_dict = dict()
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT code, hash, occurrences
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
            found_functions = [False] * len(function_sig_list)
            found_events = [False] * len(event_sig_list)
            for o in opcodes:
                if o[:6] == "PUSH4 " and o[6:] in function_sig_list:
                    found_functions[function_sig_list.index(o[6:])] = True
                elif o[:7] == "PUSH32 " and o[7:] in event_sig_list:
                    found_events[event_sig_list.index(o[7:])] = True
            # print("\"{}\",".format(sum(found_functions) + sum(found_events)), end="")
            if all(found_functions) and all(found_events):
                #print("{} ({} occurrences)".format(result[1], result[2]), flush=True)
                total_occurrences += result[2]
                total_contract_codes += 1
                blocknumber_dict = get_statistics_over_blocknumber(db, result[1], blocknumber_dict)
            result = c.fetchone()
        offset += batch_size
    print("Total occurrences:", total_occurrences)
    print("Total contract codes:", total_contract_codes)
    print("Total occurrences in user-created contracts:", sum(blocknumber_dict.values()))
    # current_batch_limit = 0
    # total_sum = 0
    # print("Sum of contracts:")
    # for i in sorted(blocknumber_dict):
    #     while i > current_batch_limit:
    #         print("({}, {})".format(current_batch_limit, total_sum))
    #         current_batch_limit += 10000
    #     total_sum += blocknumber_dict[i]
    # print("({}, {})".format(current_batch_limit, total_sum))

    print("Distribution for every 100000 blocks:")
    current_batch_limit = 0
    current_batch_sum = 0
    for i in sorted(blocknumber_dict):
        if i <= current_batch_limit:
            current_batch_sum += blocknumber_dict[i]
        else:
            while i > current_batch_limit:
                print("({}, {})".format(current_batch_limit, current_batch_sum))
                current_batch_limit += 100000
            current_batch_sum = blocknumber_dict[i]
    print("({}, {})".format(current_batch_limit, current_batch_sum))

# writes to a dict containing a mapping of blocknumber->amount of found contracts with the required properties.
# For one specific hash of a contract code, this function updates the dict.
def get_statistics_over_blocknumber(db, hash, dct):
    c = db.cursor()
    query = f"""
        SELECT blockNumber
        FROM contract, contractTransaction
        WHERE transactionHash=hash
        AND contractHash="{hash}";
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        if result[0] in dct:
            dct[result[0]] += 1
        else:
            dct[result[0]] = 1
        result = c.fetchone()
    return dct

def create_sig_list(name_list, sig_function):
    return list(map(lambda x: sig_function(x), filter(lambda y: y != "", name_list)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print all contract hashes whose code contains certain functions and/or events')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--functions', type=str, dest='functions', default='', help='Function names to search, separated by semicolons')
    parser.add_argument('--events', type=str, dest='events', default='', help='Event names to search, separated by semicolons')
    args = parser.parse_args()

    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    if args.functions != "" or args.events != "":
        run_query(db, (args.functions.split(";"), args.events.split(";")))
    else:
        run_query(db, erc20)