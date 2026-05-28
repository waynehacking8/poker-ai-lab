"""Simulator subpackage — agents and game runner for synthetic Kuhn sessions."""

from collusion.simulator.colluding_pair import ColludingPair
from collusion.simulator.game_runner import run_session
from collusion.simulator.honest_player import HonestPlayer

__all__ = ["ColludingPair", "HonestPlayer", "run_session"]
