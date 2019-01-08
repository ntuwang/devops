import pymysql
from pymysql.cursors import DictCursor


class MysqlConn:
    def __init__(self, host_ip, port_num, db_name, db_user, db_pass, conn=0,cursorclass=None):
        if not cursorclass:
            self.connection = pymysql.connect(host=host_ip, port=port_num, user=db_user, passwd=db_pass, db=db_name, charset='utf8')
        else:
            self.connection = pymysql.connect(host=host_ip, port=port_num, user=db_user, passwd=db_pass, db=db_name,
                                              charset='utf8',cursorclass=DictCursor)
        self.cursor = self.connection.cursor()
        self.conn = conn

    def __iter__(self):
        for item in self.cursor:
            yield item

    def __enter__(self):
        if self.conn:
            return self.connection
        else:
            return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


if __name__ == '__main__':
    pass