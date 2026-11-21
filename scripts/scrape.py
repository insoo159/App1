import requests,re,json,datetime,sys
KINDS={'A':'中職一軍例行賽','B':'中職明星賽','C':'中職總冠軍賽','E':'中職季後挑戰賽','G':'中職熱身賽'}
ZH={'Chinese Taipei':'中華台北','Taiwan':'中華台北','Japan':'日本','Korea':'韓國','South Korea':'韓國','United States':'美國','USA':'美國','Dominican Republic':'多明尼加','Venezuela':'委內瑞拉','Puerto Rico':'波多黎各','Mexico':'墨西哥','Cuba':'古巴','Canada':'加拿大','Italy':'義大利','Netherlands':'荷蘭','Australia':'澳洲','Panama':'巴拿馬','Colombia':'哥倫比亞','Israel':'以色列','Great Britain':'英國','Czechia':'捷克','Czech Republic':'捷克','Nicaragua':'尼加拉瓜','Brazil':'巴西','China':'中國'}
z=lambda n:ZH.get(n,n)
WA='亞洲冬盟'
SITES=[{'b':'https://www.cpbl.com.tw','p':'cpbl','cal':[1],'yrs':lambda y:[y,y+1],'k':KINDS},
       {'b':'https://awb.cpbl.com.tw','p':'awb','cal':[1,11,12],'yrs':lambda y:[y],'k':{'P':WA,'C':WA,'E':WA,'A':WA}}]
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36','Accept-Language':'zh-TW,zh;q=0.9,en;q=0.8'}
def parse(resp,year,k,s):
    out=[]
    for g in json.loads(resp.get('GameDatas') or '[]'):
        hm,aw=g.get('HomeTeamName',''),g.get('VisitingTeamName','')
        stop=g.get('IsGameStop')=='1';fin=g.get('PresentStatus')==1 and not stop
        t=str(g.get('PreExeDate') or '')
        out.append({'id':f"{s['p']}{year}{k}{g.get('GameSno')}",'site':s['p'],'y':year,'k':k,'no':g.get('GameSno'),'date':str(g.get('GameDate',''))[:10],'time':t.split('T')[1][:5] if 'T' in t else '',
            'league':s['k'][k],'title':f'{aw} vs {hm}'+(' (延賽/取消)' if stop else ''),'venue':g.get('FieldAbbe',''),
            'home':hm,'away':aw,'hs':g.get('HomeScore') if fin else None,'as':g.get('VisitingScore') if fin else None})
    return out
def site(s,y):
    ss=requests.Session();ss.headers.update(H);out=[]
    r=ss.get(s['b']+'/schedule',timeout=30);print(s['p'],'page status',r.status_code)
    if r.status_code!=200: print(' 被擋或網站異常，略過');return out
    tok=''
    for pat in (r"RequestVerificationToken['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]",r"name=[\"']__RequestVerificationToken[\"'][^>]*value=[\"']([^\"']+)[\"']",r"value=[\"']([^\"']+)[\"'][^>]*name=[\"']__RequestVerificationToken[\"']"):
        m=re.search(pat,r.text)
        if m: tok=tok;break
    print(' token',bool(tok))
    for yr in s['yrs'](y):
        for k in s['k']:
            for mo in s['cal']:
                try:
                    p=ss.post(s['b']+'/schedule/getgamedatas',data={'calendar':f'{yr}/{mo:02d}/01','location':'','kindCode':k},
                        headers={'RequestVerificationToken':m.group(1),'X-Requested-With':'XMLHttpRequest','Referer':s['b']+'/schedule'},timeout=30)
                    p.raise_for_status();o=parse(p.json(),yr,k,s);out+=o;print(' ',yr,k,mo,len(o))
                except Exception as e: print(' FAIL',yr,k,mo,e)
    return out
def wbc(y):
    out=[]
    try:
        r=requests.get('https://statsapi.mlb.com/api/v1/schedule',params={'sportId':51,'startDate':f'{y}-01-01','endDate':f'{y+4}-12-31'},timeout=30).json()
        for d in r.get('dates',[]):
            for g in d.get('games',[]):
                if 'Classic' not in str(g.get('seriesDescription','Classic')): continue
                dt=datetime.datetime.fromisoformat(g['gameDate'].replace('Z','+00:00'))+datetime.timedelta(hours=8)
                a,h=g['teams']['away'],g['teams']['home'];fin=g.get('status',{}).get('abstractGameState')=='Final'
                out.append({'id':f"wbc{g['gamePk']}",'date':dt.strftime('%Y-%m-%d'),'time':dt.strftime('%H:%M'),'league':'WBC','title':f"{z(a['team']['name'])} vs {z(h['team']['name'])}",
                    'venue':g.get('venue',{}).get('name',''),'home':z(h['team']['name']),'away':z(a['team']['name']),'hs':h.get('score') if fin else None,'as':a.get('score') if fin else None})
    except Exception as e: print('wbc FAIL',e)
    print('wbc',len(out));return out
if __name__=='__main__':
    t=datetime.date.today();y=t.year;d=[]
    for s in SITES:
        try: d+=site(s,y)
        except Exception as e: print(s['p'],'FAIL',e)
    d+=wbc(y)
    d+=json.load(open('events.json',encoding='utf-8'))
    print('total',len(d))
    if not d: print('抓到 0 筆，沒有更新 schedule.json');sys.exit(0)
    json.dump(d,open('schedule.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
