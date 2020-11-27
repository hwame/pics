"""
2020-11-02，主动推送给百度
2020-11-27，修改为post推送，只需一个单文件
"""
import requests
from lxml import etree
from re import findall

def get_article_links(site_url):
    """
    从「归档」页获取所有文章的链接
    """
    archive_url = site_url.rstrip("/") + "/archives/"
    articles = []
    # 第一页，若直接"/archives/page/1/"则报错404
    text = requests.get(archive_url).text
    html = etree.HTML(text)
    data = html.xpath('/html/body/main/article/div/section/div[2]/div/div/a/@href')
    articles.extend(data)
    # 第二页至末尾
    page = html.xpath('/html/body/main/nav/div/div')
    if len(page):
        for i in range(1, int(page[0].text.split('/')[-1])):
            page_url = archive_url + "page/{}/".format(i + 1)
            text = requests.get(page_url).text
            html = etree.HTML(text)
            data = html.xpath('/html/body/main/article/div/section/div[2]/div/div/a/@href')
            articles.extend(data)
    return list(map(lambda item: site_url + item, articles))


def get_all_links(site_url):
    """
    直接从atom.xml获取所有相关的链接并去重
    """
    site_url = site_url.rstrip("/")
    atom_xml = site_url + "/atom.xml"
    text = requests.get(atom_xml).text
    urls = findall('href="(.*?)"', text)
    # atom.xml文件也包括与站点无关的链接，故需排除urls中无关项
    return list(filter(lambda item: site_url in item, set(urls)))
    

def submit_to_baidu(articles, site, token):
    url = f"http://data.zz.baidu.com/urls?site={site}&token={token}"
    headers = {"User-Agent": "curl/7.12.1",
               "Host": "data.zz.baidu.com",
               "Content-Type": "text/plain",
               "Content-Length": "83"
              }
    post_url = "\n".join(articles)
    response = requests.post(url=url, headers=headers, data=post_url)
    return response.text


if __name__ == "__main__":
    s = """参数说明：\n     all  提交所有链接；\n    post  仅提交文章链接。\n"""
    print(s)
    param = input("请输入一个参数（all/post）：")
    mysite = input("请输入完整的主站网址：")
    mytoken = input("请输入推送密钥字符串：")
    if param == "all":
        myurls = get_all_links(mysite)
        result = submit_to_baidu(myurls, mysite, mytoken)
        print("\n", result)
    elif param == "post":
        myurls = get_article_links(mysite)
        result = submit_to_baidu(myurls, mysite, mytoken)
        print("\n", result)
    else:
        print("参数错误，请重新执行程序！")
