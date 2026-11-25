"""Per name in the archive: flop bet share when the bot acts first or is checked to (no bet yet on the flop)."""
import collections, glob, json, sys
n = collections.Counter(); b = collections.Counter(); m = collections.Counter()
for f in glob.glob(sys.argv[1] + "/*.json"):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    r = d.get("replay") or {}
    names = {p["seat"]: p["name"] for p in (r.get("metadata") or {}).get("players", [])}
    if len(names) != 2:
        continue
    for nm in names.values():
        m[nm] += 1
    for h in r.get("hands", []):
        for st in h.get("streets", []):
            if st.get("street") != "flop":
                continue
            bet = False
            for a in st["actions"]:
                if bet:
                    break
                nm = names.get(a["seat"])
                if a["action_type"] in ("raise", "bet", "all_in"):
                    n[nm] += 1; b[nm] += 1; bet = True
                elif a["action_type"] == "check":
                    n[nm] += 1
rows = [(nm, m[nm], n[nm], b[nm] / n[nm]) for nm in n if n[nm] >= 200]
rows.sort(key=lambda x: -x[3])
print("names with >= 200 unbet flop decisions:", len(rows))
for lo in (0.5, 0.6, 0.7, 0.8):
    sel = [x for x in rows if x[3] >= lo]
    print(f"  bet share >= {lo}: {len(sel)} names, {sum(x[1] for x in sel)} matches")
for x in rows[:25]:
    print(f"  {x[0]:22s} matches {x[1]:5d} spots {x[2]:6d} bet {x[3]:.2f}")
for nm in ("MonteCarlo", "fermat-mini", "PluriBot", "Blueprint", "HRT", "Shadow", "6BP9", "Ashwing_v3"):
    if n[nm]:
        print(f"  {nm:22s} matches {m[nm]:5d} spots {n[nm]:6d} bet {b[nm] / n[nm]:.2f}")
