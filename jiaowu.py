import pytesseract
import requests
from PIL import Image
import os

save_dir='checkcode/'
data={
    'id':'zyxxxxxxxxxxxxx',
    'password':'xxxxxxxxxx',
    'checkcode':''
}
session = requests.session()
ch_url = 'http://gsmis.graduate.buaa.edu.cn/gsmis/Image.do'
login_url='http://gsmis.graduate.buaa.edu.cn/gsmis/indexAction.do'

def initTable(threshold=140):           # 二值化函数
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table

def getCheckcode(ch_url):
    rep = {'O': '0',  # replace list
           'I': '1', 'L': '1',
           'Z': '2',
           'S': '8'
           };
    save_image(ch_url)
    im = Image.open(save_dir + 'checkcode.jpg')
    im = im.convert('L')
    binaryImage = im.point(initTable(), '1')
    # binaryImage.show()
    checkcode = pytesseract.image_to_string(binaryImage, config='-psm 7')
    for r in rep:
        checkcode = checkcode.replace(r, rep[r])
    print(checkcode)
    return checkcode

def save_image(url):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    try:
        response = session.get(url)
        if response.status_code == 200:
            file_path = save_dir+'{0}.{1}'.format('checkcode', 'jpg')
            with open(file_path, 'wb') as f:
                f.write(response.content)
    except requests.ConnectionError:
        print('Failed to Save Image')

if __name__ == '__main__':

    checkcode=getCheckcode(ch_url)
    data['checkcode']=checkcode

    res=session.post(login_url,data=data)
    print(res.text)

