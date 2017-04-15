# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 11:19:52 2017

@author: cube
"""
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import pandas as pd
import time

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search():
    try:
        browser.get('http://www.taobao.com')
        #设置等待的过程
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button")))
        input.send_keys('裤子')
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total")))
        total = int(re.compile('(\d+)').search(total.text).group(1))#得到总页数
        return total
    except TimeoutException:
        return search()

image_list = []
price_list = []
deal_list = []
title_list = []
shop_list = []
location_list = []

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item")))
    html = browser.page_source    
    '''
    bsObj = BeautifulSoup(html,"lxml")
    itemlist = bsObj.find("div",{"id":"mainsrp-itemlist"})
    items = itemlist.find_all("div",{"class":"item"})
    for item in items:
        product = {
            #'image': item.find("img")["src"],       
            'price': item.find(class_="price").get_text(),
            'deal': item.find(class_="deal-cnt").get_text()[:-3],
            'title': item.find(class_="title").get_text(),
            'shop': item.find(class_="shopname J_MouseEneterLeave J_ShopInfo").get_text(),
            'location': item.find(class_="location").get_text(),
            'image': re.search('//g.*?\.jpg_\.webp',str(item))
        }
        image_list.append(product['image'])
        #price_list.append(product['price'])
        deal_list.append(product['deal'])
        title_list.append(product['title'])
        shop_list.append(product['shop'])
        location_list.append(product['location'])
    
    '''
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()    
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        image_list.append(product['image'])
        price_list.append(product['price'])
        deal_list.append(product['deal'])
        title_list.append(product['title'])
        shop_list.append(product['shop'])
        location_list.append(product['location'])
        
def next_page(page_number):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number)))
    except [TimeoutException,StaleElementReferenceException]:
        return next_page(page_number)

def main():
    
    print('开始爬取......')
    total = search()
    for i in range(1,10):        
        get_products()
        print('第'+str(i)+'页爬取完成...')
        next_page(i)
        time.sleep(5)
    data = {
        '图片': image_list,
        '价格': price_list,
        '付款人数': deal_list,
        '名称': title_list,
        '店铺': shop_list,
        '地址': location_list
    }
    DF = pd.DataFrame(data,columns = ['名称','价格','付款人数','店铺','地址','图片'])
    writer = pd.ExcelWriter('E:/淘宝裤子.xlsx')
    DF.to_excel(writer,'Sheet1',index = False)
    print('程序结束！！！')
    """
    total = search()
    get_products()
    """
    
if __name__ == '__main__':
    main()