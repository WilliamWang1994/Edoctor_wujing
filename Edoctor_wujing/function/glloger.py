#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import logging

class Logger():
    def __init__(self,logger,level=logging.ERROR):
        # 创建一个logger
        # level logging.WARNING NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(level)

        #显示在屏幕上
        ch = logging.StreamHandler()
        ch.setLevel(level)

        #定义输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # 给logger添加handler
        # self.logger.addHandler(fh)
        #如果有handers就不再添加了，不然会一直增加
        if not self.logger.hasHandlers():
            self.logger.addHandler(ch)
    def getlog(self):
        return self.logger

if __name__ == '__main__':
    pass

