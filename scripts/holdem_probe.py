"""Threshold probe: shove or call with the top T of hands preflop, otherwise fold.

Used in reports/holdem-iterations.md to show what waiting for premium hands is worth.
    python scripts/holdem_probe.py maniac 0.7,0.85,0.93,0.97,0.985
"""
import functools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import holdem  # noqa: E402,F401
from holdem.arena import run_arena
from holdem.opponents import preflop_pct, postflop_strength, call_or_check, check_or_fold, raise_to
from chipzen import Action
class Probe:
    def __init__(s,T,seed=0): s.T=T
    def decide(s,st):
        v=st.valid_actions
        if st.phase=='preflop':
            if preflop_pct(st)>=s.T:
                return Action.raise_to(st.max_raise) if 'raise' in v else call_or_check(st)
            return check_or_fold(st)
        lvl,dr=postflop_strength(st)
        if lvl>=3: return call_or_check(st) if st.to_call>0 else raise_to(st, st.pot*0.7)
        if lvl>=2 and st.to_call<=st.pot*0.5: return call_or_check(st)
        return check_or_fold(st)
def make(T,seed): return Probe(T)
if __name__=="__main__":
    for T in [float(x) for x in sys.argv[2].split(',')]:
        r=run_arena(sys.argv[1],200,1,12,hero_factory=functools.partial(make,T))
        print(sys.argv[1],T,r['win_rate'],r['mean_hands_all'],flush=True)
