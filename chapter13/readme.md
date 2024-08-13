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

#### 创建Scrapy项目

进入目录 **chapter13** 使用创建命令，如下：

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

#### 创建 Spider

Spider 是自己定义的类，Scrapy 用它来从网页里抓取内容，并解析抓取的结果。

不过这个类必须继承 Scrapy 提供的 Spider 类 `scrapy.Spider`，还要定义 Spider 的名称和起始请求，以及怎样处理爬取后的结果的方法。

也可以使用命令行创建一个 Spider。比如要生成 **quotes** 这个 Spider，可以执行如下命令：

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

#### 创建 Item

Item 是保存爬取数据的容器，它的使用方法和字典类似。Item 比字典多了额外的保护机制，可以避免拼写错误或者定义字段错误。

创建 Item 需要继承 `scrapy.Item` 类，并且定义类型为 `scrapy.Field` 的字段。

观察目标网站，我们可以获取到的内容有 `text、author、tags`。

![](13-2.png)

定义 Item，在 `items.py` 添加代码：
```python
class QuoteItem(scrapy.Item):
    """
    QuotesSpider

    host: quotes.toscrape.com
    """
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
```

#### 解析 Response

> spider中，`parse()` 方法的参数 `response` 是` start_urls` 里面的链接爬取后的结果。
> 
> 所以在 `parse()` 方法中，可以直接对 `response` 变量包含的内容进行解析，比如浏览请求结果的网页源代码，
> 
> 或者进一步分析源代码内容，或者找出结果中的链接而得到下一个请求。

网页结构如上图所示。
> 每一页都有多个 `class` 为 quote 的区块，每个区块内都包含 `text、author、tags`。
> 
> 那么可以先找出所有的 *quote*，然后提取每一个 *quote* 中的内容。

提取的方式可以是 CSS 选择器或 XPath 选择器。这里使用 **CSS 选择器**进行选择，`parse()` 方法的改写如下所示：
```python
def parse(self, response):
    quotes = response.css('.quote')
    for quote in quotes:
        text = quote.css('.text::text').extract_first()
        author = quote.css('.author::text').extract_first()
        tags = quote.css('.tags .tag::text').extract()
```

#### 使用 Item

上文定义了 Item，在声明的时候需要实例化。然后依次用刚才解析的结果赋值 Item 的每一个字段，最后将 Item 返回即可。

`spiders/quotes.py` 的 `parse()` 修改如下：
```python
from scrapy_tutorial.items import QuoteItem

def parse(self, response):
    quotes = response.css('.quote')
    for quote in quotes:
        quote_item = QuoteItem()
        quote_item['text'] = quote.css('.text::text').extract_first()
        quote_item['author'] = quote.css('.author::text').extract_first()
        quote_item['tags'] = quote.css('.tags .tag::text').extract()
        yield quote_item
```

#### 后续 Request

上面的操作实现了从初始页面抓取内容。

下一页的内容抓取需要从当前页面中找到信息来生成下一个请求，然后在下一个请求的页面里找到信息再构造再下一个请求。

将刚才的页面拉到最底部，如图所示：

![](13-3.png)

> 实际上全链接就是：http://quotes.toscrape.com/page/2 
> 
> 通过这个链接就可以构造下一个请求。

构造请求时需要用到 `scrapy.Request`。这里我们传递两个参数:
- `url`：它是请求链接。 
- `callback`：它是回调函数。当指定了该回调函数的请求完成之后，获取到响应，引擎会将该响应作为参数传递给这个回调函数。回调函数进行解析或生成下一个请求，回调函数如上文的 `parse()` 所示。

> 由于 `parse()` 就是解析 `text、author、tags` 的方法，而下一页的结构和刚才已经解析的页面结构是一样的，所以可以再次使用 `parse()` 方法来做页面解析。

接下来要做的就是利用选择器得到下一页链接并生成请求，在 `parse()` 方法后追加如下的代码：

```python
next = response.css('.pager .next a::attr(href)').extract_first()
url = response.urljoin(next)
yield scrapy.Request(url=url, callback=self.parse)
```

> 第一句代码首先通过 CSS 选择器获取下一个页面的链接，即要获取 `a` 超链接中的 `href` 属性。这里用到了`::attr(href)` 操作。然后再调用 `extract_first()` 方法获取内容。
>
> 第二句代码调用了 `urljoin()` 方法，将相对 URL 构造成一个绝对的 URL。例如，获取到的下一页地址是 `/page/2`，`urljoin()` 方法处理后得到的结果就是：https://quotes.toscrape.com/page/2/
>
> 第三句代码通过 `url` 和 `callback` 变量构造了一个新的请求，回调函数 `callback` 依然使用 `parse()` 方法。这个请求完成后，响应会重新经过 `parse` 方法处理，得到第二页的解析结果，然后生成第二页的下一页，也就是第三页的请求。这样爬虫就进入了一个循环，直到最后一页。

#### 运行爬虫

接下来，进入`scrapy_tutorial`目录，运行命令：`scrapy crawl quotes` 

```shell
(base) PS D:\Python\py_files\CrawlSpider\chapter13\scrapy_tutorial> scrapy crawl quotes
D:\Python\Anaconda\lib\site-packages\scrapy\utils\_compression.py:15: ScrapyDeprecationWarning: You have brotlipy installed, and Scrapy will use it, but Scrapy support for brotlipy is deprecated and wi
ll stop working in a future version of Scrapy. brotlipy itself is deprecated, it has been superseded by brotlicffi (not currently supported by Scrapy). Please, uninstall brotlipy and install brotli instead. brotlipy has the same import name as brotli, so keeping both installed is strongly discouraged.
  warn(
2024-08-13 22:36:34 [scrapy.utils.log] INFO: Scrapy 2.11.2 started (bot: scrapy_tutorial)
2024-08-13 22:36:34 [scrapy.utils.log] INFO: Versions: lxml 4.6.3.0, libxml2 2.9.12, cssselect 1.2.0, parsel 1.9.1, w3lib 2.2.1, Twisted 24.3.0, Python 3.9.7 (default, Sep 16 2021, 16:59:28) [MSC v.1916 64 bit (AMD64)], pyOpenSSL 24.2.1 (OpenSSL 3.3.1 4 Jun 2024), cryptography 43.0.0, Platform Windows-10-10.0.22000-SP0
2024-08-13 22:36:34 [scrapy.addons] INFO: Enabled addons:
[]
2024-08-13 22:36:34 [asyncio] DEBUG: Using selector: SelectSelector
2024-08-13 22:36:35 [scrapy.crawler] INFO: Overridden settings:
{'BOT_NAME': 'scrapy_tutorial',
 'FEED_EXPORT_ENCODING': 'utf-8',
 'NEWSPIDER_MODULE': 'scrapy_tutorial.spiders',
 'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
 'ROBOTSTXT_OBEY': True,
 'SPIDER_MODULES': ['scrapy_tutorial.spiders'],
 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'}
2024-08-13 22:36:36 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware',
 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware',
 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware',
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware',
 'scrapy.downloadermiddlewares.retry.RetryMiddleware',
 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware',
 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware',
 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware',
 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware',
 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware',
 'scrapy.downloadermiddlewares.stats.DownloaderStats']
2024-08-13 22:36:36 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
2024-08-13 22:36:36 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2024-08-13 22:36:36 [scrapy.core.engine] INFO: Spider opened
2024-08-13 22:36:36 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2024-08-13 22:36:36 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6023
2024-08-13 22:36:39 [scrapy.core.engine] DEBUG: Crawled (404) <GET https://quotes.toscrape.com/robots.txt> (referer: None)
2024-08-13 22:36:40 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://quotes.toscrape.com> (referer: None)
2024-08-13 22:36:40 [scrapy.core.scraper] DEBUG: Scraped from <200 https://quotes.toscrape.com>
{'author': 'Albert Einstein',
 'tags': ['change', 'deep-thoughts', 'thinking', 'world'],
 'text': '“The world as we have created it is a process of our thinking. It '
         'cannot be changed without changing our thinking.”'}
         
......

2024-08-13 22:36:45 [scrapy.core.scraper] DEBUG: Scraped from <200 https://quotes.toscrape.com/page/10/>
{'author': 'George R.R. Martin',
 'tags': ['books', 'mind'],
 'text': '“... a mind needs books as a sword needs a whetstone, if it is to '
         'keep its edge.”'}
2024-08-13 22:36:45 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET https://quotes.toscrape.com/page/10/> - no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)  
2024-08-13 22:36:45 [scrapy.core.engine] INFO: Closing spider (finished)
2024-08-13 22:36:45 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 2944,
 'downloader/request_count': 11,
 'downloader/request_method_count/GET': 11,
 'downloader/response_bytes': 22893,
 'downloader/response_count': 11,
 'downloader/response_status_count/200': 10,
 'downloader/response_status_count/404': 1,
 'dupefilter/filtered': 1,
 'elapsed_time_seconds': 9.395826,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2024, 8, 13, 14, 36, 45, 603455, tzinfo=datetime.timezone.utc),
 'httpcompression/response_bytes': 108778,
 'httpcompression/response_count': 11,
 'item_scraped_count': 100,
 'log_count/DEBUG': 115,
 'log_count/INFO': 10,
 'request_depth_max': 10,
 'response_received_count': 11,
 'robotstxt/request_count': 1,
 'robotstxt/response_count': 1,
 'robotstxt/response_status_count/404': 1,
 'scheduler/dequeued': 10,
 'scheduler/dequeued/memory': 10,
 'scheduler/enqueued': 10,
 'scheduler/enqueued/memory': 10,
 'start_time': datetime.datetime(2024, 8, 13, 14, 36, 36, 207629, tzinfo=datetime.timezone.utc)}
2024-08-13 22:36:45 [scrapy.core.engine] INFO: Spider closed (finished)
```

> 首先，Scrapy 输出了当前的版本号以及正在启动的项目名称。接着输出了当前 `settings.py` 中一些重写后的配置。
> 
> 然后输出了当前所应用的 `Middlewares` 和 `Pipelines`。`Middlewares` 默认是启用的，可以在 `settings.py` 中修改。`Pipelines` 默认是空，同样也可以在 `settings.py` 中配置。
> 
> 接下来就是输出各个页面的抓取结果了，可以看到爬虫一边解析，一边翻页，直至将所有内容抓取完毕，然后终止。 
> 
> 最后，Scrapy 输出了整个抓取过程的统计信息，如请求的字节数、请求次数、响应次数、完成原因等。 

