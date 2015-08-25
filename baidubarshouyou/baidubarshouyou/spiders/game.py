# -*- coding: utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector,Selector
from scrapy.http import Request,FormRequest
from items import BaidubarshouyouItem
import settings
from scrapy import log
import json

class baidubarshouyouspider(CrawlSpider):
    name = "baidubar"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = ['http://tieba.baidu.com/f/index/forumpark?cn=%CA%D6%BB%FA%D3%CE%CF%B7&ci=0&pcn=%D3%CE%CF%B7&pci=0&ct=1&rn=20&pn=1']
    
    def parse(self,response):
        sel = Selector(response)
        #抓取每个游戏贴吧的第一页url
        url_list = sel.xpath("//div[@id='ba_list']/div")
        for url in url_list:
            bar_url = url.xpath("./a/@href").extract()[0]
            game_name = url.xpath(".//p[@class='ba_name']/text()").extract()[0][:-1]
            bar_url = "http://tieba.baidu.com/" + str(bar_url)
            req = Request(bar_url, callback=self.page_url_get)
            req.meta['game_name'] = game_name
            yield req
    #
    #抓取每个游戏贴吧的所有页面url
    #
    def page_url_get(self,response):
        sel = Selector(response)
        #第一页 (有些游戏贴吧只有在这一页才有今日话题，并非在pn=0页面。有些游戏在很多页面都有今日话题，
        #所以统一在第一页抓取今日话题，其它页面不抓取)
        url_first = response.url + "  "
        req = Request(url_first, callback=self.theme_url_get)
        req.meta['game_name'] = response.meta['game_name']
        yield req
        
        #抓取主题总数量，每50个为一页，从而得到所有页面url
        theme_num = int(sel.xpath("//div[@class='th_footer_l']/span/text()").extract()[0])
        url = sel.xpath("//div[@id='frs_list_pager']/a/@href").extract()[0]
        
        #href 有两种情况，一种是有"http://tieba.baidu.com"，一种没有
        if url[:4] != "http":
            url = "http://tieba.baidu.com" + url.split('pn=')[0] + "pn="
        else:
            url = url.split('pn=')[0] + "pn="
        num =50
        while num < 100:
        # while num < theme_num:
            page_url = url+str(num)
            num += 50
            #剩余页码
            req = Request(page_url,callback=self.theme_url_get)
            req.meta['game_name'] = response.meta['game_name']
            yield req
            
    #
    #抓取每一个主题
    #
    def theme_url_get(self,response):
        sel = Selector(response)
        #不是第一页url，不抓今日主题
        if int(response.url[-2:])%50 == 0 :
            #抓取主题
            if sel.xpath("//ul[@id='thread_list']/li[contains(@class,'j_thread_list clearfix')]"):
                url_list = sel.xpath("//ul[@id='thread_list']/li[contains(@class,'j_thread_list clearfix')]/@data-field").extract()
                for url in url_list[:1]:
                    id = url.split("\"id\":")[1].split(",")[0]
                    theme_url = "http://tieba.baidu.com/p/" + id
                    req = Request(theme_url, callback= self.comment_page_get)
                    req.meta['game_name'] = response.meta['game_name']
                    yield req
                    
        #如果是第一页，则抓今日主题
        else:
            #如果有今日主题
            if sel.xpath("//dl[@id='threadListGroupCnt']"):
                theme_url = sel.xpath("//dl[@id='threadListGroupCnt']//span[@class='listThreadTitle inlineBlock']/a/@href").extract()[0]
                req = Request(theme_url, callback=self.comment_page_get)
                req.meta['game_name'] = response.meta['game_name']
                yield req
                
            #如果有置顶
            if sel.xpath("//li[@class='thread_top_list_folder']/ul/li"):
                url_list = sel.xpath("//li[@class='thread_top_list_folder']/ul/li/@data-field").extract()
                for url in url_list:
                    id = url.split("\"id\":")[1].split(",")[0]
                    theme_url = "http://tieba.baidu.com/p/" + id
                    req = Request(theme_url, callback= self.comment_page_get)
                    req.meta['game_name'] = response.meta['game_name']
                    yield req
                    
            #抓取主题，贴吧主题标签li有两种格式，相差一个空格
            if sel.xpath("//ul[@id='thread_list']/li[contains(@class,'j_thread_list clearfix')]"):
                url_list = sel.xpath("//ul[@id='thread_list']/li[contains(@class,'j_thread_list clearfix')]/@data-field").extract()
                for url in url_list[:1]:
                    id = url.split("\"id\":")[1].split(",")[0]
                    theme_url = "http://tieba.baidu.com/p/" + id
                    req = Request(theme_url, callback= self.comment_page_get)
                    req.meta['game_name'] = response.meta['game_name']
                    yield req
    #                
    #抓取主题所有页面url
    #
    def comment_page_get(self,response):
        sel = Selector(response)
        page_total= sel.xpath("//ul[@class='l_posts_num']/li[2]/span[2]/text()").extract()[0]
        page_num = 1
        while page_num <= 3:
        # while page_num <= int(page_total):
            page_num_url = response.url + "?pn=" + str(page_num)
            page_num +=1
            req = Request(page_num_url,callback=self.getcontent)
            req.meta['game_name'] = response.meta['game_name']
            yield req
    #        
    #抓取帖子内容
    #
    def getcontent(self,response):
        sel = Selector(response)
        comment_list = sel.xpath(".//div[contains(@class,'l_post l_post_bright')]")
        for game in comment_list:
            game_comment = ''.join(game.xpath(".//cc//text()").extract_unquoted()).strip()
            user_data = game.xpath("@data-field").extract()[0]
            user_name = json.loads(user_data)["author"]["user_name"]
            try:
                comment_time = json.loads(user_data)["content"]["date"]
            except:
                comment_time = game.xpath(".//span[@class='tail-info']/text()").extract()[1]
            game_name = response.meta['game_name']
            item = self.deposi_item(user_name,game_comment,comment_time,game_name)
            yield item
            #如果有回复，抓取回复页面url
            if json.loads(user_data)["content"]["comment_num"] != 0:
                post_id = json.loads(user_data)["content"]["post_id"]
                comment_total_num = json.loads(user_data)["content"]["comment_num"]
                comment_page = self.page(int(comment_total_num))
                tid = response.url.split("/p/")[1].split("?pn")[0]
                page = 0
                while page < comment_page:
                    page +=1
                    url = "http://tieba.baidu.com/p/comment?tid=" + tid + "&pid=" + str(post_id) + "&pn=" + str(page)    
                    req = Request(url,callback=self.get_re_comment)
                    req.meta['game_name'] = response.meta['game_name']
                    yield req
    #                
    # 抓取回复跟帖的评论
    #
    def get_re_comment(self,response):
        sel = Selector(response)
        data_list = sel.xpath("//li[contains(@class,'lzl_single_post j_lzl_s_p')]")
        for data in data_list:
            data_field = data.xpath("@data-field").extract()[0]
            user_name = json.loads(data_field)["user_name"]
            game_comment = "".join(data.xpath(".//span[@class='lzl_content_main']/text()").extract_unquoted()).strip()
            if game_comment[:2] == u"回复":
                addr_num =  game_comment.find(":")
                addr_num = int(addr_num) + 1
                game_comment = game_comment[addr_num:]
            comment_time = sel.xpath(".//span[@class='lzl_time']/text()").extract()[0].strip()
            comment_time = comment_time.split(' ')[0] 
            game_name = response.meta['game_name']
            item = self.deposi_item(user_name,game_comment,comment_time,game_name)
            yield item
    #
    # 由帖子数量算帖子页数，10贴为一页       
    #
    def page(self,num):
        p = num/10
        w = num%10
        if w == 0:
            return int(p)
        else:
            return int(p) + 1

    def deposi_item(self,user,comment,c_time,game_name):
        item = BaidubarshouyouItem()
        item["user_name"] = user.encode('utf8','ignore')
        item['game_comment'] = comment.encode('utf8','ignore')
        item['comment_time'] = c_time.encode('utf8','ignore')
        item['game_name'] = game_name.encode('utf8','ignore')
        return item
        
        
            
            
     
        