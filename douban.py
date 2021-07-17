import requests,json,os,time,datetime,asyncio,aiohttp
from bs4 import BeautifulSoup
from mako.template import Template
import pandas as pd

async def fetchCards(uid,max_id=''):
    with open('cookie', 'r') as f:
        cookie = f.read().replace('\n','')

    url = 'https://m.douban.com/rexxar/api/v2/status/user_timeline/'+uid+'?max_id='+max_id
    headers = {
        'Host': 'm.douban.com',
        'Referer': 'https://m.douban.com/people/gohit/statuses',
        'cookie': cookie,
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url,headers=headers) as response:
            doc = await response.text()
            docu  = json.loads(doc)
            cards = docu['items']
            max_id = docu['items'][-1]['status']['id']
            return (cards,max_id)

async def fetchStatus(id):
    url = 'https://m.douban.com/rexxar/api/v2/status/'+id
    with open('cookie', 'r') as f:
        cookie = f.read().replace('\n','')
    headers = {
        'Host': 'm.douban.com',
        'Referer': 'https://m.douban.com/people/gohit/statuses',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Cookies': cookie
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url,headers=headers) as response:
            doc = await response.text()
            try:
                docu  = json.loads(doc)
                s = docu['text']
            except:
                s = 'Cookie Expired'
            return s

def cards2df(cards):
    df = pd.DataFrame(columns=['id','date','mblog','mblog_img','card_img','card_title','card_subtitle','card_url','share_text','share_name','share_img'])
    for i in cards:
        card = i['status']
        id = card['id']
        t = pd.to_datetime(card['create_time']).strftime('%Y/%m/%d %H:%M')
        mblog = card['text']
        
#        if '...' in mblog:
#            mblog = fetchStatus(id)
        mblog_img=card_img=card_title=card_subtitle=card_url=share_id=share_text=share_name=share_img=''
        if 'images' in card.keys():
            mblog_img = []
            for img in card['images']:
                mblog_img.append(img['large']['url'])
        if card['card']:
            #print(card['card'])
            if card['card']['image']:
                card_img = card['card']['image']['large']['url']
            else:
                card_img = ''
            card_title = card['card']['title']
            card_subtitle = card['card']['subtitle']
            card_url = card['card']['url']
        if card['reshared_status']:
            share_id = card['reshared_status']['id']
            if 'text' in card['reshared_status'].keys():
                share_text = card['reshared_status']['text']
                share_name = card['reshared_status']['author']['name']
#            if '...' in share_text:
#                share_text = fetchStatus(share_id)
            if 'images' in card['reshared_status'].keys():
                share_img = []
                for img in card['reshared_status']['images']:
                    share_img.append(img['large']['url'])
        df = df.append({'id':id,'date':t,'mblog':mblog,'mblog_img':mblog_img,'card_img':card_img,'card_title':card_title,'card_subtitle':card_subtitle,'card_url':card_url,'share_id':share_id,'share_text':share_text,'share_name':share_name,'share_img':share_img},ignore_index=True)
    return df

def fetchMore(df,loop):
    id_list = []
    for i in df.index:
        if ('...' in df.mblog[i]) and (df.id[i] not in id_list):
            id_list.append(df.id[i])
        if ('...' in df.share_text[i]) and (df.share_id[i] not in id_list):
            id_list.append(df.share_id[i])
    task = [fetchStatus(id) for id in id_list]
    s = loop.run_until_complete(asyncio.gather(*task))
    dict_status = dict(zip(id_list, s))
    for i in df.index:
        if df.id[i] in id_list:
            df.loc[i,'mblog'] = dict_status[df.id[i]]
        if df.share_id[i] in id_list:
            df.loc[i,'share_text'] = dict_status[df.share_id[i]]
    return df

#def today(timezone='Asia/Shanghai'):
#    os.environ['TZ'] = timezone
#    time.tzset()
#    today = pd.to_datetime(datetime.date.today())
#    return today

async def gendf(uid,max_id, n):
    df = pd.DataFrame(columns=['id','date','mblog','mblog_img','card_img','card_title','card_subtitle','card_url','share_text','share_name','share_img'])
    for i in range(n):
        (cards,max_id) = await fetchCards(uid,max_id)
        if cards:
            df_new = cards2df(cards)
            df = df.append(df_new,ignore_index=True)
        else:
            break
        i = i+1
        await asyncio.sleep(1)
    return df

def genHTML(df):
    HTML = Template("""<!DOCTYPE html><html><head>
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <meta name="referrer" content="no-referrer">
    <link rel="stylesheet" href="./init_db.css">
    <title>豆瓣广播</title>
    </head>
    <body><div class="BODY">
    <div class="REPLY_LI">
    <h2>${len(db)} 条广播</h2>
    %for id,date,mblog,mblog_img,card_img,card_title,card_subtitle,card_url,share_text,share_name,share_img in db:
    <div class="LI">
    <div class="TIME"><b>陰陽魚</b> | ${date}</div>
    <div class="SAY">${mblog}</br>
    %if mblog_img:
    %for img in mblog_img:
    <img id="myImg" loading="lazy" src=${img} onclick="click1(this.src)"  width=auto height="200"></img>
    %endfor
    %endif
    </div>
    %if card_title:
    <div class="CARD">
    <div class="pic"><img id="myImg" loading="lazy" src=${card_img} onclick="click1(this.src)"></div>
    <div class="text"><a href=${card_url}>${card_title}</a></br>${card_subtitle}</br></div>

    </div>
    %endif
    %if share_text:
    <div class="REPLY"><b1>${share_name}说：</b1>${share_text}</br>
    %if share_img:
    %for img in share_img:
    <img id="myImg" loading="lazy" src=${img} onclick="click1(this.src)"></img>
    %endfor
    %endif
    </div>
    %endif
    </div>
    %endfor
    </div>
    <div class="BACK" margin=auto><a href="./index.html">微博</a></div>
    <div id="myModal" class="modal">
    <span class="close" onclick="click2()">&times;</span>
    <img class="modal-content" id="img01">
    <script src="init.js"></script>
    </body></html>""")
    db = []
    for i in df.index:
        date = df.date[i]
        id = df.id[i]
        mblog = df.mblog[i]
        mblog_img = df.mblog_img[i]
        card_title = df.card_title[i]
        card_subtitle = df.card_subtitle[i]
        card_url = df.card_url[i]
        card_img = df.card_img[i]
        share_text = df.share_text[i]
        share_name = df.share_name[i]
        share_img = df.share_img[i]
        db.append((id,date,mblog,mblog_img,card_img,card_title,card_subtitle,card_url,share_text,share_name,share_img))
    with open("./douban.html",'w') as html:
        html.write(HTML.render(db=db))

uid = '2780378'
max_id = ''
n = 5
nloop = 190
loop = asyncio.get_event_loop()

df = pd.DataFrame(columns=['id','date','mblog','mblog_img','card_img','card_title','card_subtitle','card_url','share_text','share_name','share_img'])

for i in range(nloop):
    df_new = loop.run_until_complete(gendf(uid,max_id,n))
    df_new = fetchMore(df_new,loop)
    df = df.append(df_new,ignore_index=True)
    df = df.sort_values(by='id')
    max_id = df.loc[df.index[0],'id']
    print('Fetching page {}'.format(i*n+n))
    df.to_pickle('douban.pkl')
#df = df.append(df_new,ignore_index=True)
#df = df.drop_duplicates(subset=['date','id'])
df = df.sort_values(by='date')
df.to_pickle('douban.pkl')
#genHTML(df)