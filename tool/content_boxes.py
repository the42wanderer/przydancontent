import glob,subprocess,json,numpy as np,os,sys
res={}
for f in sorted(glob.glob(sys.argv[1]+'/*.mp4')):
    v=os.path.basename(f)[:-4]
    p=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-show_entries','format=duration','-of','json',f],capture_output=True,text=True).stdout)
    W,H=p['streams'][0]['width'],p['streams'][0]['height']; d=float(p['format']['duration'])
    w,h=W//4,H//4
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf',f'fps={60/d},scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
    fr=np.frombuffer(raw,np.uint8)[:(len(raw)//(w*h))*w*h].reshape(-1,h,w).astype(np.float32)
    sd=fr.std(0); m=sd>18
    rows=np.where(m.mean(1)>0.35)[0]; cols=np.where(m.mean(0)>0.35)[0]
    if len(rows)<5 or len(cols)<5: res[v]=[0,0,W,H]; continue
    # largest contiguous run of rows
    def run(a):
        best=(a[0],a[0]);s=a[0]
        for x,y in zip(a[:-1],a[1:]):
            if y!=x+1:
                if x-s>best[1]-best[0]: best=(s,x)
                s=y
        if a[-1]-s>best[1]-best[0]: best=(s,a[-1])
        return best
    r0,r1=run(rows); c0,c1=run(cols)
    pad=2
    box=[max(0,(c0+pad)*4),max(0,(r0+pad)*4),min(W,(c1-pad)*4),min(H,(r1-pad)*4)]
    box=[int(x) for x in box]; res[v]=box; print(v,W,H,'->',box,'size',box[2]-box[0],box[3]-box[1])
json.dump(res,open(sys.argv[2],'w'))
