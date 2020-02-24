#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import re
import base64
import collections
import os

import eth_util

# verify the estimated compiler version
def verify_compiler_version(db):
    correct_counter = 0
    total_counter = 0
    correct_occurrences_counter = 0
    total_occurrences_counter = 0
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT minCompilerVersion, maxCompilerVersion, compiler, occurrences, address
            FROM contractCode
            JOIN verifiedContracts
            ON id = verifiedSourceCodeID
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[0] != None and result[1] != None and result[2] != None and result[2] != "":
                c_version = re.findall("v(.*?)[\+-]", result[2], re.S)[0]
                if version_is_in_range(c_version, result[0], result[1]):
                    correct_counter += 1
                    correct_occurrences_counter += result[3]
                # elif not "nightly" in result[2]:
                #     print(result[4], result[0], result[1], c_version, flush=True)
                # else:
                #     print("nightly", result[4], result[0], result[1], c_version, flush=True)
                total_counter += 1
                total_occurrences_counter += result[3]
            result = c.fetchone()
        offset += batch_size
    print("{} of {} contract codes correctly estimate the compiler version ({:.4f}%)".format(correct_counter, total_counter, (correct_counter/total_counter)*100))
    print("{} of {} contracts correctly estimate the compiler version ({:.4f}%)".format(correct_occurrences_counter, total_occurrences_counter, (correct_occurrences_counter/total_occurrences_counter)*100))
    print()

def version_is_in_range(target, min_version, max_version):
    return eth_util.compare_versions(min_version, target) <= 0 and eth_util.compare_versions(target, max_version) <= 0

# verify whether SafeMath was used or not
def verify_safemath_usage(db):
    false_positive_counter = 0
    false_negative_counter = 0
    true_positive_counter = 0
    true_negative_counter = 0
    total_counter = 0
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT isUsingSafeMath, sourcecode, occurrences, address
            FROM contractCode
            JOIN verifiedContracts
            ON id = verifiedSourceCodeID
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[1] != None:
                detected_safemath = result[0] == True
                uses_safemath = contains_safemath_weak(result[1])
                if detected_safemath and not uses_safemath:
                    print(result[3])
                    false_positive_counter += 1
                elif not detected_safemath and uses_safemath:
                    #print(result[3])
                    false_negative_counter += 1
                elif detected_safemath and uses_safemath:
                    true_positive_counter += 1
                elif not detected_safemath and not uses_safemath:
                    true_negative_counter += 1
                total_counter += 1
            result = c.fetchone()
        offset += batch_size
    print("{} true positives ({:.4f}%)".format(true_positive_counter, (true_positive_counter/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter, (true_negative_counter/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter, (false_positive_counter/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter, (false_negative_counter/total_counter)*100))
    print("{} total verified contract codes".format(total_counter))
    print()

# for manual investigation purposes
# only considers true positives and true negatives
def verify_safemath_usage_manually(db, amount, print_contracts=False):
    correct_using_SafeMath_counter = 0
    correct_not_using_SafeMath_counter = 0
    using_SafeMath_list = []
    not_using_SafeMath_list = []
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT isUsingSafeMath, sourcecode, occurrences, address
            FROM contractCode
            JOIN verifiedContracts
            ON id = verifiedSourceCodeID
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[1] != None:
                detected_safemath = result[0] == True
                uses_safemath_weak = contains_safemath_weak(result[1])
                #uses_safemath_strong = contains_safemath_strong(result[1])
                if uses_safemath_weak and len(using_SafeMath_list) < amount:
                    using_SafeMath_list.append({"address": result[3], "code": result[1]})
                    if detected_safemath:
                        correct_using_SafeMath_counter += 1
                elif not uses_safemath_weak and len(not_using_SafeMath_list) < amount:
                    not_using_SafeMath_list.append({"address": result[3], "code": result[1]})
                    if not detected_safemath:
                        correct_not_using_SafeMath_counter += 1
                if len(using_SafeMath_list) == amount and len(not_using_SafeMath_list) == amount:
                    break
            result = c.fetchone()
        if len(using_SafeMath_list) == amount and len(not_using_SafeMath_list) == amount:
            break
        offset += batch_size
    if print_contracts:
        os.makedirs("using_safemath", exist_ok=True)
        for index, c in enumerate(using_SafeMath_list):
            with open("using_safemath/"+str(index).zfill(3)+".txt", "w") as f:
                f.write(c["address"] + "\n" + base64.b64decode(c["code"]).decode("utf-8"))
        os.makedirs("not_using_safemath", exist_ok=True)
        for index, c in enumerate(not_using_SafeMath_list):
            with open("not_using_safemath/"+str(index).zfill(3)+".txt", "w") as f:
                f.write(c["address"] + "\n" + base64.b64decode(c["code"]).decode("utf-8"))

    print("{}/{} correctly detected presence of SafeMath ({:.4f}%)".format(correct_using_SafeMath_counter, amount, (correct_using_SafeMath_counter/amount)*100))
    print("{}/{} correctly detected absence of SafeMath ({:.4f}%)".format(correct_not_using_SafeMath_counter, amount, (correct_not_using_SafeMath_counter/amount)*100))
    print("{}/{} total ({:.4f}%)".format(correct_using_SafeMath_counter+correct_not_using_SafeMath_counter, 2*amount, (correct_using_SafeMath_counter+correct_not_using_SafeMath_counter)/(2*amount)*100))
    print()

# classification used in the paper
def contains_safemath_weak(b64):
    decoded = base64.b64decode(b64.encode()).decode("utf-8")
    return len(re.findall("(library|contract)\s+(SafeMath|SafeMathLib)\s*{", decoded, re.S)) > 0

# classification used in the Master's thesis
def contains_safemath(b64):
    decoded = base64.b64decode(b64.encode()).decode("utf-8")
    return len(re.findall("(library|contract)\s+(SafeMath|SafeMathLib)\s*{", decoded, re.S)) > 0 or len(re.findall("function\s+(add|mul|div|sub|Add|Mul|Div|Sub|safeAdd|safeMul|safeDiv|safeSub)\s*\(", decoded, re.S)) > 0

# other possible classification used while testing
def contains_safemath_strong(b64):
    decoded = base64.b64decode(b64.encode()).decode("utf-8")
    return len(re.findall("(library|contract)\s+(SafeMath|SafeMathLib)\s*{", decoded, re.S)) > 0 or len(re.findall("function\s+(add|mul|div|sub|mod|Add|Mul|Div|Sub|Mod|safeAdd|safeMul|safeDiv|safeSub|safeMod|divide|division|times|divides|minus|plus|safeMultiply|safeIncrement|safeDecrement|subtr|addit|kvcMul)\s*\(", decoded, re.S)) > 0

# extracts Solidity version from base64 source code
def get_sourcecode_version(b64):
    decoded = base64.b64decode(b64.encode()).decode("utf-8")
    without_comments = re.sub("\s*\/\/.*", "", decoded)
    line = re.findall("pragma\s+solidity(.*?);", without_comments, re.S)
    if len(line) == 0:
        return (None, None)
    stripped = re.sub("\s+", "", line[0])
    versions = re.findall("([0-9]\.[0-9]\.[0-9]+)", stripped, re.S)
    if len(versions) > 1:
        return (versions[0], versions[1])
    elif len(versions) > 0:
        return (versions[0], None)
    else:
        return (None, None)

# check that the verified compiler version is compatible with
# the compiler version in the source code
def integrity_check_verified_compiler_version(db):
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT address, compiler, sourcecode, network
            FROM verifiedContracts
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            c_version = re.findall("v(.*?)[\+-]", result[1], re.S)
            if len(c_version) > 0:
                c_version = c_version[0]
                min_sourcecode_version, max_sourcecode_version = get_sourcecode_version(result[2])
                if min_sourcecode_version == None:
                    pass
                    #print("address: {}, compiler version: {}, no sourcecode version".format(result[0], result[1]), flush=True)
                elif eth_util.compare_versions(c_version, min_sourcecode_version) < 0 or (max_sourcecode_version != None and eth_util.compare_versions(max_sourcecode_version, c_version) < 0):
                    print("network: {}, address: {}, compiler version: {}, sourcecode version: {} - {}".format(result[3], result[0], result[1], min_sourcecode_version, max_sourcecode_version), flush=True)
            result = c.fetchone()
        offset += batch_size

# verifies five different compiler header conjectures by printing the respective confusion matrices:
# 1.: header = 0x60806040 => compiler version >= 0.4.22
# 2.: header = 0x60606040526004 => compiler version >= 0.4.18 and compiler version < 0.4.22
# 3.: header = 0x606060405263 => compiler version >= 0.4.7 and compiler version < 0.4.18
# 4.: header = 0x606060405236 => compiler version < 0.4.18
# 5.: header = 0x60606040525b => compiler version < 0.4.18
def verify_compiler_header(db):
    false_positive_counter_22 = 0
    false_negative_counter_22 = 0
    true_positive_counter_22 = 0
    true_negative_counter_22 = 0

    false_positive_counter_18 = 0
    false_negative_counter_18 = 0
    true_positive_counter_18 = 0
    true_negative_counter_18 = 0

    false_positive_counter_7 = 0
    false_negative_counter_7 = 0
    true_positive_counter_7 = 0
    true_negative_counter_7 = 0

    false_positive_counter_18_2 = 0
    false_negative_counter_18_2 = 0
    true_positive_counter_18_2 = 0
    true_negative_counter_18_2 = 0

    false_positive_counter_18_3 = 0
    false_negative_counter_18_3 = 0
    true_positive_counter_18_3 = 0
    true_negative_counter_18_3 = 0
    total_counter = 0

    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT minCompilerVersion, maxCompilerVersion, compiler, code
            FROM contractCode
            JOIN verifiedContracts
            ON id = verifiedSourceCodeID
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)

        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[0] != None and result[1] != None and result[2] != None and result[2] != "":
                c_version = re.findall("v(.*?)[\+-]", result[2], re.S)
                if len(c_version) > 0:
                    c_version = c_version[0]
                    if result[3][:10] == "0x60806040":
                        if eth_util.compare_versions(c_version, "0.4.22") >= 0:
                            true_positive_counter_22 += 1
                        else:
                            false_positive_counter_22 += 1
                    else:
                        if eth_util.compare_versions(c_version, "0.4.22") >= 0:
                            false_negative_counter_22 += 1
                        else:
                            true_negative_counter_22 += 1

                    if result[3][:16] == "0x60606040526004":
                        if eth_util.compare_versions(c_version, "0.4.18") >= 0 and eth_util.compare_versions(c_version, "0.4.22") < 0:
                            true_positive_counter_18 += 1
                        else:
                            false_positive_counter_18 += 1
                    else:
                        if eth_util.compare_versions(c_version, "0.4.18") >= 0 and eth_util.compare_versions(c_version, "0.4.22") < 0:
                            false_negative_counter_18 += 1
                        else:
                            true_negative_counter_18 += 1

                    if result[3][:14] == "0x606060405263":
                        if eth_util.compare_versions(c_version, "0.4.7") >= 0 and eth_util.compare_versions(c_version, "0.4.18") < 0:
                            true_positive_counter_7 += 1
                        else:
                            false_positive_counter_7 += 1
                    else:
                        if eth_util.compare_versions(c_version, "0.4.7") >= 0 and eth_util.compare_versions(c_version, "0.4.18") < 0:
                            false_negative_counter_7 += 1
                        else:
                            true_negative_counter_7 += 1

                    if result[3][:14] == "0x606060405236":
                        if eth_util.compare_versions(c_version, "0.4.18") < 0:
                            true_positive_counter_18_2 += 1
                        else:
                            false_positive_counter_18_2 += 1
                    else:
                        if eth_util.compare_versions(c_version, "0.4.18") < 0:
                            false_negative_counter_18_2 += 1
                        else:
                            true_negative_counter_18_2 += 1

                    if result[3][:14] == "0x60606040525b":
                        if eth_util.compare_versions(c_version, "0.4.18") < 0:
                            true_positive_counter_18_3 += 1
                        else:
                            false_positive_counter_18_3 += 1
                    else:
                        if eth_util.compare_versions(c_version, "0.4.18") < 0:
                            false_negative_counter_18_3 += 1
                        else:
                            true_negative_counter_18_3 += 1
                    total_counter += 1
            result = c.fetchone()
        offset += batch_size

    print("Check 0x60806040 for >= 0.4.22")
    print("{} true positives ({:.4f}%)".format(true_positive_counter_22, (true_positive_counter_22/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter_22, (true_negative_counter_22/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter_22, (false_positive_counter_22/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter_22, (false_negative_counter_22/total_counter)*100))
    print()
    print("Check 0x60606040526004 for >= 0.4.18 and < 0.4.22")
    print("{} true positives ({:.4f}%)".format(true_positive_counter_18, (true_positive_counter_18/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter_18, (true_negative_counter_18/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter_18, (false_positive_counter_18/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter_18, (false_negative_counter_18/total_counter)*100))
    print()
    print("Check 0x606060405263 for >= 0.4.7 and < 0.4.18")
    print("{} true positives ({:.4f}%)".format(true_positive_counter_7, (true_positive_counter_7/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter_7, (true_negative_counter_7/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter_7, (false_positive_counter_7/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter_7, (false_negative_counter_7/total_counter)*100))
    print()
    print("Check 0x606060405236 for < 0.4.18")
    print("{} true positives ({:.4f}%)".format(true_positive_counter_18_2, (true_positive_counter_18_2/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter_18_2, (true_negative_counter_18_2/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter_18_2, (false_positive_counter_18_2/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter_18_2, (false_negative_counter_18_2/total_counter)*100))
    print()
    print("Check 0x60606040525b for < 0.4.18")
    print("{} true positives ({:.4f}%)".format(true_positive_counter_18_3, (true_positive_counter_18_3/total_counter)*100))
    print("{} true negatives ({:.4f}%)".format(true_negative_counter_18_3, (true_negative_counter_18_3/total_counter)*100))
    print("{} false positives ({:.4f}%)".format(false_positive_counter_18_3, (false_positive_counter_18_3/total_counter)*100))
    print("{} false negatives ({:.4f}%)".format(false_negative_counter_18_3, (false_negative_counter_18_3/total_counter)*100))
    print("{} total verified contract codes".format(total_counter))

# prints the compiler versions that were used most often for a provided array
# of bytecode headers
def print_compiler_rankings_for_headers(db, header_strings):
    total_counter = 0
    c_rankings = []
    for h in header_strings:
        c_rankings.append((h, collections.Counter(), 0))
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT minCompilerVersion, maxCompilerVersion, compiler, code
            FROM contractCode
            JOIN verifiedContracts
            ON id = verifiedSourceCodeID
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[0] != None and result[1] != None and result[2] != None and result[2] != "":
                c_version = re.findall("v(.*?)[\+-]", result[2], re.S)
                if len(c_version) > 0:
                    c_version = c_version[0]
                    for ranking in c_rankings:
                        if result[3][:len(ranking[0])] == ranking[0]:
                            ranking[1][c_version] += 1
                    total_counter += 1
            result = c.fetchone()
        offset += batch_size

    for ranking in c_rankings:
        print("Ranking for", ranking[0])
        i = 0
        summed_up = 0
        for r in ranking[1].most_common():
            summed_up += r[1]
            print("{:02}. {} - {} ({:.4}%)".format(i, r[1], r[0], (summed_up/sum(ranking[1].values()))*100))
            i += 1
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to verify the results using verified contracts')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    #verify_compiler_version(db)
    verify_safemath_usage(db)
    #verify_safemath_usage_manually(db, 250, True)
    #verify_compiler_header(db)
    #integrity_check_verified_compiler_version(db)
    #print_compiler_rankings_for_headers(db, ["0x6060604052", "0x606060405236", "0x60606040525b", "0x606060405260", "0x606060405263"])
