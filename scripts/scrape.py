import requests,re,json,datetime,sys
B='https://cpbl.com.tw'
KINDS={'A':'中職一軍例行賽','B':'中職明星賽','C':'中職總冠軍賽','E':'中職季後挑戰賽','G':'中職熱身賽'}
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36','Accept-Language':'zh-TW,zh;q=0.9,en;q=0.8'}
def parse(resp,year,k,lab):
    out=[]
    for g in json.loads(resp.get('GameDatas') or '[]'):
        hm,aw=g.get('HomeTeamName',''),g.get('VisitingTeamName','')
        stop=g.get('IsGameStop')=='1';fin=g.get('PresentStatus')==1 and not stop
        t=str(g.get('PreExeDate') or '')
        out.append({'id':f"cpbl{year}{k}{g.get('GameSno')}",'date':str(g.get('GameDate',''))[:10],'time':t.split('T')[1][:5] if 'T' in t else '',
            'league':lab,'title':f'{aw} vs {hm}'+(' (延賽/取消)' if stop else ''),'venue':g.get('FieldAbbe',''),
            'home':hm,'away':aw,'hs':g.get('HomeScore') if fin else None,'as':g.get('VisitingScore') if fin else None})
    return out
def cpbl(year,s,tok):
    out=[]
    for k,lab in KINDS.items():
        try:
            r=s.post(B+'/schedule/getgamedatas',data={'calendar':f'{year}/01/01','location':'','kindCode':k},
                headers={'RequestVerificationToken':tok,'X-Requested-With':'XMLHttpRequest','Referer':B+'/schedule'},timeout=30)
            r.raise_for_status();o=parse(r.json(),year,k,lab);out+=o;print(year,k,lab,len(o))
        except Exception as e: print('FAIL',year,k,e)
    return out
if __name__=='__main__':
    s=requests.Session();s.headers.update(H)
    r=s.get(B+'/schedule',timeout=30);print('schedule page status',r.status_code)
    r.raise_for_status()
    m=re.search(r"RequestVerificationToken:\s*['\"]([^'\"]+)['\"]",r.text)
    if not m: sys.exit('找不到 token：中職網站可能改版，或擋掉了 GitHub 的連線')
    t=datetime.date.today();ys={t.year,t.year+1}|({t.year-1} if t.month<3 else set())
    d=[]
    for y in sorted(ys): d+=cpbl(y,s,m.group(1))
    d+=json.load(open('events.json',encoding='utf-8'))
    print('total',len(d))
    if not d: sys.exit('抓到 0 筆，沒有更新 schedule.json')
    json.dump(d,open('schedule.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
