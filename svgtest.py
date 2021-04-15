import requests
import re
from lxml import etree

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
r=requests.get("http://www.dianping.com/shop/9964442",headers=headers)
#print(r.text)
#css_url="http:"+re.findall('href="(//s3plus.meituan.net.*?svgtextcss.*?.css)',r.text)[0]
css_url="http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/81059afc4ff442ac6a87eebe282e0ac9.css"
css_cont=requests.get(css_url,headers=headers)
print(css_cont.text)


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


svg_url = re.findall('class\^="(\w+)".*?(//s3plus.*?\.svg)',css_cont.text)
s_parser=[]
for c,u in svg_url:
    f,w=svg_parser("http:"+u)
    s_parser.append({"code":c,"font":f,"fw":w})
print(s_parser)
css_list = re.findall('(\w+){background:.*?(\d+).*?px.*?(\d+).*?px;', '\n'.join(css_cont.text.split('}')))
css_list = [(i[0],int(i[1]),int(i[2])) for i in css_list]

def font_parser(ft):
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

replace_dic=[]
for i in css_list:
    replace_dic.append({"code":i[0],"word":font_parser(i)})

rep=r.text
for i in range(len(replace_dic)):
    if replace_dic[i]["code"] in rep:
        a=re.findall(f'<\w+\sclass="{replace_dic[i]["code"]}"><\/\w+>',rep)[0]
        rep=rep.replace(a,replace_dic[i]["word"])

