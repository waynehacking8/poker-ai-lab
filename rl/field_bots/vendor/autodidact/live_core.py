"""Vendored from autodidactinnovations-dev/poker-arena @ 334e1480b7b4cc99e0ae9c5297bdbbafa5ac58bf, patched for the offline arena (see PROVENANCE.md)."""

import time

from . import strategy as S

# Offline stubs for everything live_agent.py did over the network or on disk. All of it was observation only
# (opponent stats cache, shadow logs); the adapter in chipzen_agent.py switched the same things off.
S22_SHADOW_ENABLED = False
S24_SHADOW_ENABLED = False
S37_SHADOW_ENABLED = False
S38_SHADOW_ENABLED = False
S22_VETO_ENABLED = True
EQ_TRIALS = 2000


def get_opponent_stats(agent_id):
    return None


def my_agent_id():
    return None


def build_reasoning(equity, pot_odds, action):
    parts = [f'ke: "{equity * 100:.0f}% eq"']
    if action in ("bet", "raise", "all-in"):
        parts.append(f'sr: "pot odds {pot_odds * 100:.0f}%, equity edge"')
    return "{" + ", ".join(parts) + "}"


def _noop(*args, **kwargs):
    return None


shadow_record_fold = shadow_record_flop_nopair = shadow_record_s38 = shadow_record_s24 = _noop
shadow_record_s37 = shadow_record_s22 = _noop


def flop_nopair_verdict(*args, **kwargs):
    return None


_PENDING_WEIGHT_BY_STREET = {"Preflop": 0.35, "Flop": 0.65, "Turn": 0.80, "River": 0.90}
STACK_RISK_CAP = 0.5
STACK_RISK_EQUITY_FLOOR = 0.80
S32_PRICE_MARGIN = 0.05
S32_AGG_PRICE_MARGIN = 0.20
STACK_VELOCITY_SHADOW_MODE = False  # ENFORCING (was shadow-only through hand cmtd2ab0)
STACK_VELOCITY_CAP_BY_STREET = {"Preflop": 0.45, "Flop": 0.35, "Turn": 0.25, "River": 0.20}
STACK_VELOCITY_MIN_BB = 20  # skip entirely on short stacks, where every call is
STACK_VELOCITY_TIGHTEN_MAX = 0.65  # cap can shrink to 35% of its base at most
STACK_VELOCITY_TIGHTEN_K = 6.0     # aggression at which half of max tightening applies
def velocity_cap_for(street, aggression_score):
    """Base per-street cap, tightened by cumulative aggression."""
    base = STACK_VELOCITY_CAP_BY_STREET.get(street, 0.30)
    a = max(0.0, aggression_score or 0.0)
    k = STACK_VELOCITY_TIGHTEN_K
    tighten = STACK_VELOCITY_TIGHTEN_MAX * (a * a) / (a * a + k * k)
    return base * (1.0 - tighten)
P_FOLD_SINGLE = 0.55        # haircut from the measured 0.658 (n=76). Our bets
CALLED_EQUITY_HAIRCUT = 0.85  # equity_when_called < raw equity: a caller's range
FE_MIN_EQUITY = 0.25        # below this we hold nothing resembling a draw
FE_MAX_EQUITY = 0.55        # above this the normal value logic should handle it
FE_MAX_OPPONENTS = 1        # fold equity collapses multiway (measured: 0.658 at
FE_EXCLUDE_STREETS = ("River",)   # no further streets to realize equity on, and
CHECK_FUTURE_VALUE = 0.35   # crude but directionally right: a checked flop still
MIN_EDGE = 0.05
FOLD_EQUITY_ENABLED = False
STAGE1_RFI_ENABLED = True
ISO_RAISE_BASE_BB = 4.0
ISO_RAISE_PER_LIMPER_BB = 1.0
_RFI_RANK = {r: v for v, r in enumerate("23456789TJQKA", start=2)}
def _rfi_tier(hole_raw):
    """Position tier a hand qualifies for: 1 (any), 2 (HJ+), 3 (CO/BTN/SB), or
    None (never open). Pure card reading - no equity, no model input."""
    if not hole_raw or len(hole_raw) != 2:
        return None
    try:
        r1, s1 = _RFI_RANK[hole_raw[0][0]], hole_raw[0][1]
        r2, s2 = _RFI_RANK[hole_raw[1][0]], hole_raw[1][1]
    except (KeyError, IndexError):
        return None
    hi, lo, suited = max(r1, r2), min(r1, r2), s1 == s2
    pair, gap = hi == lo, hi - min(r1, r2) - 1
    if pair and hi >= 10:                                   return 1   # AA-TT
    if suited and hi == 14 and lo >= 11:                    return 1   # AJs+
    if not suited and hi == 14 and lo == 13:                return 1   # AKo
    if suited and hi == 13 and lo == 12:                    return 1   # KQs
    if pair and 7 <= hi <= 9:                               return 2   # 99-77
    if suited and (hi, lo) in ((14, 10), (13, 11), (13, 10), (12, 11), (11, 10)):
        return 2                                                       # ATs KJs KTs QJs JTs
    if not suited and (hi, lo) in ((14, 12), (14, 11), (13, 12)):
        return 2                                                       # AQo AJo KQo
    if pair:                                                return 3   # 66-22
    if suited and hi == 14:                                 return 3   # any suited ace
    if suited and hi >= 12:                                 return 3   # any suited K/Q
    if suited and hi >= 10 and lo >= 7:                      return 3
    if suited and gap <= 1 and lo >= 4:                      return 3   # 54s+ connectors
    if not suited and hi == 14 and lo >= 8:                  return 3   # A8o+
    if not suited and hi >= 12 and lo >= 10:                 return 3   # KTo QJo QTo
    if not suited and (hi, lo) == (13, 11):                  return 3   # KJo
    return None
_RFI_MAX_TIER = {"EARLY": 2, "HJ": 3, "CO": 3, "BTN": 3, "SB": 3, "BB": 3}
PREFLOP_POLARIZE_ENABLED = True
SIZE_BY_STREET = {"Flop": 0.66, "Turn": 0.50, "River": 0.40}
SIZE_TEXTURE_DRY = 0.85     # rainbow, unpaired, unconnected - range-favouring
SIZE_TEXTURE_WET = 1.15     # 3-flush, paired, or connected - draws exist
BLUFF_MIN_EQUITY = 0.40     # a real draw, not a hope. Of 36 selected spots,
BLUFF_MAX_OPPONENTS = 1     # heads-up ONLY. Fold equity collapses multiway and
BLUFF_MAX_AGGRESSION = 4.0  # never bluff into a raise war: calibration (12)
BLUFF_MAX_MADE_CATEGORY = 0
BLUFF_MAX_COMMIT = 0.25     # a 40%-committed spot is not a semi-bluff. Excludes
SIZING_SCHEME_ENABLED = True    # ON from v46 (2026-09-04 21:05). Enabled after
REDESIGN_RANGED_ENABLED = True
AGGRESSION_FOLD_ENABLED = not REDESIGN_RANGED_ENABLED
AGGRESSION_FOLD_THRESHOLD = 3.0
def board_texture(board_raw):
    """-> ('dry'|'wet', size multiplier) from the VISIBLE board only.
    Deterministic - max rank-count, suit-count and connectedness read straight
    off the community cards. Consumes no model output, so it carries no
    circularity risk (PRINCIPLES #9), and it is knowable at the decision point
    rather than only at showdown (PRINCIPLES #10).
    """
    if not board_raw or len(board_raw) < 3:
        return "n/a", 1.0
    try:
        ranks = sorted({"23456789TJQKA".index(c[0]) for c in board_raw})
        suits = {}
        for c in board_raw:
            suits[c[1]] = suits.get(c[1], 0) + 1
        paired = len(set(c[0] for c in board_raw)) < len(board_raw)
        three_flush = max(suits.values()) >= 3
        connected = (len(ranks) >= 3
                     and any(ranks[i + 2] - ranks[i] <= 4
                             for i in range(len(ranks) - 2)))
    except Exception:
        return "n/a", 1.0
    if three_flush or paired or connected:
        return "wet", SIZE_TEXTURE_WET
    return "dry", SIZE_TEXTURE_DRY
def scheme_size(street, board_raw):
    """Bet size as a fraction of pot, from street and texture ONLY.
    Takes no equity and no made_category argument by design - the tell this
    replaces existed because size was a function of hand strength.
    """
    base = SIZE_BY_STREET.get(street)
    if base is None:
        return None
    _t, mult = board_texture(board_raw)
    return base * mult
def _rfi_position(position):
    """Map _compute_position output to a seat label. frac 0 = SB, 1 = BTN."""
    frac, n = position.get("frac"), position.get("n") or 0
    if frac is None or n < 2:
        return "HJ"                       # neutral default
    idx = round(frac * (n - 1))
    if idx == 0:                          return "SB"
    if idx == 1:                          return "BB"
    if idx == n - 1:                      return "BTN"
    if idx == n - 2:                      return "CO"
    if idx == n - 3:                      return "HJ"
    return "EARLY"
def rfi_should_open(hole_raw, position):
    """True if this hand should be RAISED from this seat."""
    if not STAGE1_RFI_ENABLED:
        return False, None
    tier = _rfi_tier(hole_raw)
    if tier is None:
        return False, None
    pos = _rfi_position(position)
    return tier <= _RFI_MAX_TIER.get(pos, 2), pos
def alpha_breakeven(pot, bet):
    """Fold frequency a PURE bluff needs to break even: bet / (pot + bet).
    Half-pot 0.33, pot 0.50, 2x pot 0.67."""
    tot = (pot or 0) + (bet or 0)
    return (bet / tot) if tot > 0 else 1.0
def fold_equity_in_domain(equity, street, n_opponents):
    """Is this spot inside the domain where P_FOLD_SINGLE was measured?"""
    if street in FE_EXCLUDE_STREETS:
        return False
    if (n_opponents or 1) > FE_MAX_OPPONENTS:
        return False
    e = equity or 0
    return FE_MIN_EQUITY <= e <= FE_MAX_EQUITY
def fold_equity_decision(equity, pot, bet, n_opponents, street=None, tightness=None,
                          streets_left=0):
    """Return (should_bet, detail). Compares EV of betting vs EV of checking.
        EV_bet   = P(fold)*pot + (1-P(fold)) * (eq_called*(pot + 2*bet) - bet)
        EV_check = equity*pot + equity*CHECK_FUTURE_VALUE*pot*streets_left
    Multiway collapse is NOT a special case - it falls out of raising the
    single-opponent fold probability to the power of the opponent count."""
    detail = {"in_domain": False}
    if not fold_equity_in_domain(equity, street, n_opponents):
        return False, detail
    n = max(1, n_opponents or 1)
    p_single = P_FOLD_SINGLE
    if tightness == "tight":
        p_single = min(0.75, p_single + 0.10)
    elif tightness == "loose":
        p_single = max(0.30, p_single - 0.10)
    p_fold = p_single ** n
    eq = equity or 0
    eq_called = eq * CALLED_EQUITY_HAIRCUT
    ev_bet = p_fold * pot + (1 - p_fold) * (eq_called * (pot + 2 * bet) - bet)
    ev_check = eq * pot + eq * CHECK_FUTURE_VALUE * pot * max(0, streets_left)
    detail = {"in_domain": True, "p_fold": round(p_fold, 3),
              "alpha": round(alpha_breakeven(pot, bet), 3),
              "ev_bet": round(ev_bet, 1), "ev_check": round(ev_check, 1),
              "streets_left": streets_left, "n_opp": n}
    edge = (ev_bet - ev_check) / pot if pot else 0.0
    detail["edge"] = round(edge, 4)
    return (ev_bet > ev_check + MIN_EDGE * pot), detail
_STREETS_LEFT = {"Flop": 2, "Turn": 1, "River": 0}
VALUE_SIZE_HIGH = 0.90
STACK_VELOCITY_MADE_HAND_EXEMPT = 4
STACK_VELOCITY_POT_ODDS_EXEMPT = 0.12
STACK_VELOCITY_POT_ODDS_MIN_RATIO = 3.0
STACK_VELOCITY_POT_ODDS_MIN_CATEGORY = 1
_DECIDED_BY = {
    "opening for value from here": "value_open",
    "not a hand I'd open with - folding rather than calling a raise": "polarize_fold_vs_raise",
    "raise or fold here - not calling with a hand I wouldn't open": "polarize_fold_branch_c",
    "premium hand, three-betting the top of my range": "value_3bet_tier",
    "premium hand, re-raising for value": "value_3bet",
    "isolating for value": "value_isolate",
    "raising it up, taking this pot down now": "value_iso_raise",
    "betting for value here": "value_bet",
    "betting with fold equity - checking is worth less here": "fold_equity_bet",
    "semi-bluffing with a draw, heads up": "semi_bluff",
    "raising for value here": "value_raise",
    "raising, well ahead here": "value_raise",
    "price is right for this equity": "pot_odds_call",
    "cheap price, defending": "pot_odds_call",
    "price is right, calling": "pot_odds_call",
    "all-in for less - price is tiny, taking it": "allin_bargain",
    "price beats the risk cap - calling": "price_over_cap",
    "their betting says this price is not real - folding": "s22_range_veto",
    "opponent has shown real aggression - not paying this price": "aggression_fold",
    "not enough equity to pay this price": "pot_odds_fold",
    "not worth even the cheap price": "pot_odds_fold",
    "not enough equity to continue": "pot_odds_fold",
    "hand never developed - not paying another street with nothing": "stalled_guard",
    "capping risk - re-raising here outruns my edge, taking the cheaper line": "stack_risk_cap",
    "capping risk - not enough edge to justify this much of my stack": "stack_risk_cap",
    "capping risk - checking instead of over-committing": "stack_risk_cap",
    "capping risk - that moves too much of my stack at once, taking the cheaper line": "velocity_brake",
    "capping risk - taking the free card instead of committing this fast": "velocity_brake",
    "capping risk - too much of my stack committed in a single move": "velocity_brake",
    "checking my option": "check_free",
    "checking, taking a free card": "check_free",
    "taking the free option": "check_free",
    "taking the passive line": "passive_call",
    "no check available, calling": "forced_call",
    "no fold available, taking the call": "forced_call",
    "no fold available, calling": "forced_call",
    "folding, no cheap way to continue": "pot_odds_fold",
    "no good option here": "forced_fold",
    "only line available": "forced_only_legal",
    "playing it safe": "fallback_error_path",
}
def decided_by(msg):
    return _DECIDED_BY.get(msg, f"unmapped:{msg}")
STALLED_MIN_STREET = "Turn"     # river-only fires zero times; money is already in
STALLED_MAX_CATEGORY = 0        # high card only
STALLED_EQUITY_RELEASE = 0.45
_STREET_INDEX = {"Preflop": 0, "Flop": 1, "Turn": 2, "River": 3}
def stalled_hand_fold(street, made_category, equity, to_call):
    """True if this CALL should be refused because the hand never developed.
    Only ever evaluated on a call facing a bet. Checking is free and is never
    touched - none of the traced leak hands lost a chip by checking."""
    if not to_call or to_call <= 0:
        return False
    if _STREET_INDEX.get(street, 0) < _STREET_INDEX[STALLED_MIN_STREET]:
        return False
    if made_category is None or made_category > STALLED_MAX_CATEGORY:
        return False
    if equity is not None and equity >= STALLED_EQUITY_RELEASE:
        return False
    return True
def evaluate_velocity_brake(street, delta_frac, equity, aggression_score, action,
                             to_call, total_available, bb_chips, can,
                             made_category=None, pot=None):
    """Return (verdict, detail) for the proposed velocity brake, or (None, detail).
    Pure function of already-computed values so it can be evaluated in shadow
    mode and unit-tested without a live table. `can` is a predicate for whether
    an action name is currently legal."""
    detail = {"delta_frac": round(delta_frac, 3), "street": street}
    if action not in ("call", "bet", "raise", "all-in"):
        return None, detail
    if made_category is not None and made_category >= STACK_VELOCITY_MADE_HAND_EXEMPT:
        detail["skipped"] = "made_hand"
        detail["made_category"] = made_category
        return None, detail
    if pot is not None and to_call > 0:
        _po = to_call / (pot + to_call) if (pot + to_call) > 0 else 1.0
        detail["pot_odds"] = round(_po, 3)
        if (_po <= STACK_VELOCITY_POT_ODDS_EXEMPT
                and equity >= _po * STACK_VELOCITY_POT_ODDS_MIN_RATIO
                and made_category is not None
                and made_category >= STACK_VELOCITY_POT_ODDS_MIN_CATEGORY):
            detail["skipped"] = "pot_odds"
            return None, detail
    if bb_chips and total_available < STACK_VELOCITY_MIN_BB * bb_chips:
        detail["skipped"] = "short_stack"
        return None, detail
    cap = velocity_cap_for(street, aggression_score)
    detail["cap"] = round(cap, 3)
    detail["agg"] = round(aggression_score or 0.0, 2)
    if delta_frac <= cap:
        return None, detail
    call_delta = (to_call / total_available) if total_available else 1.0
    if action in ("raise", "bet", "all-in") and to_call > 0 and can("call") \
            and call_delta <= cap:
        detail["call_delta"] = round(call_delta, 3)
        return "call", detail
    if to_call <= 0 and can("check"):
        return "check", detail
    if action in ("raise", "bet", "all-in") and to_call > 0 and can("call"):
        detail["fallthrough"] = "call_over_cap"
        detail["call_delta"] = round(call_delta, 3)
        return "call", detail
    if can("fold"):
        return "fold", detail
    return None, detail
def decide_live(table):
    """v7: mirrors strategy.py's v6 decide() (v4's equity-vs-pot-odds shape -
    wide calling, selective raising - as the primary preflop driver, with
    position awareness and opponent-tendency-aware sizing layered on top; see
    strategy.py's module docstring for why v5's Chen-heavy preflop blend was
    dropped) plus this file's own live-only additions: certain/pending
    opponent-count correction, street-aware pending weight, and the
    escalating-re-raise + stack-risk-cap safeguards documented in the module
    docstring above."""
    allowed_names, to_call, call_amount = set(), 0, 0
    try:
        allowed = table.get("allowedActions") or {}
        allowed_names = S._capability_names(allowed)
        self_seat = S._find_self_seat(table)
        hole_raw = self_seat.get("holeCards") or []
        board_raw = table.get("boardCards") or []
        pot = table.get("potChips", 0) or 0
        current_bet = table.get("currentBet")
        my_bet = self_seat.get("currentBetChips", 0) or 0
        stack = self_seat.get("stackChips")
        _committed = self_seat.get("totalCommittedChips", my_bet) or my_bet
        _committed_frac = (_committed / (_committed + stack)
                           if stack is not None and (_committed + stack) > 0 else 0.0)
        call_to_amount = allowed.get("callToAmount")
        call_chips = allowed.get("callChips")
        if call_chips is None:
            call_chips = allowed.get("callAmount")
        if call_chips is None and call_to_amount is not None:
            call_chips = max(0, int(call_to_amount) - int(my_bet))
        if call_chips is None and current_bet is not None:
            call_chips = max(0, int(current_bet) - int(my_bet))
        to_call = call_chips or 0
        _stack_num = stack if isinstance(stack, (int, float)) and stack > 0 else None
        eff_to_call = min(to_call, _stack_num) if _stack_num is not None else to_call
        allin_for_less = to_call > eff_to_call
        call_amount = call_to_amount if call_to_amount is not None else (current_bet if current_bet is not None else my_bet + to_call)
        min_bet_to = allowed.get("minBet")
        min_raise_to = allowed.get("minRaiseTo", table.get("minRaiseTo"))
        max_commit = allowed.get("maxCommit")
        allin_to = allowed.get("allInToAmount")
        bet_range = allowed.get("betRange") or []
        raise_range = allowed.get("raiseRange") or []
        seats = table.get("seats") or []
        active_seats = [s for s in seats if isinstance(s, dict) and s.get("status") in ("Active", "AllIn") and s is not self_seat]
        opponent_ids = [s.get("agentId") for s in active_seats if s.get("agentId")]
        acted_nums = S._acted_seat_numbers(table)
        certain_seats = [s for s in active_seats if s.get("seatNumber") in acted_nums]
        pending_seats = [s for s in active_seats if s.get("seatNumber") not in acted_nums]
        num_opponents = len(certain_seats)
        num_pending = len(pending_seats)
        if num_opponents == 0 and num_pending == 0:
            num_opponents = 1
        S._update_opponent_model(table)
        looseness, aggression = S._opp_profile(opponent_ids)
        position = S._compute_position(table, self_seat)
        pos_bonus = (position["frac"] - 0.5) * 0.20
        loose_bonus = (looseness - 0.4) * 0.10
        opp_raises = S._opponent_raises_this_street(table, self_seat.get("seatNumber"))
        escalation_bump = 0.10 * max(0, opp_raises - 1)
        aggressor_seat = S._last_aggressor_seat(table, self_seat.get("seatNumber"))
        opp_bump = 0.0
        if aggressor_seat is not None:
            aggressor_id = next((s.get("agentId") for s in seats
                                  if isinstance(s, dict) and s.get("seatNumber") == aggressor_seat), None)
            if aggressor_id:
                try:
                    opp_bump = S.opponent_read_bump(get_opponent_stats(aggressor_id))
                except Exception:
                    opp_bump = 0.0
        try:
            hole = [S._parse_card(c) for c in hole_raw if c]
            board = [S._parse_card(c) for c in board_raw if c]
        except Exception:
            hole, board = [], []
        street = table.get("street")
        pending_weight = _PENDING_WEIGHT_BY_STREET.get(street, 0.35)
        made_category = None
        if len(hole) == 2 and len(board) >= 3:
            try:
                made_category = S._best_hand_rank(hole + board)[0]
            except Exception:
                made_category = None
        range_strength = 0.0
        aggression_score = 0.0
        if street in ("Flop", "Turn", "River"):
            aggression_score = S.cumulative_aggression(table, self_seat.get("seatNumber"))
            range_strength = S.aggression_to_range_strength(aggression_score)
        try:
            equity = S.estimate_equity(hole, board, num_opponents=num_opponents, pending_opponents=num_pending,
                                        pending_weight=pending_weight, range_strength=range_strength,
                                        trials=EQ_TRIALS) if len(hole) == 2 else 0.5
        except Exception:
            equity = 0.5
        redesign_info = None
        if (REDESIGN_RANGED_ENABLED and street in ("Flop", "Turn", "River")
                and to_call > 0 and len(hole) == 2):
            try:
                _acts = S.opponent_postflop_actions(table, self_seat.get("seatNumber"))
                _lists = [_acts[s.get("seatNumber")] for s in active_seats if s.get("seatNumber") in _acts]
                if _lists:
                    _eq_r, _ = S.estimate_equity_ranged(hole, board, _lists,
                                                        pending_opponents=len(active_seats) - len(_lists))
                    redesign_info = {"equity_old": round(equity, 3), "equity_ranged": round(_eq_r, 3)}
                    equity = _eq_r
            except Exception:
                redesign_info = None
        chen_norm = min(1.0, S._chen_score(hole) / 20.0) if len(hole) == 2 else 0.5
        def has(name):
            return not allowed_names or name in allowed_names
        def sized_bet(fraction):
            frac = max(0.3, min(1.1, fraction * (1.0 + 0.25 * (looseness - 0.4))))
            lo = min_bet_to if min_bet_to is not None else (bet_range[0] if len(bet_range) > 0 else None)
            hi = max_commit if max_commit is not None else (bet_range[1] if len(bet_range) > 1 else stack)
            target = int(my_bet + max(pot, 10) * frac)
            return S._clamp_to_amount(target, lo, hi)
        def sized_raise(fraction):
            frac = max(0.3, min(1.1, fraction * (1.0 + 0.25 * (looseness - 0.4))))
            lo = min_raise_to if min_raise_to is not None else (raise_range[0] if len(raise_range) > 0 else None)
            hi = max_commit if max_commit is not None else (raise_range[1] if len(raise_range) > 1 else stack)
            base = call_amount if call_amount else (my_bet + to_call)
            target = int(base + max(pot, 10) * frac)
            return S._clamp_to_amount(target, lo, hi)
        def bb_raise(bb_multiple):
            """Absolute raise-to in big blinds. Preflop opens are sized off the
            blind, not off a pot that has barely moved - see ISO_RAISE_BASE_BB.
            Falls back to the pot-fraction sizer if the table does not report a
            big blind, so a missing field degrades instead of raising."""
            if not bb_chips:
                return sized_raise(0.7)
            lo = min_raise_to if min_raise_to is not None else (
                raise_range[0] if len(raise_range) > 0 else None)
            hi = max_commit if max_commit is not None else (
                raise_range[1] if len(raise_range) > 1 else stack)
            return S._clamp_to_amount(int(bb_chips * bb_multiple), lo, hi)
        _fe_detail = {}
        _fe_amount = 0
        def _fe_bet(pot_, my_bet_, min_bet_to_, max_commit_, bet_range_, stack_):
            """Would a 0.5-pot semi-bluff beat checking, once P(fold) is priced?"""
            nonlocal _fe_detail, _fe_amount
            try:
                amt = sized_bet(0.5)
                new_chips = max(0, int(amt) - int(my_bet_ or 0))
                if new_chips <= 0:
                    return False
                tightness = None
                if aggressor_seat is not None:
                    pass  # nobody has bet into us here by definition (to_call<=0)
                ok, det = fold_equity_decision(
                    equity, pot_, new_chips, num_opponents, street=street,
                    tightness=tightness, streets_left=_STREETS_LEFT.get(street, 0))
                _fe_detail, _fe_amount = det, amt
                return ok
            except Exception:
                return False
        def below_min(amount, lo):
            try:
                return lo is not None and int(amount) < int(lo)
            except (TypeError, ValueError):
                return False
        pot_odds = eff_to_call / (pot + eff_to_call) if (pot + eff_to_call) > 0 else 0.0
        allin_bargain = allin_for_less and equity >= pot_odds
        _agg_for_margin = min(1.0, (aggression_score or 0.0) / BLUFF_MAX_AGGRESSION)
        _price_margin = S32_PRICE_MARGIN + (S32_AGG_PRICE_MARGIN - S32_PRICE_MARGIN) * _agg_for_margin
        price_is_good = (to_call or 0) > 0 and equity >= pot_odds + _price_margin
        bb_chips = table.get("bigBlindChips")
        if street == "Preflop":
            strength = equity + 0.08 * (chen_norm - 0.5)
            raise_pos_adj = pos_bonus * 0.5 + loose_bonus * 0.4
            call_margin = max(0.0, max(0.0, 0.06 - loose_bonus - pos_bonus * 0.3) + escalation_bump + opp_bump)
            facing_raise = bb_chips is not None and (current_bet or 0) > bb_chips
            rfi_open, rfi_pos = rfi_should_open(hole_raw, position)
            _seat_label = _rfi_position(position)
            if to_call <= 0:
                open_thresh = 0.68 - raise_pos_adj
                if rfi_open and has("raise"):
                    amount = sized_raise(0.65 + 0.15 * max(0, looseness - 0.4))
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "opening for value from here"
                elif strength >= open_thresh and has("raise"):
                    amount = sized_raise(0.65 + 0.15 * max(0, looseness - 0.4))
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "opening for value from here"
                elif has("check"):
                    action, amount, msg = "check", 0, "checking my option"
                elif has("call"):
                    action, amount, msg = "call", call_amount, "taking the passive line"
                elif has("fold"):
                    action, amount, msg = "fold", 0, "no good option here"
                else:
                    action, amount, msg = next(iter(allowed_names), "check"), 0, "only line available"
            elif facing_raise:
                raise_thresh = 0.72 - raise_pos_adj + escalation_bump + opp_bump
                _t = _rfi_tier(hole_raw)
                if (STAGE1_RFI_ENABLED and _t is not None and _t <= 2
                        and opp_raises <= 1 and has("raise")):
                    amount = sized_raise(0.85)
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "premium hand, three-betting the top of my range"
                elif strength >= raise_thresh and has("raise"):
                    amount = sized_raise(0.85)
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "premium hand, re-raising for value"
                elif allin_bargain and has("call"):
                    action, amount, msg = ("call", call_amount,
                                           "all-in for less - price is tiny, taking it")
                elif (PREFLOP_POLARIZE_ENABLED and _t is None
                      and _seat_label != "BB" and has("fold")):
                    action, amount, msg = "fold", 0, \
                        "not a hand I'd open with - folding rather than calling a raise"
                elif equity >= pot_odds + call_margin and has("call"):
                    action, amount, msg = "call", call_amount, "price is right for this equity"
                elif has("fold"):
                    action, amount, msg = "fold", 0, "not enough equity to pay this price"
                elif has("check"):
                    action, amount, msg = "check", 0, "taking the free option"
                elif has("call"):
                    action, amount, msg = "call", call_amount, "no fold available, taking the call"
                else:
                    action, amount, msg = next(iter(allowed_names), "fold"), call_amount, "only line available"
            else:
                isolate_thresh = 0.66 - raise_pos_adj + escalation_bump + opp_bump
                _limpers = 0
                try:
                    _limpers = S._limpers_this_street(table, self_seat.get("seatNumber"))
                except Exception:
                    _limpers = 0
                if rfi_open and has("raise"):
                    amount = bb_raise(ISO_RAISE_BASE_BB
                                      + ISO_RAISE_PER_LIMPER_BB * _limpers)
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = ("raising it up, taking this pot down now" if _limpers
                           else "opening for value from here")
                elif strength >= isolate_thresh and has("raise"):
                    amount = sized_raise(0.7)
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "isolating for value"
                elif allin_bargain and has("call"):
                    action, amount, msg = ("call", call_amount,
                                           "all-in for less - price is tiny, taking it")
                elif (PREFLOP_POLARIZE_ENABLED and to_call > 0
                      and _seat_label != "BB" and has("fold")):
                    action, amount, msg = "fold", 0, \
                        "raise or fold here - not calling with a hand I wouldn't open"
                elif equity >= pot_odds + call_margin and has("call"):
                    action, amount, msg = "call", call_amount, "cheap price, defending"
                elif has("fold"):
                    action, amount, msg = "fold", 0, "not worth even the cheap price"
                elif has("check"):
                    action, amount, msg = "check", 0, "taking the free option"
                else:
                    action, amount, msg = next(iter(allowed_names), "fold"), call_amount, "only line available"
        else:
            value_thresh = 0.68 - pos_bonus * 0.3
            raise_thresh = 0.72 - pos_bonus * 0.3 + escalation_bump + opp_bump
            _scheme = scheme_size(street, board_raw) if SIZING_SCHEME_ENABLED else None
            if to_call <= 0:
                if equity >= value_thresh and has("bet"):
                    amount = sized_bet(_scheme if _scheme is not None
                                       else (VALUE_SIZE_HIGH if equity > 0.82 else 0.5))
                    if below_min(amount, min_bet_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "bet"
                    msg = "betting for value here"
                elif equity >= value_thresh and has("raise"):
                    amount = sized_raise(_scheme if _scheme is not None
                                         else (VALUE_SIZE_HIGH if equity > 0.82 else 0.5))
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "raising for value here"
                elif (FOLD_EQUITY_ENABLED and has("bet") and made_category is not None
                      and pot and _fe_bet(pot, my_bet, min_bet_to, max_commit, bet_range, stack)):
                    amount = _fe_amount
                    if below_min(amount, min_bet_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "bet"
                    msg = "betting with fold equity - checking is worth less here"
                elif (SIZING_SCHEME_ENABLED and has("bet")
                      and street in ("Turn", "River")
                      and made_category is not None
                      and made_category <= BLUFF_MAX_MADE_CATEGORY
                      and equity >= BLUFF_MIN_EQUITY
                      and (num_opponents or 0) <= BLUFF_MAX_OPPONENTS
                      and (aggression_score or 0.0) < BLUFF_MAX_AGGRESSION
                      and _committed_frac <= BLUFF_MAX_COMMIT
                      and _scheme is not None):
                    amount = sized_bet(_scheme)
                    if below_min(amount, min_bet_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "bet"
                    msg = "semi-bluffing with a draw, heads up"
                elif has("check"):
                    action, amount, msg = "check", 0, "checking, taking a free card"
                elif has("call"):
                    action, amount, msg = "call", call_amount, "no check available, calling"
                elif has("fold"):
                    action, amount, msg = "fold", 0, "folding, no cheap way to continue"
                else:
                    action, amount, msg = next(iter(allowed_names), "check"), 0, "only line available"
            else:
                call_margin = max(0.0, 0.06 - loose_bonus * 0.5 + escalation_bump + opp_bump)
                if allin_bargain and has("call"):
                    action, amount, msg = ("call", call_amount,
                                           "all-in for less - price is tiny, taking it")
                elif (has("fold") and not price_is_good
                      and stalled_hand_fold(street, made_category, equity, to_call)):
                    action, amount, msg = "fold", 0, \
                        "hand never developed - not paying another street with nothing"
                elif equity >= raise_thresh and has("raise"):
                    amount = sized_raise(_scheme if _scheme is not None else 0.75)
                    if below_min(amount, min_raise_to) and has("all-in"):
                        action, amount = "all-in", int(allin_to if allin_to is not None else amount)
                    else:
                        action = "raise"
                    msg = "raising, well ahead here"
                elif (AGGRESSION_FOLD_ENABLED
                      and (aggression_score or 0.0) >= AGGRESSION_FOLD_THRESHOLD
                      and not (equity >= pot_odds + S32_AGG_PRICE_MARGIN)
                      and has("fold")):
                    _shadow_would = ("call" if (equity >= pot_odds + call_margin
                                                and has("call"))
                                     else ("fold" if has("fold")
                                           else ("check" if has("check") else None)))
                    shadow_record_fold(table.get("id") or table.get("tableId"), {
                        "street": street,
                        "equity": equity,
                        "pot": pot,
                        "to_call": to_call,
                        "aggression_score": aggression_score,
                        "made_category": made_category,
                        "shadow_action": _shadow_would,
                        "pot_odds": pot_odds,
                        "call_margin": round(call_margin, 4),
                        "hero_committed_at_fold":
                            (self_seat.get("totalCommittedChips", my_bet) or my_bet),
                        "board_at_fold": list(board_raw),
                        "hole_cards": list(hole_raw),
                        "num_opponents": num_opponents,
                        "hero_agent_id": my_agent_id(),
                        "hero_seat": self_seat.get("seatNumber"),
                    })
                    action, amount, msg = "fold", 0,                         "opponent has shown real aggression - not paying this price"
                elif equity >= pot_odds + call_margin and has("call"):
                    action, amount, msg = "call", call_amount, "price is right, calling"
                    try:
                        _fnp = flop_nopair_verdict(street, made_category, equity,
                                                   pot_odds, call_margin,
                                                   hole_raw, board_raw)
                        if _fnp is not None:
                            shadow_record_flop_nopair(
                                table.get("id") or table.get("tableId"), dict(_fnp, **{
                                    "pot": pot, "to_call": to_call,
                                    "aggression_score": aggression_score,
                                    "hole_cards": list(hole_raw),
                                    "board": list(board_raw),
                                    "num_opponents": num_opponents,
                                    "hero_seat": self_seat.get("seatNumber"),
                                    "actual": "call"}))
                    except Exception:
                        pass
                elif has("fold"):
                    action, amount, msg = "fold", 0, "not enough equity to continue"
                elif has("check"):
                    action, amount, msg = "check", 0, "taking the free option"
                elif has("call"):
                    action, amount, msg = "call", call_amount, "no fold available, calling"
                else:
                    action, amount, msg = next(iter(allowed_names), "fold"), call_amount, "only line available"
        my_total_committed = self_seat.get("totalCommittedChips", my_bet) or my_bet
        already_committed_other_streets = max(0, my_total_committed - my_bet)
        if (stack is not None and action in ("call", "bet", "raise", "all-in")
                and amount and not allin_bargain):
            total_available = my_total_committed + stack
            if total_available > 0:
                commit_frac = (amount + already_committed_other_streets) / total_available
                if commit_frac > STACK_RISK_CAP and equity < STACK_RISK_EQUITY_FLOOR:
                    if action in ("raise", "bet", "all-in") and to_call > 0 and has("call") \
                            and (my_bet + to_call + already_committed_other_streets) / total_available <= STACK_RISK_CAP:
                        action, amount, msg = "call", call_amount, "capping risk - re-raising here outruns my edge, taking the cheaper line"
                    elif to_call == 0 and has("check"):
                        action, amount, msg = "check", 0, "capping risk - checking instead of over-committing"
                    elif has("fold") and not price_is_good:
                        action, amount, msg = "fold", 0, "capping risk - not enough edge to justify this much of my stack"
                    elif price_is_good and has("call"):
                        action, amount, msg = ("call", call_amount,
                                               "price beats the risk cap - calling")
        shadow = {}
        try:
            if stack is not None:
                _total_avail = my_total_committed + stack
                if _total_avail > 0:
                    _delta = max(0.0, (amount - my_bet) / _total_avail) if amount else 0.0
                    _verdict, shadow = evaluate_velocity_brake(
                        street, _delta, equity, aggression_score, action, to_call,
                        _total_avail, bb_chips, has, made_category=made_category,
                        pot=pot)
                    shadow["would"] = _verdict
                    shadow["actual"] = action
                    _s38_proposed = amount
                    if _verdict and not STACK_VELOCITY_SHADOW_MODE and not allin_bargain:
                        if _verdict == "call":
                            action, amount, msg = "call", call_amount, "capping risk - that moves too much of my stack at once, taking the cheaper line"
                        elif _verdict == "check":
                            action, amount, msg = "check", 0, "capping risk - taking the free card instead of committing this fast"
                        elif not price_is_good:
                            action, amount, msg = "fold", 0, "capping risk - too much of my stack committed in a single move"
                        elif has("call"):
                            action, amount, msg = ("call", call_amount,
                                                   "price beats the risk cap - calling")
                    if (S38_SHADOW_ENABLED and _verdict == "check"
                            and (to_call or 0) == 0):
                        _s38_cap = shadow.get("cap")
                        shadow_record_s38(
                            table.get("id") or table.get("tableId"), {
                                "street": street,
                                "equity": round(equity, 3),
                                "made_category": made_category,
                                "pot": pot,
                                "total_available": _total_avail,
                                "delta_frac": round(_delta, 3),
                                "cap": _s38_cap,
                                "aggression_score": round(aggression_score or 0.0, 2),
                                "proposed_amount": int(_s38_proposed or 0),
                                "capped_amount": (int(_s38_cap * _total_avail)
                                                  if _s38_cap is not None else None),
                                "enforced": not STACK_VELOCITY_SHADOW_MODE,
                                "equity_times_pot": round(equity * (pot or 0), 1),
                            })
        except Exception:
            shadow = {"error": "velocity brake evaluation failed"}
        result = {"action": action, "amount": int(amount), "message": msg}
        if allowed.get("reasoningRequired"):
            result["reasoning"] = build_reasoning(equity, pot_odds, action)
        thresholds = {name: round(locals()[name], 3) for name in
                      ("open_thresh", "raise_thresh", "isolate_thresh", "value_thresh") if name in locals()}
        result["_debug"] = {
            "street": street, "equity": round(equity, 3), "pot_odds": round(pot_odds, 3),
            "num_opponents": num_opponents, "num_pending": num_pending, "pending_weight": pending_weight,
            "position_frac": round(position["frac"], 2), "looseness": round(looseness, 2),
            "aggression": round(aggression, 2), "thresholds": thresholds,
            "opp_raises_this_street": opp_raises, "escalation_bump": round(escalation_bump, 2),
            "aggressor_seat": aggressor_seat, "opp_bump": round(opp_bump, 3),
            "stack": stack, "eff_to_call": eff_to_call, "allin_for_less": allin_for_less,
            "opp_stacks": [sv.get("stackChips") for sv in seats
                           if isinstance(sv, dict)
                           and sv.get("seatNumber") != self_seat.get("seatNumber")],
            "stack_bb": (round(stack / bb_chips, 1)
                         if stack is not None and bb_chips else None),
            "spr": (round(stack / pot, 2) if stack is not None and pot else None),
            "total_chips": table.get("_participant_total_chips"),
            "buyin": table.get("_participant_initial_chips"),
            "below_buyin": (None if table.get("_participant_total_chips") is None
                            or table.get("_participant_initial_chips") is None
                            else table["_participant_total_chips"]
                                 < table["_participant_initial_chips"]),
            "range_strength": round(range_strength, 2),
            "aggression_score": round(aggression_score, 2),
            "made_category": made_category,
            "rfi_open": rfi_open if street == "Preflop" else None,
            "limpers": _limpers if street == "Preflop" and "_limpers" in locals() else None,
            "rfi_pos": rfi_pos if street == "Preflop" else None,
            "seat_label": (_seat_label if street == "Preflop"
                           and "_seat_label" in locals() else None),
            "stalled_guard": stalled_hand_fold(street, made_category, equity, to_call),
            "decided_by": decided_by(msg), "fold_equity": _fe_detail,
            "pot": pot, "to_call": to_call,
            "bet_to_pot": round((amount - my_bet) / pot, 3)
                          if pot and action in ("bet", "raise", "all-in") and amount else None,
            "size_frac": (round(scheme_size(street, board_raw), 3)
                          if (SIZING_SCHEME_ENABLED
                              and action in ("bet", "raise", "all-in")
                              and scheme_size(street, board_raw) is not None)
                          else None),
            "board_texture": (board_texture(board_raw)[0]
                              if street != "Preflop" else None),
            "hole": hole_raw, "board": board_raw,
            "shadow_brake": shadow,
            "stack_commit_frac": round((amount + already_committed_other_streets) / (my_total_committed + stack), 3)
                                  if stack and (my_total_committed + stack) > 0 else None,
        }
        if redesign_info:
            result["_debug"]["redesign"] = redesign_info
        try:
            if S24_SHADOW_ENABLED and street in ("Flop", "Turn", "River") and to_call > 0 and len(hole) == 2:
                _agg = S.s24_last_aggression(table, self_seat.get("seatNumber"))
                if _agg:
                    _hc = S.s24_hand_class(list(hole_raw), list(board_raw))
                    _ap = S.s24_ahead_prob(street, _agg[1], _hc)
                    shadow_record_s24(table.get("id") or table.get("tableId"), {
                        "street": street, "equity": round(equity, 4), "ahead_prob": None if _ap is None else round(_ap, 4),
                        "hand_class": _hc, "agg_seat": _agg[0], "agg_bucket": _agg[1], "action": action,
                        "to_call": to_call, "pot": pot, "pot_odds": round(pot_odds, 4),
                        "hole": hole_raw, "board": board_raw})
                    result["_debug"]["ahead_prob_s24"] = None if _ap is None else round(_ap, 3)
        except Exception:
            pass
        try:
            if S22_SHADOW_ENABLED and street in ("Flop", "Turn", "River") and to_call > 0 and len(hole) == 2:
                _acts = S.opponent_postflop_actions(table, self_seat.get("seatNumber"))
                _lists = [_acts.get(s.get("seatNumber"), []) for s in certain_seats]
                _t0 = time.time()
                _eq_r, _acc = S.estimate_equity_ranged(hole, board, _lists, pending_opponents=num_pending,
                                                       pending_weight=pending_weight)
                shadow_record_s22(table.get("id") or table.get("tableId"), {
                    "street": street, "equity": round(equity, 4), "equity_ranged": round(_eq_r, 4),
                    "accept_rate": round(_acc, 3) if _acc is not None else None,
                    "secs": round(time.time() - _t0, 2), "action": action, "to_call": to_call, "pot": pot,
                    "pot_odds": round(pot_odds, 4), "opp_actions": _lists, "num_pending": num_pending,
                    "hole": hole_raw, "board": board_raw})
                result["_debug"]["equity_ranged"] = round(_eq_r, 3)
                if (S22_VETO_ENABLED and result.get("action") == "call"
                        and equity >= pot_odds and _eq_r < pot_odds
                        and opp_bump >= 0
                        and has("fold")):
                    result["action"], result["amount"] = "fold", 0
                    result["message"] = "their betting says this price is not real - folding"
                    if allowed.get("reasoningRequired"):
                        result["reasoning"] = build_reasoning(_eq_r, pot_odds, "fold")
                    result["_debug"]["decided_by"] = "s22_range_veto"
                    result["_debug"]["s22_vetoed_from"] = "call"
        except Exception:
            pass
        try:
            _db = (result.get("_debug") or {}).get("decided_by")
            if (S37_SHADOW_ENABLED and street in ("Flop", "Turn", "River")
                    and to_call == 0 and len(hole) == 2
                    and _db in ("value_bet", "value_raise")):
                _a37 = S.opponent_postflop_actions(table, self_seat.get("seatNumber"))
                _l37 = [_a37.get(sv.get("seatNumber"), []) for sv in certain_seats]
                _t37 = time.time()
                _eqr37, _acc37 = S.estimate_equity_ranged(
                    hole, board, _l37, pending_opponents=num_pending,
                    pending_weight=pending_weight)
                shadow_record_s37(table.get("id") or table.get("tableId"), {
                    "street": street, "equity": round(equity, 4),
                    "equity_ranged": round(_eqr37, 4),
                    "accept_rate": round(_acc37, 3) if _acc37 is not None else None,
                    "secs": round(time.time() - _t37, 2),
                    "decided_by": _db, "action": result.get("action"),
                    "amount": result.get("amount"), "pot": pot,
                    "board_texture": (board_texture(board_raw)[0]
                                      if board_raw else None),
                    "made_category": made_category,
                    "opp_actions": _l37, "num_pending": num_pending,
                    "hole": hole_raw, "board": board_raw})
                result["_debug"]["equity_ranged_bet"] = round(_eqr37, 3)
        except Exception:
            pass
        return result
    except Exception:
        action = "fold" if to_call > 0 else "check"
        if allowed_names and action not in allowed_names:
            for cand in ("check", "call", "fold"):
                if cand in allowed_names:
                    action = cand
                    break
            else:
                action = next(iter(allowed_names), action)
        amount = call_amount if action == "call" else 0
        return {"action": action, "amount": int(amount), "message": "playing it safe",
                "_debug": {"note": "fallback path (parsing/computation error)",
                           "decided_by": "fallback_error_path"}}
