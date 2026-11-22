"""Hand-level sanity check of the blueprint logs (BP_LOG dir): strong folds, cheap folds,
premium preflop folds, fallbacks, clamps, a few narrated hands and a depth census.

    python bpopp/hand_check.py DIR
"""
import sys, json, glob, os
_R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _R); sys.path.insert(0, os.path.join(_R, "chipzen_bot"))
from nlhe.cards import cards_from
from nlhe.evaluator import evaluate, category
from chipzen.models import Card
rows=[json.loads(l) for f in glob.glob(sys.argv[1]+"/bp_*.jsonl") for l in open(f) if l.strip()]
def cat(r):
    h=[Card.from_str(c) for c in r["hole"]]; b=[Card.from_str(c) for c in r["board"]]
    return category(evaluate(cards_from(h)+cards_from(b)))
folds=[r for r in rows if r["act"]["action"]=="fold" and r["board"]]
from collections import Counter
c=Counter(cat(r) for r in folds)
print("postflop folds by made-hand category (0 hc,1 pair,2 2pair,3 trips,...)", dict(c))
strong=[r for r in folds if cat(r)>=2]
for r in strong[:12]:
    print("STRONG FOLD", r["hand"], r["phase"], r["hole"], r["board"], "pot",r["pot"],"to_call",r["to_call"],"stack",r["stack"],"opp",r["opp"])
pf=[r for r in folds if cat(r)==1 and r["to_call"]*8<r["pot"]]
for r in pf[:8]:
    print("PAIR small-price fold", r["hand"], r["phase"], r["hole"], r["board"], "pot",r["pot"],"to_call",r["to_call"])
# aggregated by pot odds
cheap=[r for r in folds if r["to_call"]*5<=r["pot"]]
print("folds facing <=20% pot price", len(cheap), "of", len(folds), "; with a pair or better:", sum(cat(r)>=1 for r in cheap))
# preflop folds as BB when to_call is 0 impossible; folds of premium preflop
rank="23456789TJQKA"
def pre(r):
    a,b=sorted(r["hole"],key=lambda c:rank.index(c[0]),reverse=True)
    return a[0]+b[0]+("s" if a[1]==b[1] else "o" if a[0]!=b[0] else "")
pfold=Counter(pre(r) for r in rows if r["phase"]=="preflop" and r["act"]["action"]=="fold")
prem=[k for k in pfold if k in("AA","KK","QQ","JJ","TT","AKs","AKo","AQs","AQo","AJs","KQs")]
print("premium preflop folds:", {k:pfold[k] for k in prem})
print("fallback rows:", [(r["hand"],r["phase"],r["act"]) for r in rows if r["fallback"]])
print("clamped rows:", [(r["hand"],r["phase"],r["min"],r["max"],r["act"]) for r in rows if r["clamped"]])
# narrate 3 hands from the 50/100 level
import itertools
seen=set()
for r in rows:
    key=(r["seat"],r["hand"], tuple(r["hole"]))
    if r["hand"]<=3 and key not in seen and len(seen)<3 and r["phase"]=="preflop":
        seen.add(key)
        print("--- hand",r["hand"],"seat",r["seat"],"hole",r["hole"])
        for q in rows:
            if (q["seat"],q["hand"],tuple(q["hole"]))==key:
                print("  ",q["phase"],q["board"],"pot",q["pot"],"to_call",q["to_call"],"->",q["act"]["action"],q["act"].get("params"),"off_tree",q["off_tree"])
print("======= depth census")
def committed(r, seat):
    by={}
    for e in r["hist"]:
        if e["seat"]==seat: by[e["phase"]]=max(by.get(e["phase"],0),e["amount"])
    return sum(by.values())
bins=Counter()
for r in rows:
    bb=[e["amount"] for e in r["hist"] if e["action"]=="post_big_blind"][0]
    eff=min(r["stack"]+committed(r,r["seat"]), r["opp"][0]+committed(r,1-r["seat"]))/bb
    bins["<=10bb" if eff<=10 else "<=25bb" if eff<=25 else "<=50bb" if eff<=50 else "<=100bb" if eff<=100 else ">100bb"]+=1
tot=sum(bins.values()); print({k:(v,round(v/tot,3)) for k,v in sorted(bins.items())})
