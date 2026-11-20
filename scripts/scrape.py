import requests,re,json
B='https://cpbl.com.tw'
KINDS={'A':'中職例行賽','B':'中職明星賽','C':'中職季後挑戰賽','E':'中職台灣大賽'}
def cpbl(year):
    s=requests.Session();s.headers['User-Agent']='Mozilla/5.0'
    h=s.get(B+'/schedule',timeout=30).text
    m=re.search(r'RequestVerificationToken[^>]*?value="([^"]+)"',h) or re.search(r'RequestVerificationToken\W+([\w-]{20,})',h)
    tok=m.group(1) if m else ''
    out=[]
    for k,lab in KINDS.items():
        for mo in range(1,13):
            try:
                r=s.post(B+'/schedule/getgamedatas',data={'calendar':f'{year}/{mo:02d}/01','location':'','kindCode':k},headers={'RequestVerificationToken':tok},timeout=30).json()
                for g in json.loads(r.get('GameDatas') or '[]'):
                    hm,aw=g.get('HomeTeamName',''),g.get('VisitingTeamName','')
                    out.append({'id':f"cpbl{year}{k}{g.get('GameSno')}",'date':str(g.get('GameDate',''))[:10],'league':lab,'title':f'{aw} vs {hm}','venue':g.get('FieldAbbe',''),'home':hm,'away':aw,'hs':g.get('HomeScore'),'as':g.get('VisitingScore')})
            except Exception as e: print('skip',k,mo,e)
    return out
if __name__=='__main__':
    import datetime
    y=datetime.date.today().year;d=[]
    for yr in {y,y-1} if datetime.date.today().month<3 else {y}:
        d+=cpbl(yr)
    d+=json.load(open('events.json',encoding='utf-8'))
    print('total',len(d))
    if d: json.dump(d,open('schedule.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
