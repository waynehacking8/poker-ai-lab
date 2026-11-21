"""Decision context shared by the replay fitter and the playable clones.

A context is (street, position, facing class, effective stack bucket).  The same
functions are fed by replay ``Act`` records and by live ``GameState`` objects, so a
clone sees a spot exactly as the fitter counted it.
"""

from __future__ import annotations

STREETS = ("preflop", "flop", "turn", "river")
FOLD, CHECK, CALL, RAISE, ALLIN = range(5)
ACTION_NAMES = ("fold", "check", "call", "raise", "allin")
NA = 5
NSTREET, NPOS, NFCL, NSTK = 4, 2, 10, 4
STK_EDGES_BB = (10, 25, 50)
BET_EDGES = (0.4, 0.8, 1.6)  # facing-bet size as a fraction of the pot before the bet

# facing classes
F_OPEN, F_LIMP, F_VS_OPEN, F_VS_3BET = 0, 1, 2, 3
F_NOBET, F_BET_S, F_BET_M, F_BET_L, F_BET_XL, F_RAISED = 4, 5, 6, 7, 8, 9
PREFLOP_FCL = (0, 1, 2, 3)
POSTFLOP_FCL = (4, 5, 6, 7, 8, 9)


def stack_bucket(stack: int, opp_stack: int, bb: int) -> int:
    eff = min(stack, opp_stack) / bb
    k = 0
    for e in STK_EDGES_BB:
        if eff > e:
            k += 1
    return k


def facing_class(street: int, is_button: bool, to_call: int, pot: int, n_raises: int) -> int:
    if street == 0:
        if n_raises == 0:
            return F_OPEN if is_button else F_LIMP
        return F_VS_OPEN if n_raises == 1 else F_VS_3BET
    if n_raises == 0:
        return F_NOBET
    if n_raises >= 2:
        return F_RAISED
    ratio = to_call / max(pot - to_call, 1)
    k = 0
    for e in BET_EDGES:
        if ratio >= e:
            k += 1
    return F_BET_S + k


def make_ctx(street, is_button, to_call, pot, n_raises, stack, opp_stack, bb):
    return (street, 1 if is_button else 0,
            facing_class(street, is_button, to_call, pot, n_raises),
            stack_bucket(stack, opp_stack, bb))


def legal_mask(fcl: int, to_call_positive: bool | None = None):
    """Allowed action codes for a facing class (fold/call need a bet to face)."""
    facing = fcl in (F_OPEN, F_VS_OPEN, F_VS_3BET, F_BET_S, F_BET_M, F_BET_L, F_BET_XL, F_RAISED)
    if facing:
        return (FOLD, CALL, RAISE, ALLIN)
    return (CHECK, RAISE, ALLIN)


def act_code(kind: str, added: int, stack: int) -> int:
    if kind == "fold":
        return FOLD
    if kind == "check":
        return CHECK
    if kind == "call":
        return CALL
    return ALLIN if added >= stack else RAISE


def size_frac(added: int, to_call: int, pot: int) -> float:
    """Raise increment over the call, as a fraction of the pot after calling."""
    extra = max(added - to_call, 0)
    return extra / max(pot + to_call, 1)


def event_of_act(a, is_button: bool):
    """(ctx, action code, size fraction or None) for a replay ``Act``."""
    street = STREETS.index(a.street)
    ctx = make_ctx(street, is_button, a.to_call, a.pot, a.n_raises, a.stack, a.opp_stack, a.bb)
    code = act_code(a.kind, a.added, a.stack)
    frac = size_frac(a.added, a.to_call, a.pot) if code == RAISE else None
    return ctx, code, frac


def ctx_of_state(state, my_street_bet_fn=None):
    """Context of a live ``GameState`` (engine or platform)."""
    street = STREETS.index(state.phase)
    is_button = state.your_seat == state.dealer_seat
    n_raises = sum(1 for e in state.action_history
                   if e["phase"] == state.phase and e["action"] == "raise")
    opp = state.opponent_stacks[0] if state.opponent_stacks else state.your_stack
    bb = infer_bb(state)
    return make_ctx(street, is_button, state.to_call, state.pot, n_raises,
                    state.your_stack, opp, bb), n_raises, bb


def infer_bb(state) -> int:
    for e in state.action_history:
        if e["action"] == "post_big_blind":
            return e["amount"]
    return 100
