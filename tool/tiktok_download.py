import re,json,sys,urllib.request,http.cookiejar,os
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
outdir=sys.argv[1]
for u in sys.argv[2:]:
    cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    h=op.open(urllib.request.Request("https://www.tiktok.com/@"+u,headers={"User-Agent":UA})).read().decode()
    d=json.loads(re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',h,re.S).group(1))
    v=d["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["video"]
    id=u.split("/")[-1]
    try:
        b=op.open(urllib.request.Request(v["playAddr"],headers={"User-Agent":UA,"Referer":"https://www.tiktok.com/"})).read()
        open(f"{outdir}/{id}.mp4","wb").write(b); print(id,len(b))
    except Exception as e: print(id,"FAIL",e)
