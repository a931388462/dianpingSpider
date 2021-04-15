import requests
import re
from lxml import etree

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}

#解析svg，生成
def svg_parser(url):
    r=requests.get(url,headers=headers)
    font=re.findall('" y="(\d+)">(\w+)</text>',r.text,re.M)
    if not font:
        font=[]
        z=re.findall('" textLength.*?(\w+)</textPath>',r.text,re.M)
        y=re.findall('id="\d+" d="\w+\s(\d+)\s\w+"',r.text,re.M)
        for a,b in zip(y,z):
            font.append((a,b))
    width=re.findall("font-size:(\d+)px",r.text)[0]
    new_font=[]
    for i in font:
        new_font.append((int(i[0]),i[1]))
    return new_font,int(width)

#计算class坐标对应svg的文字
def font_parser(ft,s_parser):
    for i in s_parser:
        if i["code"] in ft[0]:
            font=sorted(i["font"])
            if ft[2] < int(font[0][0]):
                x=int(ft[1]/i["fw"])
                return font[0][1][x]
            for j in range(len(font)):
                if (j+1) in range(len(font)):
                    if(ft[2]>=int(font[j][0]) and ft[2]< int(font[j+1][0])):
                        x=int(ft[1]/i["fw"])
                        return font[j+1][1][x]

#取得svg字典
def getSvgDic(pageSource):
    #svg文件所在的css地址
    css_url="http:"+re.findall('href="(//s3plus.meituan.net.*?svgtextcss.*?.css)',pageSource)[0]
    #请求css文件
    css_cont = requests.get(css_url, headers=headers)
    #找到所有svg文件的url
    svg_url = re.findall('class\^="(\w+)".*?(//s3plus.*?\.svg)', css_cont.text)
    s_parser = []
    for c, u in svg_url:
        #解析svg
        f, w = svg_parser("http:" + u)
        s_parser.append({"code": c, "font": f, "fw": w})
    ######
    css_list = re.findall('(\w+){background:.*?(\d+).*?px.*?(\d+).*?px;', '\n'.join(css_cont.text.split('}')))
    css_list = [(i[0], int(i[1]), int(i[2])) for i in css_list]
    # svg字典
    replace_dic = []
    #生成svg字典
    for i in css_list:
        replace_dic.append({"code": i[0], "word": font_parser(i,s_parser)})
    #print(replace_dic)
    return replace_dic

#删除emoji
def delemoji(domstr):
    # 找到所有emoji节点
    emojis = re.findall('<img class="emoji-img" .*?alt="">', domstr)
    # 删除
    for emoji in emojis:
        domstr = domstr.replace(emoji, "")
    return domstr

#parm svg字典 要替换的dom
def repSvgStr(replace_dic,repStr):
    for i in range(len(replace_dic)):
        if replace_dic[i]["code"] in repStr:
            a = re.findall(f'<\w+\sclass="{replace_dic[i]["code"]}"><\/\w+>',repStr)[0]
            repStr = repStr.replace(a,replace_dic[i]["word"])
    html = etree.HTML(delemoji(repStr))
    rewiew = html.xpath("//div[@class='review-words Hide']/text()|//div[@class='review-words']/text()")[0]
    return (rewiew.strip())
