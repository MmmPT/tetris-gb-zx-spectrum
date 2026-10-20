"""Native 128K gameplay and audio rendered from actual AY register writes."""
from pathlib import Path
import subprocess,wave,json
import numpy as np
from emulator import setup,run
from demo_player import DemoPlayer,S
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist';SECONDS=40
s,t=setup(str(OUT/'Tetris_GB.z80'))
joystick=[0];read_original=t.read_port
def joystick_port(reg,p):return joystick[0] if p&255==31 else read_original(reg,p)
t.read_port=joystick_port;s.set_tracer(t)
Y=np.arange(192);addresses=((Y&192)<<5)+((Y&7)<<8)+((Y&56)<<2)
palette=np.array([[v if c&2 else 0,v if c&4 else 0,v if c&1 else 0] for v in [205,255] for c in range(8)],dtype=np.uint8)
def pixels():
 m=np.asarray(s.memory.banks[7 if s.memory.o7ffd&8 else 5],dtype=np.uint8);bits=np.unpackbits(m[addresses[:,None]+np.arange(32)],axis=1)
 a=np.repeat(np.repeat(m[6144:6912].reshape(24,32),8,axis=0),8,axis=1);col=np.where(bits,a&7,(a>>3)&7)+((a>>6)&1)*8
 return np.repeat(np.repeat(palette[col],3,axis=0),3,axis=1)
events=[];onsets=[];muted_ticks=0;muted_start=None;last_music_on=1
original=t.write_port;start=s.registers[25]
def port(reg,p,v,offset=0):
 global muted_ticks,muted_start,last_music_on
 if (p&0xc002)==0x8000:
  stamp=reg[25]+offset-start
  events.append((stamp,t.outfffd,v))
  enabled=s.memory[S['music_on']]
  if enabled!=last_music_on:
   if not enabled:muted_start=stamp
   elif muted_start is not None:muted_ticks+=stamp-muted_start;muted_start=None
   last_music_on=enabled
  if t.outfffd==0 and s.memory[S['song_index']]==0 and s.memory[0x7043]==0 and s.memory[S['song_base']]+s.memory[S['song_base']+1]!=0:
   onsets.append(stamp-muted_ticks)
 original(reg,p,v,offset)
t.write_port=port;s.set_tracer(t)
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','768x576','-r','25','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(ROOT/'demo_silent.mp4')],stdin=subprocess.PIPE)
ai=DemoPlayer();first_clear=None
for n in range(SECONDS*50):
 pressed=[] if n<100 else ['EN'] if n<102 else ai.keys(s.memory)
 if n in [1200,1201,1500,1501]:pressed=pressed+['m']
 joystick[0]=sum(v for k,v in [("o",2),("p",1),("a",4),("q",16),("EN",16)] if k in pressed)
 pressed=[k for k in pressed if k not in ["o","p","a","q","EN"]]
 run(s,t,1,pressed)
 if first_clear is None and s.memory[S["cleared"]]:first_clear=n/50
 if n%2==0:
  p=pixels();proc.stdin.write(p.tobytes())
  if n%250==0:
   from PIL import Image
   Image.fromarray(p).save(ROOT/f'demo_frame_{n}.png')
proc.stdin.close();assert proc.wait()==0
# AY tone and 17-bit noise generators, driven by the game's hardware register writes.
# No independent soundtrack or post-added effects.
sr=88200;clock=3546900;psgclock=clock/2
length=SECONDS*sr;audio=np.zeros(length);phase=np.zeros(3);noisephase=0.;ay=[0]*16;prev=0
vol=np.array([0,.00465,.00772,.01096,.01699,.02510,.03710,.05539,.07980,.11216,.15849,.22387,.31623,.44668,.63096,1.0])
noise=np.zeros(131071,dtype=bool);rng=0x1ffff
for i in range(len(noise)):
 noise[i]=bool(rng&1);rng=(rng>>1)|(((rng^(rng>>3))&1)<<16)
def render(end):
 global prev,phase,noisephase
 if end<=prev:return
 idx=np.arange(end-prev)
 delta_n=psgclock/(16*max(1,ay[6]&31)*sr)
 ns=noise[((noisephase+idx*delta_n).astype(np.int64))%len(noise)]
 for ch in range(3):
  period=max(1,ay[2*ch]+((ay[2*ch+1]&15)<<8));delta=psgclock/(16*period*sr)
  tone=np.ones(len(idx),dtype=bool) if ay[7]&(1<<ch) else (phase[ch]+idx*delta)%1<.5
  gate=tone if ay[7]&(8<<ch) else tone&ns
  audio[prev:end]+=(gate.astype(float)*2-1)*vol[ay[8+ch]&15]/3
  phase[ch]=(phase[ch]+(end-prev)*delta)%1
 noisephase=(noisephase+(end-prev)*delta_n)%len(noise)
 prev=end
for ticks,r,v in events:
 render(max(0,min(length,round(ticks/clock*sr))))
 if r<16:ay[r]=v
render(length)
# Low-pass and downsample to reduce square-wave aliasing.
from scipy.signal import resample_poly
samples=resample_poly(audio,1,2)
with wave.open(str(ROOT/'demo_audio.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr//2);w.writeframes((np.clip(samples,-1,1)*30000).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'demo_silent.mp4'),'-i',str(ROOT/'demo_audio.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-t',str(SECONDS),'-movflags','+faststart',str(OUT/'Tetris_GB_demo.mp4')],check=True)
report={'seconds':SECONDS,'machine':'128K','mode_at_end':s.memory[S['mode']],'pieces':s.memory[S['pieces']],'lines':s.memory[S['lines']],'level':s.memory[S['level']],'ay_register_writes':len(events),'registers_written':sorted(set(r for _,r,_ in events)),'audio_rms':float(np.sqrt(np.mean(samples*samples)))}
# Check the melody clock even while rows are being redrawn/cleared.
durations=list((ROOT/'assets/music_a.bin').read_bytes())[2:-3:3]
jitter=[abs((b-a)/s.frame_duration-durations[i%len(durations)]) for i,(a,b) in enumerate(zip(onsets,onsets[1:]))]
report['max_music_onset_jitter_frames']=max(jitter,default=0)
report['music_off_interval_seconds']=[24,30]
report['first_clear_second']=first_clear
report['controls']='Kempston port 1F; M via keyboard'
report['noise_mixer_writes']=sum(r==7 and v==42 for _,r,v in events)
assert report['max_music_onset_jitter_frames']<.01
(ROOT/'demo_validation.json').write_text(json.dumps(report,indent=2));np.savez_compressed(ROOT/'ay_register_capture.npz',events=np.asarray(events));print(report)
