# coding=utf-8
import os
import sys

import pymysql
import cx_Oracle
import json

from utils.jsonUtil import OracleConverter, MySQLConverter


class MySQL(object):
    def __init__(self, host, port, user, passwd, db=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)

    def query(self, sql, one=False):
        with self.conn.cursor(cursor=pymysql.cursors.DictCursor) as c:
            c.execute(sql)
            if one:
                return self.toJSON(c.fetchone())
            return self.toJSON(c.fetchall())

    def toJSON(self, results):
        return json.loads(
            json.dumps(
                results,
                default=MySQLConverter
            )
        )

    def queryOne(self, sql, one=True):
        return self.query(self)

    def exec(self, sql):
        with self.conn.cursor(cursor=pymysql.cursors.DictCursor) as c:
            c.execute(sql)
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def __del__(self):
        self.close()


class Oracle(object):
    def __init__(self, host, port, user, passwd, db=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        dsnTns = cx_Oracle.makedsn(self.host, self.port, service_name=self.db)
        os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
        self.conn = cx_Oracle.connect(self.user, self.passwd, dsnTns)

    def query(self, sql, one=False):
        with self.conn.cursor() as c:
            c.execute(sql)
            c.rowfactory = self.makeDictFactory(c)
            if one:
                return self.toJSON(c.fetchone())
            return self.toJSON(c.fetchall())

    def queryOne(self, sql, one=True):
        return self.query(self)

    def toJSON(self, results):
        return json.loads(
            json.dumps(
                results,
                default=OracleConverter
            )
        )

    def exec(self, sql):
        with self.conn.cursor() as c:
            c.execute(sql)

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def makeDictFactory(self, cursor):
        columnNames = [d[0] for d in cursor.description]

        def createRow(*args):
            return dict(zip(columnNames, args))

        return createRow

    def __del__(self):
        self.close()


if __name__ == '__main__':
    pass
