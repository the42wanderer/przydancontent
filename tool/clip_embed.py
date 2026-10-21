import sys,json,torch,open_clip,numpy as np
from PIL import Image
idx=sys.argv[1]
shots=json.load(open(idx+'/shots.json'))
model,_,pre=open_clip.create_model_and_transforms('ViT-B-32',pretrained='laion2b_s34b_b79k')
model.eval(); E=[]
with torch.no_grad():
    for i in range(0,len(shots),64):
        b=torch.stack([pre(Image.open(f"{idx}/thumbs/{s['id']}.jpg").convert('RGB')) for s in shots[i:i+64]])
        e=model.encode_image(b); E.append((e/e.norm(dim=-1,keepdim=True)).numpy())
np.save(idx+'/emb.npy',np.concatenate(E)); print('ok',len(shots))
