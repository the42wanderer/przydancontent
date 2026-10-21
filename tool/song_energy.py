import sys,numpy as np,librosa
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
print('tempo',np.round(np.atleast_1d(tempo),1),'first beats',np.round(beats[:4],2))
hop=512
rms=librosa.feature.rms(y=y,hop_length=hop)[0]; t=librosa.times_like(rms,sr=sr,hop_length=hop)
on=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
S_=np.abs(librosa.stft(y,hop_length=hop)); f=librosa.fft_frequencies(sr=sr)
low=S_[f<120].mean(0)
n=int(t[-1]); sec=lambda a:np.array([a[(t>=i)&(t<i+1)].mean() for i in range(n)])
R=20*np.log10(sec(rms)+1e-9); O=sec(on); L=20*np.log10(sec(low)+1e-9)
for i in range(0,n,3): print(f'{i//60}:{i%60:02d} rms{R[i]:6.1f} bass{L[i]:6.1f} hits{O[i]:5.2f} '+'#'*int(max(0,R[i]+28)*2))
z=lambda a:(a-a.mean())/a.std(); sc=z(R)+z(O)+z(L)
for Wn in (10,15,20):
    c=np.convolve(sc,np.ones(Wn)/Wn,'valid'); i=int(np.argmax(c)); print(f'best {Wn}s: {i//60}:{i%60:02d}-{(i+Wn)//60}:{(i+Wn)%60:02d}')
j=np.array([R[i+1:i+3].mean()-R[max(0,i-3):i+1].mean() for i in range(n-3)])
print('drops:',[f'{(i+1)//60}:{(i+1)%60:02d} +{j[i]:.1f}dB' for i in np.argsort(j)[::-1][:5]])
