#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import datetime

import eth_util

def match_verified_sourcecode(db):
    for tablename in ["contract", "contractCreatedContract"]:
        c = db.cursor()
        query = f"""
            SELECT id, contractHash
            FROM verifiedContracts v, {tablename} c
            WHERE v.address = c.address
            AND network = origin
            AND compiler <> "";
            """
        c.execute(query)
        result = c.fetchone()
        while result != None:
            update_db(db, result[0], result[1])
            result = c.fetchone()

def update_db(db, v_id, hash):
    c = db.cursor()
    query = f"""
        UPDATE contractCode
        SET verifiedSourceCodeID={v_id}
        WHERE hash="{hash}";"""
    c.execute(query)
    db.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to set the `verifiedSourceCodeID` field in the contractCode table')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    match_verified_sourcecode(db)
