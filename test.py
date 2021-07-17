import pandas as pd
from mako.template import Template

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
df = pd.read_pickle('douban_gohit.pkl')
df = df.sort_values(by='date')
df = df.drop_duplicates(subset=['date'])
genHTML(df)