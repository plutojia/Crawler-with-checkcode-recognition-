import pytesseract
import requests
from PIL import Image
import os
from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
import pymongo

data={
    'id':'xxxxxxxx',
    'password':'xxxxxxxxx',
    'checkcode':''
}
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def initTable(threshold=140):           # 二值化函数
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table

def getCheckcode(savepath,location,size):
    rep = {'O': '0',  # replace list
           'I': '1', 'L': '1',
           'Z': '2',
           'S': '8'
           };
    im = Image.open(savepath)
    location['x']=825
    location['y']=495
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    im.save(savepath)
    im = im.convert('L')
    binaryImage = im.point(initTable(), '1')
    # binaryImage.show()
    checkcode = pytesseract.image_to_string(binaryImage, config='-psm 7')
    for r in rep:
        checkcode = checkcode.replace(r, rep[r])
    print(checkcode)
    return checkcode

def login():
    browser.get('http://gsmis.graduate.buaa.edu.cn/gsmis/main.do')
    browser.maximize_window()
    input_id=browser.find_element_by_xpath('//input[@name="id"]')
    input_password =browser.find_element_by_xpath('//input[@name="password"]')
    input_checkcode=browser.find_element_by_xpath('//input[@name="checkcode"]')
    img_checkcode=browser.find_element_by_xpath('//img[@src="/gsmis/Image.do"]')

    location = img_checkcode.location
    size = img_checkcode.size
    browser.save_screenshot('checkcode.png')
    checkcode=getCheckcode('checkcode.png',location,size)

    input_id.send_keys(data['id'])
    input_password.send_keys(data['password'])
    input_checkcode.send_keys(checkcode)

    lg_button=browser.find_element_by_xpath('//img[@onclick="document.forms[0].submit()"]')

    time.sleep(1)
    lg_button.click()

def navigate():
    time.sleep(1)
    browser.get("http://gsmis.graduate.buaa.edu.cn/gsmis/toModule.do?prefix=/py&page=/pySelectCourses.do?do=xsXuanKe")
    browser.switch_to.frame('frmme')
    browser.switch_to.frame('leftFrame')
    xuanke=browser.find_element_by_xpath('//a[@href="/gsmis/py/pySelectCourses.do?do=xuanBiXiuKe"]')
    xuanke.click()
    browser.switch_to.parent_frame()
    browser.switch_to.frame('mainFrame')

def prase():
    lessons=browser.find_elements_by_class_name("tablefont2")
    for lesson in lessons:
        infos=lesson.find_elements_by_xpath("./td")
        is_selected = infos[0].find_element_by_xpath("./input").is_selected()
        if(is_selected):
            info={
                'when&where':infos[1].text,
                'classification': infos[3].text,
                'name': infos[4].text,
                'teacher': infos[10].text,
                'remian': infos[12].text,
            }
            yield(info)


MONGO_URL = 'localhost'
MONGO_DB = 'jiaowu'
MONGO_COLLECTION = 'Curriculum'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
def save_to_mongo(result):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')

login()
navigate()
for res in prase():
    print(res)
    save_to_mongo(res)
