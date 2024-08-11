## Scrapy 框架的使用

pyspider 可以快速完成爬虫的编写。不过它可配置化程度不高，异常处理能力有限等，它对于一些反爬程度非常强的网站的爬取显得力不从心。

与之对应的，

Scrapy 功能非常强大，爬取效率高，相关扩展组件多，可配置和可扩展程度非常高，它几乎可以应对所有反爬网站，是目前 Python 中使用最广泛的爬虫框架。

### 1 Scrapy介绍
**Scrapy 是一个基于 Twisted 的异步处理框架**，是纯 Python 实现的爬虫框架，其架构清晰，模块之间的耦合程度低，可扩展性极强，可以灵活完成各种需求。我们只需要定制开发几个模块就可以轻松实现一个爬虫。

![](13-1.jpg)

 **Scrapy 架构**可以分为如下的几个部分。

- Engine，引擎，用来处理整个系统的数据流处理，触发事务，是整个框架的核心。 
- Item，项目，它定义了爬取结果的数据结构，爬取的数据会被赋值成该对象。 
- Scheduler， 调度器，用来接受引擎发过来的请求并加入队列中，并在引擎再次请求的时候提供给引擎。 
- Downloader，下载器，用于下载网页内容，并将网页内容返回给Spider。 
- Spiders，其内定义了爬取的逻辑和网页的解析规则，它主要负责解析响应并生成提取结果和新的请求。 
- Item Pipeline，项目管道，负责处理由Spider从网页中抽取的项目，它的主要任务是清洗、验证和存储数据。 
- Downloader Middlewares，下载器中间件，位于引擎和下载器之间的钩子框架，主要是处理引擎与下载器之间的请求及响应。 
- Spider Middlewares， Spider中间件，位于引擎和Spider之间的钩子框架，主要工作是处理Spider输入的响应和输出的结果及新的请求。

**Scrapy 中的数据流**由引擎控制，其过程如下:

- Engine 首先打开一个网站，找到处理该网站的 Spider 并向该 Spider 请求第一个要爬取的 URL。 
- Engine 从 Spider 中获取到第一个要爬取的 URL 并通过 Scheduler 以 Request 的形式调度。 
- Engine 向 Scheduler 请求下一个要爬取的 URL。 
- Scheduler 返回下一个要爬取的 URL 给 Engine，Engine 将 URL 通过 Downloader Middlewares 转发给 Downloader 下载。 
- 一旦页面下载完毕， Downloader 生成一个该页面的 Response，并将其通过 Downloader Middlewares 发送给 Engine。 
- Engine 从下载器中接收到 Response 并通过 Spider Middlewares 发送给 Spider 处理。 
- Spider 处理 Response 并返回爬取到的 Item 及新的 Request 给 Engine。 
- Engine 将 Spider 返回的 Item 给 Item Pipeline，将新的 Request 给 Scheduler。 
- 重复第二步到最后一步，直到 Scheduler 中没有更多的 Request，Engine 关闭该网站，爬取结束。

通过多个组件的相互协作、不同组件完成工作的不同、组件对异步处理的支持，Scrapy 最大限度地利用了网络带宽，大大提高了数据爬取和处理的效率。

Scrapy 是通过命令行来创建项目的。项目创建之后，项目文件结构如下所示：
```
scrapy.cfg
project/
    __init__.py
    items.py
    pipelines.py
    settings.py
    middlewares.py
    spiders/
        __init__.py
        spider1.py
        spider2.py
        ...
```
- `scrapy.cfg`：它是 Scrapy 项目的配置文件，其内定义了项目的配置文件路径、部署相关信息等内容。
- `items.py`：它定义 Item 数据结构，所有的 Item 的定义都可以放这里。
- `pipelines.py`：它定义 Item Pipeline 的实现，所有的 Item Pipeline 的实现都可以放这里。
- `settings.py`：它定义项目的全局配置。
- `middlewares.py`：它定义 Spider Middlewares 和 Downloader Middlewares 的实现。
- **spiders**：其内包含一个个 Spider 的实现，每个 Spider 都有一个文件。

### 2 Scrapy 入门
> 需要安装好 Scrapy 框架、MongoDB 和 PyMongo 库。

创建Scrapy项目，进入目录 **chapter13** 使用创建命令，如下：

```bash
(base) PS D:\Python\py_files\CrawlSpider\chapter13> scrapy startproject scrapy_tutorial
 ...
New Scrapy project 'scrapy_tutorial', using template directory 'D:\Python\Anaconda\Lib\site-packages\scrapy\templates\project', created in:
    D:\Python\py_files\CrawlSpider\chapter13\scrapy_tutorial

You can start your first spider with:
    cd scrapy_tutorial
    scrapy genspider example example.com
```
`scrapy_tutorial` 文件夹结构如下所示：
```
scrapy.cfg     # Scrapy 部署时的配置文件
scrapy_tutorial         # 项目的模块，引入的时候需要从这里引入
    __init__.py    
    items.py     # Items 的定义，定义爬取的数据结构
    middlewares.py   # Middlewares 的定义，定义爬取时的中间件
    pipelines.py       # Pipelines 的定义，定义数据管道
    settings.py       # 配置文件
    spiders         # 放置 Spiders 的文件夹
        __init__.py
```

**创建 Spider**

Spider 是自己定义的类，Scrapy 用它来从网页里抓取内容，并解析抓取的结果。

不过这个类必须继承 Scrapy 提供的 Spider 类 `scrapy.Spider`，还要定义 Spider 的名称和起始请求，以及怎样处理爬取后的结果的方法。

也可以使用命令行创建一个 Spider。比如要生成 **Quotes** 这个 Spider，可以执行如下命令：

```shell
cd scrapy_tutorial
scrapy genspider quotes quotes.toscrape.com
```
> [第一个参数是 Spider 的名称，第二个参数是网站域名。]

执行完毕之后，`spiders` 文件夹中多了一个 `quotes.py`，它就是刚刚创建的 Spider，内容如下所示：
```python
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        pass
```

这里有三个属性 —— `name、allowed_domains` 和 `start_urls`，还有一个方法 `parse()`。

- `name`，它是每个项目唯一的名字，用来区分不同的 Spider。
- `allowed_domains`，它是允许爬取的域名，如果初始或后续的请求链接不是这个域名下的，则请求链接会被过滤掉。
- `start_urls`，它包含了 Spider 在启动时爬取的 url 列表，初始请求是由它来定义的。
- `parse()`，它是 Spider 的一个方法。默认情况下，被调用时 `start_urls` 里面的链接构成的请求完成下载执行后，返回的响应就会作为唯一的参数传递给这个函数。
   
   该方法负责解析返回的响应、提取数据或者进一步生成要处理的请求。

**创建 Item**