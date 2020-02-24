#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse

import eth_util

def run_query(user, password):
    db = MySQLdb.connect(user=user, passwd=password, db="eth")
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT contractHash, SUM(c)
            FROM (
                SELECT contractHash, COUNT(*) AS c
                FROM contractCreatedContract
                GROUP BY contractHash
                UNION ALL
                SELECT contractHash, COUNT(*) AS c
                FROM contract
                GROUP BY contractHash
            ) AS s
            GROUP BY contractHash
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        update_set = []
        while result != None:
            update_set.append([result[0], result[1]])
            result = c.fetchone()
        for u in update_set:
            c2 = db.cursor()
            query2 = f"""
                UPDATE contractCode
                SET occurrences={u[1]}
                WHERE hash='{u[0]}';"""
            c2.execute(query2)
        db.commit()
        offset += batch_size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='recalculates the occurrences value of eth.contractCode and updates the table')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()

    run_query(args.user, args.password)
