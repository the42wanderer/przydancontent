import json,re,sys,difflib
W=[w for s in json.load(open(sys.argv[1])) for w in s['words']]
norm=lambda x:re.sub(r"[^a-z]","",x.lower())
hw=[norm(w['w']) for w in W]
lines=[l.strip() for l in open(sys.argv[2]) if l.strip()]
lw=[];owner=[]
for i,l in enumerate(lines):
    for w in l.split(): 
        n=norm(w)
        if n: lw.append(n); owner.append(i)
sm=difflib.SequenceMatcher(None,lw,hw,autojunk=False)
t=[None]*len(lw)
for a,b,n in sm.get_matching_blocks():
    for k in range(n): t[a+k]=W[b+k]['s']
out=[]
for i,l in enumerate(lines):
    ts=[t[k] for k in range(len(lw)) if owner[k]==i and t[k] is not None]
    st=min(ts) if ts else None
    out.append((st,l)); print(f"{'%d:%04.1f'%(st//60,st%60) if st is not None else '  ?   '}  {l}")
json.dump(out,open(sys.argv[3],'w'))
