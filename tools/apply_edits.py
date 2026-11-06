"""Apply an edits file exported from the app (format quran-bg-edits v1) to data/.
Usage: python3 tools/apply_edits.py redakcii.json [--dry]
Verse edits replace data/bg-<source>.json[s][v]; tafsir edits replace a note in data/tafsir.json.
An edited verse is removed from data/bg-<source>-flags.json. Mismatched originals are reported but applied."""
import json,sys,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
f=sys.argv[1]; dry='--dry' in sys.argv
E=json.load(open(f))
assert E.get('format')=='quran-bg-edits', 'not an edits file'
cache={}; changed=set(); report=[]
def load(name):
    if name not in cache: cache[name]=json.load(open(os.path.join(D,name)))
    return cache[name]
for x in E['edits']:
    src,ref,new=x['source'],x['ref'],x['text'].strip()
    if src=='tafsir':
        t=load('tafsir.json'); s,ab=ref.split(':'); a,b=map(int,ab.split('-')); s=int(s); i=x['note']-1
        sec=next((q for q in t['sections'] if q['s']==s and q['a']==a and q['b']==b),None)
        if not sec or i>=len(sec['notes']): report.append(('MISSING',src,ref,i+1)); continue
        cur=sec['notes'][i]
        if cur!=x.get('original') and cur!=new: report.append(('ORIG-DIFF',src,ref,i+1))
        sec['notes'][i]=new; changed.add('tafsir.json')
    else:
        fn=f'bg-{src}.json'
        if not os.path.exists(os.path.join(D,fn)): report.append(('NO-SOURCE',src,ref)); continue
        t=load(fn); s,v=map(int,ref.split(':'))
        cur=t[s-1][v-1]
        if cur!=x.get('original') and cur!=new: report.append(('ORIG-DIFF',src,ref))
        t[s-1][v-1]=new; changed.add(fn)
        fl=f'bg-{src}-flags.json'
        if os.path.exists(os.path.join(D,fl)):
            L=load(fl)
            if ref in L: L.remove(ref); changed.add(fl)
print(f"editor={E.get('editor')!r} edits={len(E['edits'])} files={sorted(changed)}")
for r in report: print(*r)
if not dry:
    for n in changed: json.dump(cache[n],open(os.path.join(D,n),'w'),ensure_ascii=False,separators=(',',':'))
