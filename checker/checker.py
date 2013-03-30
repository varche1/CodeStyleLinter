# -*- encoding: utf-8 -*-

import datetime
import os
import re
import subprocess
import threading
import time
try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser
from os.path import expanduser

import abc

class CheckError():
    """Класс представления ошибки"""
    def __init__(self, *args, **kwargs):
        self.line_start = None
        self.line_end = None
        self.column_start = None
        self.column_end = None
        self.message = None
        self.severity = None
        self.type = None


        # Линия начала ошибки
        if 'line_start' in kwargs.keys():
            self.line_start = kwargs['line_start']

        # Линия конца ошибки
        if 'line_end' in kwargs.keys():
            self.line_end = kwargs['line_end']

        # Колонка начала ошибки
        if 'column_start' in kwargs.keys():
            self.column_start = kwargs['column_start']

        # Колонка конца ошибки
        if 'column_end' in kwargs.keys():
            self.column_end = kwargs['column_end']

        # Сообщение ошибки
        if 'severity' in kwargs.keys():
            self.severity = kwargs['severity']

        # Суровость ошибки
        if 'message' in kwargs.keys():
            self.message = kwargs['message']

        # Тип ошибки
        if 'type' in kwargs.keys():
            self.type = kwargs['type']


    def get_line(self):
        return self.line

    def get_message(self):
        data = self.message

        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            """"""
            # ошибка декодирования в лог

        return HTMLParser().unescape(data)

class BaseChecker:
    __metaclass__ = abc.ABCMeta

    def save_content(self, content):
        file_name = "temp.{ext}".format(ext=self.file_extension)
        with open(file_name, "a+") as f:
            f.write(content)
            # os.remove(file_name)

    def shell_out(self, cmd):
        data = None
        info = None
        home = expanduser("~")

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=info, cwd=home)

        if proc.stdout:
            data = proc.communicate()[0]
            self.parse_report(data)

        return data
    
    @abc.abstractmethod
    def check(self, content):
        """Метод реализующий получение ответа от низкоуровнего проверяльщика"""
        return

    @abc.abstractmethod
    def parse_report(self, report_data):
        """Метод реализующий парсинг ответа от низкоуровнего проверяльщика"""
        return

class CheckPhp(BaseChecker):
    def __init__(self):
        self.file_extension = 'php'
        self.errors_list = []

    def check(self, content):
        """
        """
        self.save_content(content)
        self.shell_out(['phpcs', '--report=checkstyle', '/home/www/checker.codestyle.dev.webpp.ru/docs/codestyle/checker/temp.php'])

    def parse_report(self, report_data):
        expression = r'.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source="(?P<type>.*)"'
        lines = re.finditer(expression, report_data)

        for line in lines:
            args = {
                'line_start':   line.group('line'),
                'line_end':     line.group('line'),
                'column_start': line.group('column'),
                'column_end':   line.group('column'),
                'message':      line.group('message'),
                'severity':     line.group('severity'),
                'type':         line.group('type')
            }

            error = CheckError(**args)
            self.errors_list.append(error)

# print os.getcwd()

if __name__ == "__main__":
    content = open('/home/www/checker.codestyle.dev.webpp.ru/docs/codestyle/examples/phpcs.php', 'r').read()
    checker = CheckPhp()
    checker.check(content)
    print len(checker.errors_list)