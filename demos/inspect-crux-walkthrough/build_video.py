#!/usr/bin/env python3
"""Render an English coding walkthrough. Never executes teaching snippets."""
import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont
from content import LESSONS

HERE = Path(__file__).resolve().parent
BUILD = HERE / ".build"
W, H, FPS, RATE = 1920, 1080, 24, 22050
BG, INK, MUTED = "#f3f2ec", "#183336", "#667875"
DARK, CODE, TEAL, PURPLE = "#14272e", "#e3eee8", "#087c6d", "#6956b7"
NATIVE = {n for lesson in LESSONS for n in lesson["native"]}
TOKENS = re.compile(r'''(\#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\bce\.[A-Za-z_]\w*|\b[A-Za-z_]\w*\b)''')


@lru_cache(None)
def font(size, bold=False, mono=False):
    if mono:
        choices = [Path("/System/Library/Fonts/Menlo.ttc"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
    else:
        choices = [Path.home()/"Library/Fonts"/("Carlito-Bold.ttf" if bold else "Carlito-Regular.ttf"),
                   Path("/System/Library/Fonts/Supplemental")/("Arial Bold.ttf" if bold else "Arial.ttf"),
                   Path("/usr/share/fonts/truetype/dejavu")/("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")]
    return ImageFont.truetype(str(next(p for p in choices if p.exists())), size, layout_engine=ImageFont.Layout.BASIC)


@lru_cache(maxsize=4096)
def wrap(value, size, width, bold=False, mono=False):
    result=[]
    f=font(size,bold,mono)
    for paragraph in value.split("\n"):
        line=""
        for word in paragraph.split():
            candidate=(line+" "+word).strip()
            if line and f.getlength(candidate)>width:
                result.append(line)
                line=word
            else:
                line=candidate
        result.append(line)
    return result


@lru_cache(maxsize=8192)
def tile(value,size,color,bold,mono):
    f=font(size,bold,mono)
    im=Image.new("RGBA",(max(1,math.ceil(f.getlength(value))+4),size*2))
    ImageDraw.Draw(im).text((0,0),value,font=f,fill=color)
    return im


def text(d,x,y,value,size=28,color=INK,bold=False,mono=False,width=None,spacing=1.25):
    lines=wrap(str(value),size,width,bold,mono) if width else str(value).split("\n")
    for line in lines:
        t=tile(line,size,color,bold,mono)
        d._image.paste(t,(round(x),round(y)),t)
        y+=round(size*spacing)
    return y


def card(d,box,fill,outline=None):
    d.rounded_rectangle(box,18,fill=fill,outline=outline,width=2)


@lru_cache(maxsize=2048)
def code_tile(value,size):
    f=font(size,mono=True)
    im=Image.new("RGBA",(max(1,math.ceil(f.getlength(value))+4),size*2))
    d=ImageDraw.Draw(im)
    x=0;end=0
    for match in TOKENS.finditer(value):
        prefix=value[end:match.start()]
        text(d,x,0,prefix,size,CODE,mono=True)
        x+=f.getlength(prefix)
        word=match.group()
        color="#7d9a91" if word.startswith("#") else "#c8dea6" if word.startswith(('"',"'")) else "#70d9bf" if word.startswith("ce.") else "#b5b5ff" if word in NATIVE else "#d1acf5" if word in {"from","import","def","async","await","return","if","in","for","class","True","False","None"} else CODE
        text(d,x,0,word,size,color,mono=True)
        x+=f.getlength(word);end=match.end()
    text(d,x,0,value[end:],size,CODE,mono=True)
    return im


def narration():
    BUILD.mkdir(exist_ok=True)
    samples=bytearray();position=0;timeline=[];captions=[];transcript=[]
    for index,lesson in enumerate(LESSONS):
        start=position/RATE;steps=[]
        transcript.append(f"\n{index+1:02}. {lesson['title']}\n")
        for step in lesson["steps"]:
            sentence=step["narration"]
            key=hashlib.sha256(("Samantha/160/"+sentence).encode()).hexdigest()[:16]
            source,aiff,wav=[BUILD/(key+s) for s in [".txt",".aiff",".wav"]]
            if not wav.exists():
                source.write_text(sentence)
                subprocess.run(["say","-v","Samantha","-r","160","-o",str(aiff),"-f",str(source)],check=True)
                subprocess.run(["ffmpeg","-y","-v","error","-i",str(aiff),"-ac","1","-ar",str(RATE),str(wav)],check=True)
            gap=round((.5 if not steps else .45)*RATE)
            samples.extend(b"\0\0"*gap);position+=gap
            with wave.open(str(wav),"rb") as w:
                assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(RATE,1,2)
                raw=w.readframes(w.getnframes())
            begin=position/RATE
            samples.extend(raw);position+=len(raw)//2
            end=position/RATE
            steps.append({**step,"start":begin-start,"end":end-start})
            captions.append({"start":begin,"end":end+.2,"text":sentence})
            transcript.append(sentence)
        frame_end=math.ceil((position/RATE+.85)*FPS)
        sample_end=round(frame_end*RATE/FPS)
        samples.extend(b"\0\0"*(sample_end-position));position=sample_end
        timeline.append({**lesson,"steps":steps,"start":start,"end":position/RATE})
        print(f"Narration {index+1}/{len(LESSONS)}: {lesson['id']} ({position/RATE-start:.1f}s)",flush=True)
    with wave.open(str(BUILD/"narration.wav"),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(samples)
    (HERE/"video-timeline.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+"\n")
    (HERE/"narration.txt").write_text("\n".join(transcript)+"\n")
    def stamp(seconds):
        n=round(seconds*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
        return f"{h:02}:{m:02}:{s:02},{n:03}"
    (HERE/"captions.srt").write_text("\n".join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(captions,1)))
    return timeline


@lru_cache(None)
def code_size(value):
    size=27
    while max(font(size,mono=True).getlength(line) for line in value.splitlines())>1100:
        size-=1
    assert size>=18,(size,value)
    return size


def frame(lesson,index,local,now,total):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    text(d,60,36,"CONTAINMENT / CODE WALKTHROUGH",25,TEAL,True)
    text(d,1300,38,"TEACHING SKETCH · NO EVALUATIONS RUN",22,MUTED,True)
    text(d,60,99,f"{index+1:02} / {len(LESSONS):02}    {lesson['part'].upper()} / {lesson['feature'].upper()}",23,MUTED,True)
    size=54
    while font(size,True).getlength(lesson["title"])>1800:size-=1
    text(d,60,139,lesson["title"],size,INK,True)
    text(d,60,213,"Official API patterns in purple. Your adapter helpers, ce.*, in green. All code is instructional.",26,MUTED)
    card(d,(60,275,1260,910),DARK)
    d.rounded_rectangle((61,276,1259,328),17,fill="#1c333b")
    text(d,83,290,lesson["file"],23,"#b7cfc1",mono=True)
    text(d,1300,285,"WHY THIS CODE",22,TEAL,True)
    step_index=max([i for i,s in enumerate(lesson["steps"]) if local>=s["start"]] or [0])
    step=lesson["steps"][step_index]
    for j in range(3):
        x=1300+j*185
        card(d,(x,330,x+165,374),"#ddefe3" if j==step_index else "#e6e9e1")
        text(d,x+18,338,f"{j+1}. "+["Write","Connect","Review"][j],22,TEAL if j==step_index else MUTED,True)
    y=text(d,1300,405,step["title"],35,INK,True,width=550)
    y=text(d,1300,y+20,step["narration"],29,MUTED,width=550,spacing=1.35)
    assert y<760,(lesson["id"],step_index,y)
    card(d,(1300,766,1860,910),"#ddefe3")
    text(d,1323,783,"ILLUSTRATED FLOW · NOT RUN OUTPUT",18,TEAL,True)
    flow_size=23
    while len(wrap(step["output"],flow_size,511,mono=True))*round(flow_size*1.25)>88:
        flow_size-=1
    assert flow_size>=19,(lesson["id"],step_index,flow_size)
    y=text(d,1323,814,step["output"],flow_size,TEAL,mono=True,width=511)
    assert y<=905,(lesson["id"],step_index,y)
    lines=lesson["code"].splitlines();fs=code_size(lesson["code"])
    height=min(30,555/max(1,len(lines)))
    previous=max([s["lines"][1] for s in lesson["steps"][:step_index]] or [0])
    end=max(previous,step["lines"][1]);phase=min(1,max(0,(local-step["start"])/2.4))
    typed=previous+(end-previous)*phase
    for n,line in enumerate(lines,1):
        yy=345+(n-1)*height
        if step["lines"][0]<=n<=step["lines"][1]:
            d.rectangle((61,yy-1,1259,yy+height-1),fill="#24433e")
            d.rectangle((61,yy-1,65,yy+height-1),fill="#73d9b5")
        text(d,79,yy+2,f"{n:02}",17,"#739386",mono=True)
        fraction=min(1,max(0,typed-n+1))
        if fraction>0:
            value=line[:math.ceil(len(line)*fraction)]
            bitmap=code_tile(value,fs)
            im.paste(bitmap,(126,round(yy)),bitmap)
            if fraction<1:
                x=127+font(fs,mono=True).getlength(value)
                d.rectangle((x,yy+3,x+7,yy+fs+2),fill="#8cebc3")
    d.rectangle((0,946,W,H),fill=DARK)
    caption=step["narration"] if step["start"]-.1<=local<=step["end"]+.25 else ""
    if caption:
        rows=wrap(caption,30,1720)
        assert len(rows)<=2,(lesson["id"],rows)
        yy=979 if len(rows)==1 else 958
        for row in rows:
            text(d,(W-font(30).getlength(row))/2,yy,row,30,"#f5f8f2")
            yy+=40
    d.rectangle((0,1068,W,1080),fill="#354e50")
    d.rectangle((0,1068,W*now/total,1080),fill="#73d9b5")
    return im


def previews(timeline):
    total=timeline[-1]["end"]
    sheet=Image.new("RGB",(1440,438*math.ceil(len(timeline)/2)),"#e6e9e1")
    d=ImageDraw.Draw(sheet)
    for i,l in enumerate(timeline):
        t=l["steps"][1]["start"]+3
        im=frame(l,i,t,l["start"]+t,total)
        im.save(BUILD/f"preview-{l['id']}.png")
        sheet.paste(im.resize((704,396)),(8+(i%2)*720,8+(i//2)*438))
        text(d,15+(i%2)*720,408+(i//2)*438,f"{i+1:02} / {l['id']}",21,INK,True)
        # Exercise every explanatory step before starting a long render.
        for step in l["steps"]:
            frame(l,i,step["start"]+3,l["start"]+step["start"]+3,total)
    sheet.save(HERE/"storyboard-preview.jpg",quality=88)
    frame(timeline[0],0,5,0,total).save(HERE/"poster.jpg",quality=92)


def encode(timeline):
    total=timeline[-1]["end"]
    target=HERE/"inspect-crux-coding-walkthrough.mp4"
    args=["ffmpeg","-y","-v","warning","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0", "-i",str(BUILD/"narration.wav"),
          "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-threads","4",
          "-c:a","aac","-b:a","128k","-ar","48000","-af","loudnorm=I=-16:TP=-1.5:LRA=9","-movflags","+faststart",
          "-metadata","title=Inspect x CRUX: a coding walkthrough",
          "-metadata","comment=Teaching pseudocode and API patterns. No models called or evaluations run. ce.* helpers require implementation.","-shortest",str(target)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    index=0;previous=None
    for f in range(round(total*FPS)):
        now=f/FPS
        while index+1<len(timeline) and now>=timeline[index]["end"]-.0001:
            index+=1
            print(f"Rendering {index+1}/{len(timeline)}: {timeline[index]['id']}",flush=True)
        l=timeline[index];local=now-l["start"]
        im=frame(l,index,local,now,total)
        if local<.25 and previous is not None:im=Image.blend(previous,im,max(0,local/.25))
        if l["end"]-now<=1/FPS+.0001:previous=im.copy()
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError("ffmpeg encoding failed")
    print(f"Wrote {target.name}: {total:.2f}s, {target.stat().st_size/1e6:.1f} MB",flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preview",action="store_true")
    p.add_argument("--reuse-narration",action="store_true")
    args=p.parse_args()
    timeline=json.loads((HERE/"video-timeline.json").read_text()) if args.reuse_narration else narration()
    previews(timeline)
    if not args.preview:encode(timeline)


if __name__=="__main__":main()
