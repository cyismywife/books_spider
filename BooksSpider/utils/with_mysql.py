import time
import pymysql
from pymysql.cursors import DictCursor, SSDictCursor
import traceback
import pandas as pd
import datetime


class MySQLContextManager:
    """实现上下文管理器"""
    def __init__(self, host="localhost", port=3306, user="root", password="123456", database=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def __enter__(self):
        """
        上文管理器 返回的结果 会被赋给as 关键字之后的变量
        :return: cursor
        """
        try:
            self.db_conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                           database=self.database, charset="utf8")
            self.cursor = self.db_conn.cursor()
            return self.cursor
        except Exception as e:
            traceback.print_exc()
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        下文管理器 选择性地处理包装代码块中出现的异常
        :param exc_type: 异常类型 默认为 None,发生异常,参数被填充
        :param exc_val: 异常实例 默认为 None,发生异常,参数被填充
        :param exc_tb: 异常回溯 默认为 None,发生异常,参数被填充
        :return:
        """
        try:
            if exc_type:
                self.db_conn.rollback()
                # 返回False 传播异常
                # 返回True 终止异常 不要这么做
                # 抛出不同的异常 代替 原有异常
                return False
            else:
                self.db_conn.commit()
        except Exception as e:
            raise e
        finally:
            self.cursor.close()
            self.db_conn.close()