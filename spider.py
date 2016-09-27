import pycurl
import StringIO
import urllib  

import mechanize
import cookielib

from bs4 import BeautifulSoup
import re

import random

def post_data(url, data):
    head = ["Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding:gzip, deflate",
            "Accept-Language:zh-CN,zh;q=0.8",
            "Cache-Control:max-age=0",
            "Connection:keep-alive",
            "Content-Length:47",
            "Content-Type:application/x-www-form-urlencoded",
            "Cookie:__utmt=1; __utma=51474103.1979389292.1467254190.1467254190.1467254190.1; __utmb=51474103.1.10.1467254190; __utmc=51474103; __utmz=51474103.1467254190.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); NSC_ECBxfciptujohQsfnjvnTTMW=ffffffff839a740945525d5f4f58455e445a4a42378b"
            #"Cookie:__utma=51474103.1279819473.1467166788.1467166788.1467166788.1; __utmb=51474103.5.10.1467166788; __utmc=51474103; __utmz=51474103.1467166788.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); NSC_ECBxfciptujohQsfnjvnTTMW=ffffffff839a740645525d5f4f58455e445a4a42378b",
            "Host:www.osu.edu",
            "Origin:https://www.osu.edu",
            "Referer:https://www.osu.edu/findpeople/",
            "Upgrade-Insecure-Requests:1",
            "User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"]

    buf = StringIO.StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)
    curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(data))
    #curl.setopt(pycurl.POSTFIELDS,  data)
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.HTTPHEADER,  head)
    #curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    #curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    curl.perform() 
    the_page = buf.getvalue()
    buf.close() 
    print the_page
    return the_page 


def mechan(url):
    if 1:
        data = {
                "blog_id" :9000,
                "uid":755,
                "content":"what_happend_1111",
                }
        data=urllib.urlencode(data)
        br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()  
        br.set_cookiejar(cj) 
        br.set_handle_equiv(True) 
        br.set_handle_gzip(True) 
        br.set_handle_redirect(True)  
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        br.set_debug_http(False)
        
        br.addheaders = [("User-Agent","Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")]
        response = br.open(url, data)
        print response.read()




       # return page_content





if __name__ == "__main__":
    for i in range(10):
        url = "http://121.43.230.143:8015/comment"
    #url = "http://121.43.230.143:8015/comment?blog_id=9000&uid=550&content=what_happend"
        mechan(url)

