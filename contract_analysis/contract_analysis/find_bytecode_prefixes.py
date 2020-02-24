#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import collections

import eth_util

# -only smart contracts that start with 0x60 are of interest. There are only 30000 SCs starting with 0x58.
#  - Big jumps:
#   005. 6411684 - 6060604052
#   006. 3477162 - 606060405236 ->
#   011. 1263082 - 60606040525b (>= 0.4.8 and <= 0.4.16?)
#   016. 0852769 - 606060405260 ->
#   017. 0802071 - 606060405263 (>= 0.4.7 and <= 0.4.17 with optimizations on!)

#   009. 3413123 - 606060405236156100
#   010. 1648224 - 60606040523615610049
#   026. 0395578 - 60606040523615610055
#   036. 0321818 - 60606040523615610088
#   037. 0308123 - 60606040523615610046
#   038. 0140738 - 6060604052361561004a
#   041. 0126791 - 6060604052361561003f
#   044. 0089317 - 60606040523615610054

#   016. 0852769 - 606060405260
#   022. 0640626 - 60606040526004 (>= 0.4.18 and < 0.4.22)
#   039. 0138353 - 60606040526000
#   045. 0066345 - 606060405260e0

def find_bytecode_prefixes(db):
    batch_size = 10000
    offset = 0
    max_prefix_len = 10
    prefixes = collections.Counter()
    while True:
        c = db.cursor()
        query = f"""
            SELECT code, occurrences, hash
            FROM contractCode
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            # don't use prefixes that are longer than the bytecode itself
            for i in range(2, min(int(len(result[0])/2+1), max_prefix_len+2)):
               prefixes[result[0][2:(2*i)]] += result[1]
            result = c.fetchone()
        offset += batch_size
    i = 1
    for p in prefixes.most_common():
        print("{:03}. {:07} - {}".format(i, p[1], p[0]))
        i += 1
        if i > 200:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to find the most common bytecode prefixes')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    find_bytecode_prefixes(db)
