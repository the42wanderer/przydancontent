import re,json,sys,urllib.request,datetime
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
out=[]
for u in sys.argv[2:]:
    h=urllib.request.urlopen(urllib.request.Request("https://www.tiktok.com/@"+u,headers={"User-Agent":UA})).read().decode()
    m=re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',h,re.S)
    d=json.loads(m.group(1))["__DEFAULT_SCOPE__"].get("webapp.video-detail",{})
    it=d.get("itemInfo",{}).get("itemStruct")
    if not it: print(u,"NO DATA",d.get("statusCode")); continue
    st=it.get("stats",{}); mu=it.get("music",{}); v=it.get("video",{}); au=it.get("author",{}); ast=it.get("authorStats",{})
    rec=dict(url=u,author=au.get("uniqueId"),followers=ast.get("followerCount"),date=datetime.datetime.utcfromtimestamp(int(it["createTime"])).date().isoformat(),
      desc=it.get("desc"),plays=st.get("playCount"),likes=st.get("diggCount"),comments=st.get("commentCount"),shares=st.get("shareCount"),saves=st.get("collectCount"),
      dur=v.get("duration"),music=f'{mu.get("title")} — {mu.get("authorName")} (original={mu.get("original")})',
      tags=[c.get("hashtagName") for c in it.get("challenges",[])], cover=v.get("cover"), dl=v.get("playAddr"))
    out.append(rec)
    print(json.dumps({k:rec[k] for k in rec if k not in("cover","dl")},ensure_ascii=False))
json.dump(out,open(sys.argv[1],"w"))
