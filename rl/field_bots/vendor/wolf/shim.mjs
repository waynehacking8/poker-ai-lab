// JSON-lines shim around the vendored Wolf engine (our code). One JSON object per stdin line, one reply line per
// "decide". No fs, net or child_process: stdin and stdout only. Runs in a --network none container (rl/field_bots/wolf.py).
import { createInterface } from 'node:readline'
import { TableTracker } from './tracker.js'
import { decideAction } from './adapter.js'
import { makeRng } from './rng.js'
import { decide as wolf } from './engine/aiPlayer.js'
import { decide as wolfV5 } from './engine/aiPlayerV5.js'
import { decide as wolfV2 } from './engine/aiPlayerV2.js'
import { decide as wolfV1 } from './engine/aiPlayerV1.js'

const VARIANTS = { wolf, wolf_v5: wolfV5, wolf_v2: wolfV2, wolf_v1: wolfV1 }
const engine = VARIANTS[process.argv[2]]
const budgetMs = Number(process.argv[3] || 100)
if (!engine) throw new Error('unknown variant ' + process.argv[2])
const tracker = new TableTracker()

const rl = createInterface({ input: process.stdin })
rl.on('line', (line) => {
  const m = JSON.parse(line)
  if (m.ev === 'match_start') tracker.onMatch(m.msg)
  else if (m.ev === 'round_start') tracker.newHand(m.msg)
  else if (m.ev === 'round_result') tracker.commitHand(m.msg)
  else if (m.ev === 'decide') {
    const state = m.state
    const rng = makeRng(state.roundId, state.handNumber, state.actionHistory.length)
    const { action, info } = decideAction(state, tracker, rng, engine, budgetMs)
    process.stdout.write(JSON.stringify({ action: action.action, amount: action.amount ?? null, error: info.error ?? null }) + '\n')
  }
})
