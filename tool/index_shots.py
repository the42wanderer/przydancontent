import sys,os,re,json,subprocess,glob,numpy as np
from collections import Counter
src=sys.argv[1]; out=sys.argv[2]; os.makedirs(out+'/thumbs',exist_ok=True)
shots=[]
for f in sorted(glob.glob(src+'/*.mp4')):
    vid=os.path.basename(f)[:-4]
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    cd=subprocess.run(['ffmpeg','-i',f,'-vf','fps=1,cropdetect=limit=24:round=2:reset=0','-f','null','-'],capture_output=True,text=True).stderr
    crops=re.findall(r'crop=(\d+:\d+:\d+:\d+)',cd)
    crop=Counter(crops[len(crops)//3:]).most_common(1)[0][0] if crops else None
    cw,ch,cx,cy=map(int,crop.split(':'))
    cf=f'crop={crop}'
    e=subprocess.run(['ffmpeg','-i',f,'-vf',f"{cf},select='gt(scene,0.22)',showinfo",'-f','null','-'],capture_output=True,text=True).stderr
    cuts=[0.0]+[float(x) for x in re.findall(r'pts_time:([\d.]+)',e)]+[dur]
    W,H=96,54
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf',f'{cf},fps=10,scale={W}:{H},format=gray','-f','rawvideo','-'],capture_output=True).stdout
    fr=np.frombuffer(raw,np.uint8)[: (len(raw)//(W*H))*W*H].reshape(-1,H,W).astype(np.float32)
    segs=[]
    for k in range(len(cuts)-1):
        a,b=cuts[k],cuts[k+1]
        if b-a<0.25: continue
        n=max(1,int(round((b-a)/2.0)))
        for m in range(n): segs.append((a+(b-a)*m/n,a+(b-a)*(m+1)/n,k))
    for j,(a,b,k) in enumerate(segs):
        seg=fr[int(a*10):max(int(a*10)+2,int(b*10))]
        mot=float(np.abs(np.diff(seg,axis=0)).mean()) if len(seg)>1 else 0.0
        sid=f'{vid}_{j:03d}'; mid=(a+b)/2
        subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{mid:.2f}','-i',f,'-frames:v','1','-vf',f'{cf},scale=256:-2',f'{out}/thumbs/{sid}.jpg'])
        shots.append(dict(id=sid,vid=vid,shot=k,start=round(a,2),end=round(b,2),dur=round(b-a,2),motion=round(mot,2),bright=round(float(seg.mean()),1),crop=crop))
    print(vid,crop,round(dur),'pieces',sum(1 for s in shots if s['vid']==vid),flush=True)
json.dump(shots,open(out+'/shots.json','w'))
print('total',len(shots))
