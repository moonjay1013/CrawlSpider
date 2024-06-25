import requests
import selenium
from selenium import webdriver
import aiohttp, aiodns, cchardet
import lxml, bs4
from bs4 import BeautifulSoup  # introduce
import pyquery
import pymysql, pymongo
import flask
from flask import Flask
import tornado.ioloop
import tornado.web

app = Flask(__name__)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([(r"/", MainHandler),
                                    ])


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    print("requests", requests.__version__)
    print("selenium", selenium.__version__)
    # browser = webdriver.Chrome()
    # browser.get('https://www.baidu.com')
    # print(browser.title)
    print("aiohttp", aiohttp.__version__)
    print("aiodns", aiodns.__version__)
    print("cchardet", cchardet.__version__)
    print("lxml", lxml.__version__)
    print("BeautifulSoup", bs4.__version__)
    print("pyquery", "1.4.3")
    print("pymysql", pymysql.__version__)
    print("pymongo", pymongo.__version__)
    print("flask", flask.__version__)
    # flask
    # app.run()

    # Tornado
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
