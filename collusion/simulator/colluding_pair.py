"""Colluding pair — two agents that share hole-card information.

Behaviour modelled (per ``docs/specifications-phase2.md`` §2):

  1. **Soft-play fold.** When seated against the partner, if the
     colluder's hole card is weaker than the partner's, fold with
     probability ``soft_fold_prob`` whenever folding is legal — even
     when the honest policy would have called or raised. This is the
     primary detectable signal.

  2. **Chip dump.** With probability ``chip_dump_prob``, the colluder
     calls in place of an honest fold — letting the partner's value
     bets win a larger pot. The partner's chips do not actually move
     to the colluder; they move *between the colluders' two accounts*,
     which over many hands is what the chip-flow feature is meant to
     capture.

  3. **No bluff vs partner.** When the colluder holds the weakest
     possible card and the honest policy would have bet, suppress the
     bet — never bluff into a partner who already knows your hand.

When the partner is not seated at the same table (``partner_card`` is
``None``), the colluder reverts to the honest policy.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


from collusion.simulator.honest_player import HonestPlayer


class ColludingPair:
    """One member of a two-player collusion pair.

    The same class is used for both partners — the partner_ids tuple
    identifies the pair, and ``own_id`` distinguishes which side this
    instance represents.
    """

    def __init__(
        self,
        own_id: int,
        partner_id: int,
        policy: Dict[str, np.ndarray],
        soft_fold_prob: float = 0.7,
        chip_dump_prob: float = 0.1,
        rng: np.random.Generator | None = None,
    ):
        if rng is None:
            rng = np.random.default_rng()
        self.own_id = own_id
        self.partner_id = partner_id
        self.soft_fold_prob = soft_fold_prob
        self.chip_dump_prob = chip_dump_prob
        self.rng = rng
        self._honest = HonestPlayer(policy, rng)

    def act(
        self,
        own_card: int,
        partner_card: int | None,
        info_set: str,
        legal_actions: Tuple[str, ...],
    ) -> str:
        if partner_card is None:
            return self._honest.act(info_set, legal_actions)

        weaker_than_partner = own_card < partner_card

        # No-bluff rule: weakest holding never opens a bet against partner.
        # In Kuhn the actions are ('p', 'b'); 'b' is "open bet" when there
        # is no pending bet (info_set ends with '' or 'p').
        if "b" in legal_actions and own_card == 0 and not info_set.endswith("b"):
            return "p"

        # Soft-fold: facing a bet with weaker hand, fold extra often.
        # In Kuhn this is the info-set whose history ends in 'b' (Q:b or J:b).
        facing_bet = info_set.endswith("b")
        if facing_bet and weaker_than_partner and "p" in legal_actions:
            if self.rng.random() < self.soft_fold_prob:
                return "p"
            # Otherwise fall through to chip-dump consideration below.

        # Chip-dump: if honest policy would fold, occasionally call instead
        # to inflate partner's winning pot.
        honest_choice = self._honest.act(info_set, legal_actions)
        if (
            facing_bet
            and weaker_than_partner
            and honest_choice == "p"
            and "b" in legal_actions
            and self.rng.random() < self.chip_dump_prob
        ):
            return "b"
        return honest_choice
