"""
抓取猫眼电影排行

目标：
本节中，提取出猫眼电影 TOP100 的电影名称、时间、评分、图片等信息，提取的站点 URL 为 https://www.maoyan.com/board/4，提取的结果会以文件形式保存下来。

页面信息：
每页展示10条电影信息：
<dl class="board-wrapper">
    <dd>...</dd>
    ...
</dl>
------------------
<dd>标签中的详细信息
------------------
<dd>
    <i class="board-index board-index-1">1</i>
    <a href="/films/1200486" title="我不是药神" class="image-link" data-act="boarditem-click" data-val="{movieId:1200486}">
      <img src="//s3.meituan.net/static-prod01/com.sankuai.movie.fe.mywww-files/image/loading_2.e3d934bf.png" alt="" class="poster-default" />
      <img data-src="https://p0.pipi.cn/mmdb/54ecde9a2c9f2a51ba06d67d795a9434b8421.jpg?imageView2/1/w/160/h/220" alt="我不是药神" class="board-img" />
    </a>
    <div class="board-item-main">
      <div class="board-item-content">
        <div class="movie-item-info">
        <p class="name"><a href="/films/1200486" title="我不是药神" data-act="boarditem-click" data-val="{movieId:1200486}">我不是药神</a></p>
        <p class="star">主演：徐峥,王传君,周一围</p>
        <p class="releasetime">上映时间：2018-07-05</p>
        </div>
        <div class="movie-item-number score-num">
          <p class="score"><i class="integer">9.</i><i class="fraction">6</i></p>
        </div>
      </div>
    </div>
</dd>
------------------
将网页滚动到最下方，可以发现有分页的列表
------------------
<div class="pager-main">
    <ul class="list-pager">
        <li class="active"><a class="page_1" href="javascript:void(0);" style="cursor: default">1</a></li>
        <li ><a class="page_2" href="?offset=10">2</a></li>
        <li ><a class="page_3" href="?offset=20">3</a></li>
        <li ><a class="page_4" href="?offset=30">4</a></li>
        <li ><a class="page_5" href="?offset=40">5</a></li>
        <li class="sep">...</li>
        <li ><a class="page_10" href="?offset=90">10</a></li>
        <li>  <a class="page_2" href="?offset=10">下一页</a></li>
    </ul>
</div>

offset 代表偏移量值，如果偏移量为 n，则显示的电影序号就是 n+1 到 n+10，每页显示 10 个。

所以，如果想获取 TOP100 电影，只需要分开请求 10 次，而 10 次的 offset 参数分别设置为 0、10、20…90 即可，

这样获取不同的页面之后，再用正则表达式提取出相关信息，就可以得到 TOP100 的所有电影信息了。
"""

import requests
import re
import json


def get_one_page(url):
    """
    抓取一页的内容（返回网页源代码）
    :param url:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def parse_one_page(html):
    """
    解析网页代码
    排名, img src, 电影名, 出演人员, 上映时间, 评分（整数部分）, 评分（小数部分）
    :param html:
    :return: 生成器生成的 { }
    """
    pattern_str = '<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>.*?</dd>'

    pattern = re.compile(pattern_str, re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {'index': item[0],
               'image': item[1],
               'title': item[2].strip(),
               'actor': item[3].strip()[3:] if len(item[3]) > 3 else '',
               'time': item[4].strip()[5:] if len(item[4]) > 5 else '',
               'score': item[5].strip() + item[6].strip()}


def write_to_file(content):
    """
    将提取的结果写入到一个文本文件中。
    这里通过 JSON 库的 dumps 方法实现字典的序列化，并指定 ensure_ascii 参数为 False，这样可以保证输出结果是中文形式而不是 Unicode 编码。
    :param content:
    :return:
    """
    with open('result.txt', 'a', encoding='utf-8') as f:
        # print(type(json.dumps(content)))
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


if __name__ == '__main__':
    """
    url = 'https://www.maoyan.com/board/4'
    html = get_one_page(url)
    parse_res = parse_one_page(html)
    for _, parse_re in enumerate(parse_res):
        write_to_file(parse_re)
        print(parse_re)
    """

    """
    给这个链接传入 offset 参数，实现其他 90 部电影的爬取，此时添加如下调用即可：
    """
    for i in range(10):
        offset = i * 10
        url = 'https://www.maoyan.com/board/4?offset=' + str(offset)
        html = get_one_page(url)
        parse_res = parse_one_page(html)
        for _, parse_re in enumerate(parse_res):
            write_to_file(parse_re)
            print(parse_re)
