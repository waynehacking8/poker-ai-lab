"""Local Hold'em arena: engine, baseline opponents and match runner.

Importing this package puts ``chipzen_bot`` on ``sys.path`` so the bot's ``nlhe``
package can be imported the same way the Docker image does.
"""

import os
import sys

_BOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chipzen_bot")
if _BOT_DIR not in sys.path:
    sys.path.insert(0, _BOT_DIR)
