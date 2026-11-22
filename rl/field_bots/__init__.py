"""Registry of third-party Chipzen bots playable as SDK-engine opponents: name -> zero-argument factory.

The sources are pinned and reviewed under vendor/ (see vendor/*/PROVENANCE.md and tools/check_vendor.py).
Use them as ``ext:<name>`` in rl.eval_arena and rl.sdk_rollout.
"""

from __future__ import annotations


def _sdkref():
    from .vendor.sdkref.bot import ReferenceBot
    return ReferenceBot()


def _ashwing(cls_name):
    def make():
        from .vendor.ashwing import entry
        return getattr(entry, cls_name)(seed=None)
    return make


def _ashwing_hive():
    from .vendor.ashwing import entry
    from .vendor.ashwing.hive_policy import hive_mind
    return entry.CompetitionBot(strategy=hive_mind)


def _ashwing_value():
    from .vendor.ashwing import entry
    return entry.CompetitionBot()


def _autodidact():
    from .autodidact import AutodidactBot
    return AutodidactBot()


def _autodidact_fast():
    # same code, fewer Monte Carlo trials per decision (2000 -> 200, ranged 600 -> 150) so it is usable in training
    from .autodidact import AutodidactBot
    return AutodidactBot(eq_trials=200, ranged_trials=150)


def _wolf(variant):
    def make():
        from .wolf import WolfBot
        return WolfBot(variant)
    return make


REGISTRY = {
    "sdkref": _sdkref,
    "ashwing_v2": _ashwing("AshwingV2Bot"),
    "ashwing_hive": _ashwing_hive,
    "ashwing_value": _ashwing_value,
    "ashwing_adaptive": _ashwing("AshwingAdaptiveBot"),
    "ashwing_search": _ashwing("AshwingSearchBot"),
    "ashwing": _ashwing("AshwingBot"),
    "autodidact": _autodidact,
    "autodidact_fast": _autodidact_fast,
    "wolf": _wolf("wolf"),
    "wolf_v5": _wolf("wolf_v5"),
    "wolf_v2": _wolf("wolf_v2"),
    "wolf_v1": _wolf("wolf_v1"),
}


def build(name):
    """A new bot for ``ext:<name>`` (the prefix is optional). Module level, so functools.partial(build, name) pickles."""
    return REGISTRY[name[4:] if name.startswith("ext:") else name]()
