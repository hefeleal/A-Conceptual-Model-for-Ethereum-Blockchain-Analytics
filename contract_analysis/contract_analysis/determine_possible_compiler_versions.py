#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import datetime

import eth_util

def determine_possible_compiler_versions(db, complete_compiler_list):
    c = db.cursor()
    query = f"""
        SELECT hash, code, minCompilerVersion, maxCompilerVersion
        FROM contractCode;
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        possible_compiler_list1 = compare_timestamp(db, result[0], complete_compiler_list)
        possible_compiler_list2 = compare_header(db, result[1], complete_compiler_list)
        min_compiler1, max_compiler1 = eth_util.get_min_max_versions([x[0] for x in possible_compiler_list1])
        min_compiler2, max_compiler2 = eth_util.get_min_max_versions([x[0] for x in possible_compiler_list2])

        # Example: if list1 = [0.4.5, 0.4.6, 0.4.7, 0.4.8]
        #         and list2 = [0.4.7, 0.4.8, 0.4.9, 0.4.10]
        # then min_compiler is 0.4.7 because list2 is more restrictive here
        # and max_compiler is 0.4.8 because list1 is more restrictive here
        if eth_util.compare_versions(min_compiler1, min_compiler2) < 0:
            min_compiler = min_compiler2
        else:
            min_compiler = min_compiler1
        if eth_util.compare_versions(max_compiler1, max_compiler2) < 0:
            max_compiler = max_compiler1
        else:
            max_compiler = max_compiler2

        # if there is already a higher minCompilerVersion or a lower maxCompilerVersion
        # in the database, take that one
        if result[2] != None and eth_util.compare_versions(min_compiler, result[2]) < 0:
            min_compiler = result[2]
        if result[3] != None and  eth_util.compare_versions(result[3], max_compiler) < 0:
            max_compiler = result[3]
        update_db(db, result[0], min_compiler, max_compiler)
        result = c.fetchone()

# the header of the bytecode contains information that can be relevant to narrow down
# the compiler version that was used to compile the contract
def compare_header(db, bytecode, complete_compiler_list):
    if bytecode[:2] == "0x":
        netto_bytecode = bytecode[2:]
    else:
        netto_bytecode = bytecode
    if netto_bytecode[:8] == "60806040": # >= 0.4.22
        return [x for x in complete_compiler_list if eth_util.compare_versions(x[0], "0.4.22") >= 0]
    # there are also other possible headers (we have 11.5% false negatives for the verifiedContracts,
    # i.e. a contract is between 0.4.18 and 0.4.21, but the header is different), but here only the
    # false positives are relevant because if the header is not matched, we assume all compiler versions
    # False positives are at 0.6%
    elif netto_bytecode[:14] == "60606040526004": # >= 0.4.18 and < 0.4.22
        return [x for x in complete_compiler_list if eth_util.compare_versions(x[0], "0.4.18") >= 0
            and eth_util.compare_versions(x[0], "0.4.22") < 0]
    elif netto_bytecode[:12] == "606060405263": # >= 0.4.7 and < 0.4.18 (only with optimizations on,
        # that is why there are so many false negatives. But only 0.006% false positives)
        return [x for x in complete_compiler_list if eth_util.compare_versions(x[0], "0.4.7") >= 0
            and eth_util.compare_versions(x[0], "0.4.18") < 0]
    elif netto_bytecode[:12] == "606060405236" or netto_bytecode[:12] == "60606040525b": # < 0.4.18
        return [x for x in complete_compiler_list if eth_util.compare_versions(x[0], "0.4.18") < 0]

    return complete_compiler_list

# if a contract was created before a compiler version was released,
# that compiler version definitely was not used
# but also consider one version higher than the latest one released
# because a nightly version could have been used as well!
def compare_timestamp(db, hash, complete_compiler_list):
    c = db.cursor()
    query = f"""
            SELECT min(b.timestamp)
            FROM contract c, contractTransaction t, block b
            WHERE c.contractHash = "{hash}"
            AND c.transactionHash = t.hash
            AND t.blockNumber = b.blockNumber;
        """
    c.execute(query)
    result = c.fetchone()
    if result != None and result[0] != None:
        i = 0
        ret_list = [complete_compiler_list[0]]
        while i < len(complete_compiler_list)-1 and complete_compiler_list[i][1] <= result[0]:
            i += 1
            ret_list.append(complete_compiler_list[i])
        return ret_list
    else: # it is a contract-created-contract
        query = f"""
            SELECT min(b.timestamp)
            FROM contractCreatedContract cc, contract c, contractTransaction t, block b
            WHERE cc.contractHash = "{hash}"
            AND cc.creatorAddress = c.address
            AND c.transactionHash = t.hash
            AND t.blockNumber = b.blockNumber;
        """
        c.execute(query)
        result = c.fetchone()
        if result != None and result[0] != None:
            i = 0
            ret_list = [complete_compiler_list[0]]
            while i < len(complete_compiler_list)-1 and complete_compiler_list[i][1] <= result[0]:
                i += 1
                ret_list.append(complete_compiler_list[i])
            return ret_list
        else: # it is a contract-created-contract of generation >= 2
            return complete_compiler_list

def update_db(db, hash, min_compiler, max_compiler):
    if min_compiler == None:
        min_compiler_string = "NULL"
    else:
        min_compiler_string = "\"" + min_compiler + "\""
    if max_compiler == None:
        max_compiler_string = "NULL"
    else:
        max_compiler_string = "\"" + max_compiler + "\""
    c = db.cursor()
    query = f"""
        UPDATE contractCode
        SET minCompilerVersion={min_compiler_string}, maxCompilerVersion={max_compiler_string}
        WHERE hash="{hash}";"""
    c.execute(query)
    db.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Determine a minimum and a maximum compiler version based on certain heuristics')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    complete_compiler_list = eth_util.get_all_compiler_versions(db)
    determine_possible_compiler_versions(db, complete_compiler_list)
