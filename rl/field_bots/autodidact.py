"""Glue: the poker-arena Chipzen entry (chipzen_agent.PokerArenaBot) without its file logging or network runner."""

from chipzen import Bot

from .vendor.autodidact import chipzen_adapter as A
from .vendor.autodidact import live_core as L
from .vendor.autodidact import strategy as S


class AutodidactBot(Bot):
    def __init__(self, eq_trials=None, ranged_trials=None):
        super().__init__()
        self.game_config = {}
        self.match_id = "cz"
        self.eq_trials, self.ranged_trials = eq_trials, ranged_trials

    def on_match_start(self, match_info):
        self.game_config = match_info.get("game_config") or {}
        # the real entry ran one process per match, so its opponent model started empty each match
        S._OPPONENT_STATS.clear()
        S._SEEN_EVENT_IDS.clear()
        if self.eq_trials:
            L.EQ_TRIALS = self.eq_trials
        if self.ranged_trials:
            S.RANGED_TRIALS = self.ranged_trials

    def decide(self, state):
        action, _ = A.decide_chipzen(state, self.game_config, self.match_id)
        return action
