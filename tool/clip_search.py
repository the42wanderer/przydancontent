import sys,json,torch,open_clip,numpy as np
from PIL import Image,ImageDraw
idx=sys.argv[1]; shots=json.load(open(idx+'/shots.json')); E=np.load(idx+'/emb.npy')
model,_,_=open_clip.create_model_and_transforms('ViT-B-32',pretrained='laion2b_s34b_b79k'); tok=open_clip.get_tokenizer('ViT-B-32')
Q=json.load(open(sys.argv[2])); res={}
with torch.no_grad():
  for key,q in Q.items():
    t=model.encode_text(tok([q])); t=(t/t.norm(dim=-1,keepdim=True)).numpy()[0]
    sc=E@t; order=np.argsort(-sc)
    top=[];vids={}
    for i in order:
        s=shots[i]
        if vids.get(s['vid'],0)>=2: continue
        vids[s['vid']]=vids.get(s['vid'],0)+1; top.append((s['id'],float(sc[i]))); 
        if len(top)==10: break
    res[key]=top
    sheet=Image.new('RGB',(5*256,2*(170)),'black'); d=ImageDraw.Draw(sheet)
    for n,(sid,v) in enumerate(top):
        im=Image.open(f"{idx}/thumbs/{sid}.jpg"); im.thumbnail((256,150))
        x,y=(n%5)*256,(n//5)*170; sheet.paste(im,(x,y)); d.text((x+3,y+152),f"{n}:{sid[-12:]} {v:.2f}",fill='yellow')
    sheet.save(f"{idx}/q_{key}.jpg")
json.dump(res,open(idx+'/search.json','w')); print('done')
