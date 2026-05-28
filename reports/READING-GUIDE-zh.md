# 報告閱讀指南(中文)

英文版的三份報告(`phase1-convergence.md`、`mccfr-scaling.md`、
`phase2-collusion-detection.md`)用嚴謹格式記錄實驗結果。
這份中文指南是**怎麼讀那些報告**的 narrator — 幫你用三種速度切入,
告訴你每張圖的形狀為什麼合理、哪些細節是面試官會抓的、哪些是該誠實
標出的限制。

---

## 給誰看

- **你自己** — 隔幾週回來複習,不用每次重新爬全部報告
- **面試官 / reviewer** — 帶他們快速 navigate 三份報告的價值
- **接手的 AI / 工程師** — 知道每份報告的目的、結構、怎麼引用

英文報告負責「**這是什麼**」;這份中文指南負責「**該怎麼讀、為什麼合理、怎麼防被質疑**」。

---

## reports/ 目錄地圖

| 檔案 | 主題 | 用意 |
|---|---|---|
| [`phase1-convergence.md`](phase1-convergence.md) | CFR 三家族在 Kuhn / Leduc 收斂 | Phase 1 結果報告 |
| [`mccfr-scaling.md`](mccfr-scaling.md) | MCCFR 在大遊戲上贏 enum 的 crossover | Phase 1 補充實驗(回應「MCCFR 是不是廢物」) |
| [`phase2-collusion-detection.md`](phase2-collusion-detection.md) | LightGBM 夥牌偵測 | Phase 2 結果報告 |
| `phase2-metrics-*.json` | Phase 2 機器可讀數據 | 報告引用的 ground truth |
| `phase2-roc-*.png` | Phase 2 ROC 曲線 | 報告圖示 |
| `mccfr-scaling.png` | MCCFR crossover 雙線圖 | 報告圖示 |
| `mccfr-scaling.json` | MCCFR sweep raw 數據 | 報告引用的 ground truth |
| `phase2-metrics.json` | Phase 2 combined 數據 | 報告引用 |
| [`../results/convergence_kuhn.png`](../results/convergence_kuhn.png) | Phase 1 Kuhn 收斂圖 | 報告圖示 |
| [`../results/convergence_leduc.png`](../results/convergence_leduc.png) | Phase 1 Leduc 收斂圖 | 報告圖示 |

---

## 報告一:Phase 1 — CFR 收斂報告

### 它在說什麼

三個 canonical CFR 演算法在兩個玩具游戲(Kuhn 12 info set、Leduc
528 info set)上的實作完整、收斂正確、與文獻一致。

### 30 秒看一張圖

開 [`../results/convergence_leduc.png`](../results/convergence_leduc.png):

- 🟧 **橘色 CFR+ enum** 線最下面(最強)→ expl 0.001 at 1000 iter
- 🔵 **藍色 vanilla CFR enum** 線中間 → expl 0.033 at 1000 iter
- 🟢 **綠色 MCCFR** 線在天上 → expl 0.46 at 200,000 iter

文字結論一句:**CFR+ 比 vanilla 快 35×,符合 Tammelin 2014。MCCFR
在小遊戲上慢,符合 Lanctot 2009。**

### 3 分鐘掃這 4 個地方

| 章節 | 看什麼 |
|---|---|
| §1 What's measured | exploitability 公式 + published Nash value 對照表 |
| §3.1 Kuhn 收斂表 | CFR+ 在 1k iter 達到 expl 0.00018,比 vanilla 快 75× |
| §4.1 Leduc 收斂表 + advantage 表 | 35× advantage 怎麼從 1.6× 慢慢長出來 |
| §6 Bug fix history | RM+ inline floor bug 的發現過程 — 方法論示範 |

### 深讀:每個數字怎麼來

每個 cell 對應一個 deterministic seed run(enum 無 RNG);MCCFR 用 5 個
seed(Kuhn)或 3 個 seed(Leduc)取 mean ± std。**Reproducibility 在
§8** — 跟著貼指令到 terminal,你機器能得到相同數字。

與公認 Nash value 對照:

| 遊戲 | 公認 Nash value | 我們的最佳 game value | 差距 |
|---|---|---|---|
| Kuhn | -1/18 ≈ -0.0556(Kuhn 1950 解析) | -0.0555 at 5000 enum iter | < 0.001 ✓ |
| Leduc | -0.0856(Lanctot 2013 published) | -0.0779 at 1000 CFR+ enum iter | 0.008 ✓ |

差距都在 finite-iter 誤差內,**證明實作正確**(若實作錯,游戲值會偏離 published 0.02+)。

### 紅旗檢查表(看別人類似報告時可以拿來判真假)

| 紅旗 | 意義 |
|---|---|
| ❌ 收斂曲線在某段反彈 | strategy_sum 更新有 bug(沒累加而被覆蓋) |
| ❌ CFR+ 比 vanilla 慢 | 通常是 inline RM+ floor bug — 我們的早期版本 |
| ❌ game value 偏離 published 0.02 以上 | utility 計算錯,或 sign convention 錯 |
| ❌ MCCFR 在 Kuhn 比 enum CFR+ 快 | 違反 Lanctot 2009 預測,要回頭找 bug |
| ✓ 我們的圖全部通過上述檢查 | |

---

## 報告二:MCCFR scaling 補充實驗

### 它在說什麼

Phase 1 報告讓讀者誤以為「MCCFR 廢物」。這份補充用**受控實驗**證明:
**MCCFR 在遊戲夠大時會贏**,完全符合 Lanctot 2009 的 asymptotic-
advantage 預測。

### 30 秒看一張圖

開 [`mccfr-scaling.png`](mccfr-scaling.png):

- 🔵 藍色 **enum CFR+** 線從左下(很強)斜向右上(變弱)— N² 成本爆炸
- 🟧 橘色 **MCCFR** 線幾乎水平 — per-iter 成本與 N 無關
- 兩條線在 **N ≈ 250-300 交叉**

文字結論一句:**N < 250 enum 贏,N ≥ 300 MCCFR 贏。Crossover 是真實
存在的物理現象。**

### 3 分鐘掃這 3 個地方

| 章節 | 看什麼 |
|---|---|
| §2 Results 表 | 8 個 N 值的對戰結果,從 N=3 enum 贏 350× 到 N=400 MCCFR 贏 5× |
| §3 What the chart shows | 兩條線分別為什麼那樣 — enum N² 成本 vs MCCFR 常數成本 |
| §4 對工業界的意義 | Cepheus 用 CFR+,Libratus / Pluribus 用 MCCFR 的原因 |

### 深讀:為什麼這個實驗設計乾淨

| 設計選擇 | 為什麼 |
|---|---|
| 用 N-card Kuhn,不用 Big Leduc | Kuhn 樹結構簡單,**N 加大只增 chance branching,單一變數** |
| N=3 sanity check | 跟 standard Kuhn match 到 1e-9,證明 parameterized 實作正確 |
| 20 秒 wall-time budget | 固定時間下誰學得更好,**公平 head-to-head** |
| 1 deterministic seed for enum + 固定 seed for MCCFR | 完全可重現 |

### 紅旗檢查表

| 紅旗 | 意義 |
|---|---|
| ❌ MCCFR 在 N=3 贏 enum | 違反 Lanctot,有 bug |
| ❌ 兩條線從不交叉 | 受控環境失敗 |
| ❌ Enum 在 N=400 還跑 1000 iter | wall time 統計錯 |
| ✓ 我們的曲線在 N=250-300 乾淨交叉 | |

### 跟真實 Texas Hold'em 的對應

報告 §5 老實標出:**這個實驗不是 NLHE benchmark**。N-card Kuhn 不論
怎麼加牌,info set 數還是線性 O(N),跟 NLHE 的 10¹⁷ info sets 差
無數個數量級。

但「**enum per-iter 成本爆掉 → MCCFR 翻盤**」這個物理現象在
N=300 跟在 NLHE 是**同一個機制**。所以這個玩具實驗等於把「為什麼
Libratus 用 MCCFR」這條因果**實際跑出來給你看**。

---

## 報告三:Phase 2 — 合成夥牌偵測

### 它在說什麼

用 Phase 1 的 CFR 策略當「正直玩家」、注入合成 colluder、訓 LightGBM
偵測器。**頭條 AUC 0.9995 太漂亮**,所以我也報告了 **adversarial
baseline AUC 0.8245**(關掉強訊號的版本)。

### 30 秒看一張圖

開 [`phase2-roc-comparison.png`](phase2-roc-comparison.png):

- 上面 **藍色 ROC** 緊貼左上角 → AUC 0.9995(有 shared-latency 訊號)
- 下面 **紅色 ROC** 在中上區 → AUC 0.8245(沒有 shared-latency 訊號)
- 灰色虛線是 random baseline(AUC 0.5)

文字結論一句:**強訊號下完美,沒強訊號還是有用**。Detector 不靠單一
feature 撐起來。

### 3 分鐘掃這 4 個地方

| 章節 | 看什麼 |
|---|---|
| §1 Pipeline | ASCII 流程圖 — CFR → simulator → features → LightGBM 整條鏈 |
| §2 Behavioural model | 夥牌的 4 條規則 + shared-latency 隱性訊號 |
| §4 Results 雙欄表 | 兩種設定的 AUC、P@R50、feature importance 並列 |
| §5 Finding #1 | decision_time_corr 獨大時 vs 移除後,fold-rate 接手主導 |

### 深讀:為什麼用 stacked sessions(D10)

Spec §6 寫「4-player Kuhn, 10k hands, AUC ≥ 0.85」。但 N=4 只有
C(4,2)=6 對,classifier 訓不出來。我用 **40 個獨立 4-player sessions
× 2k hands** 堆出 240 對,namespacing 避免 collision。這個設計偏離
寫在 [`../docs/design-decisions.md`](../docs/design-decisions.md) D10
條目。

### 深讀:為什麼 chip_flow gain = 0

教科書都說 chip dumping 是夥牌經典訊號。但我們設 `chip_dump_prob=0.1`
(10% 的「該蓋牌時改成跟注」),每對玩家只玩 333 手共同的牌,正常輸贏
的 noise 蓋過 chip dump 訊號。**我沒有調參讓它好看** — 留住 spec
defaults 並誠實標出 finding。

### 紅旗檢查表

| 紅旗 | 意義 |
|---|---|
| ❌ AUC 跨過 random diagonal | classifier 有 bug |
| ❌ 移除 latency 後 AUC 反而變高 | 邏輯不通 |
| ❌ 沒講 caveat,讓人以為 0.9995 是 production-ready | 不誠實 |
| ✓ 我們有 §5 Finding #1 把 caveat 講得很清楚 | |

---

## 三份報告的整體故事

```
        ┌──────────────────────────────────────┐
        │  Phase 1 — CFR 演算法基礎             │
        │  「你會 CFR 全家嗎?」                │
        └────────────────┬─────────────────────┘
                         │ 引用
                         ▼
        ┌──────────────────────────────────────┐
        │  MCCFR scaling 補充                   │
        │  「你懂為什麼工業界選 MCCFR 嗎?」    │
        └──────────────────────────────────────┘

        ┌──────────────────────────────────────┐
        │  Phase 2 — 夥牌偵測 pipeline          │
        │  「你能把 CFR 整合到產品嗎?」        │
        └──────────────────────────────────────┘
```

- Phase 1 是「**你會 CFR 嗎**」的答案
- MCCFR scaling 是「**你懂為什麼工業界選 MCCFR 不選 enum 嗎**」的答案
- Phase 2 是「**你能把 CFR 整合到一個實際 detection 系統嗎**」的答案

三份報告獨立成立,合起來是同一個故事:**「從演算法理解到系統工程的完整鏈」**。

---

## 我們證明了什麼 — 概念對應到具體實驗

| 我會的概念 | 證據在哪 |
|---|---|
| CFR 演算法機制(cf_reach, sign convention) | Phase 1 §1, [`cfr/algorithms/vanilla_cfr.py:84`](../cfr/algorithms/vanilla_cfr.py) |
| RM+ + linear averaging | Phase 1 §6 bug fix history |
| Strategy averaging vs last-iterate | Phase 1 §5 |
| Exploitability metric + two-pass BR | Phase 1 §1 + [`tests/test_exploitability.py`](../tests/test_exploitability.py) |
| MCCFR External Sampling | Phase 1 §4.2 + [`cfr/algorithms/mccfr.py`](../cfr/algorithms/mccfr.py) |
| MCCFR asymptotic advantage | mccfr-scaling.md(整份) |
| Sampling vs enumeration trade-off | Phase 1 §6 + mccfr-scaling §3 |
| 真實夥牌 detection pipeline | Phase 2(整份) |
| 合成資料的誠實對抗 baseline | Phase 2 §4 雙欄表 |
| Player-disjoint train/test 避免 leakage | Phase 2 §3 + [`collusion/models/lgbm_classifier.py`](../collusion/models/lgbm_classifier.py) |
| Bug-finding methodology | Phase 1 §6 + commit `d5c42dd` |
| 文獻 grounded(Tammelin / Lanctot / Bowling) | 三份報告所有 sources |

---

## 我們沒證明的概念 — 誠實標出來

| 概念 | 為什麼沒做 |
|---|---|
| Card abstraction(EHS / OCHS / KMeans 桶化) | 沒做過 bucketing pipeline |
| Action abstraction(NLHE 必須) | 沒碰 |
| Deep CFR / function approximation | tabular only |
| Subgame solving / nested resolving | 只在 references.md 列了 |
| Public Belief States(ReBeL) | 同上 |
| GPU / CUDA implementation | 只有 design doc,沒寫 `.cu` |
| 真實 Texas Hold'em scale | D2 設計排除 |
| 真實 production data | D6 設計排除 |
| Self-play / NFSP | 同上 |
| Multi-player(3+ 桌)CFR | HU only |

面試時碰到上述問題,**老實答「我做過 design,沒實作」或「我讀過 papers,沒踩過坑」** — 比浮誇好。

---

## 一張速查表 — 八個必背數字 + 對應結論

```
公認 Nash values
────────────────────────────────────────────
Kuhn:    -1/18 ≈ -0.0556      (Kuhn 1950 解析)
Leduc:   -0.0856                (Lanctot 2013 published)

Phase 1 結果(canonical enum 變體)
────────────────────────────────────────────
Vanilla CFR enum  1000 iter:  expl 0.033,val -0.079
CFR+ enum         1000 iter:  expl 0.001,val -0.078    ← 35× 比 vanilla 強
MCCFR Leduc       200k iter:  expl 0.47                ← 在小遊戲不利

MCCFR scaling 結果(N-card Kuhn,20 秒 budget)
────────────────────────────────────────────
N=3:    enum 4.4e-6  / mccfr 1.5e-3   → enum 贏 350×
N=300:  enum 1.8e-2  / mccfr 7.8e-3   → MCCFR 翻盤 ✓
N=400:  enum 4.4e-2  / mccfr 8.7e-3   → MCCFR 贏 5×

Phase 2 結果
────────────────────────────────────────────
with    shared latency:  AUC 0.9995   (decision_time_corr 主導)
without shared latency:  AUC 0.8245   (fold-rate 主導,更誠實的數字)
```

**這 8 個數字記住,大部分技術討論都接得起來**。需要查細節再開檔案。

---

## 怎麼回答常見問題

### Q1:「你會 CFR 嗎?」

> 「會。從零實作了 vanilla、MCCFR(External Sampling)、CFR+,包含
> chance-sampling 跟 enum 兩個變體。在 Leduc 上 CFR+ enum 1000 iter
> 達到 expl 0.001,跟 Tammelin 2014 published 一致。實作過程找過
> 兩個 bug(inline RM+ floor + live strategy reading),都是對照
> OpenSpiel reference 找出來的。」

### Q2:「為什麼工業界(Libratus, Pluribus)用 MCCFR?」

> 「我做過 N-card Kuhn 的 scaling 實驗,實測 MCCFR 在 N ≈ 300 開始
> 勝出 enum CFR+。原因是 enum 的 per-iter 成本爆 N²,MCCFR 是常數。
> 實作驗證的內容跟 Lanctot 2009 §1, §6 的 asymptotic-advantage
> claim 完全一致。真實 NLHE info sets 10¹⁷,**遠在 crossover 右邊**,
> 所以只能用 MCCFR。」

### Q3:「夥牌偵測你怎麼做的?」

> 「Phase 1 訓出 CFR 策略當正直玩家,加上合成 colluder(soft-fold +
> chip-dump + no-bluff vs partner)。pipeline 端到端到 LightGBM 二元
> 分類,player-disjoint split。AUC 0.9995 是有 shared-latency 強訊號
> 的版本;**關掉這個訊號後 AUC 還有 0.8245**,fold-rate features 接手
> 主導。我清楚地把這兩種設定並列,**沒有藏 caveat**。」

### Q4:「為什麼不直接用 OpenSpiel?」

> 「OpenSpiel 是 production-grade 的選擇,但對 interview-prep prototype
> 來說會把『你究竟做了什麼』模糊掉。從零實作讓我碰到每個 sign
> convention、reach probability、Leduc round-boundary 的 edge case
> — 也讓我找得到 inline RM+ floor 那個 bug。**這個設計選擇記在 D3**。」

### Q5:「你會 GPU CFR 嗎?」

> **老實答**:「我寫了 Phase 1 design doc(`docs/flashcfr-phase1-design.md`)
> 涵蓋 kernel signature、SoA memory layout、kernel-by-kernel 工作序。
> 沒寫 `.cu` — 因為手邊沒 GPU 且 spec 自己要求 PAUSE for review 才能
> 開始實作。如果接下來有環境,我有完整的工作計畫。」
>
> **不要說**:「我會寫 CUDA」(沒驗證過就別說)

### Q6:「你的實驗夠 robust 嗎?」

> 「Phase 1 enum 變體無 RNG,deterministic;MCCFR 用多 seed(Kuhn
> 5 個 / Leduc 3 個)取 mean ± std,std 都 < 7% mean。Phase 2 seed=0
> 全程 deterministic。CI 在 GitHub Actions 上跑 ruff + bandit + pytest
> matrix(Python 3.11/3.12),每個 PR 都會跑。」

---

## 給自己的「報告維護紀律」

當你修改任何演算法後,**必須做這四件事再 commit**:

1. **跑相關 tests** — `pytest tests/test_xxx.py`,確認沒 regression
2. **重新跑 affected 報告的實驗**(plot script + metrics script)
3. **更新報告裡受影響的數字**(別讓報告跟程式碼說不同話)
4. **commit message 講清楚數字變化** — 「expl 從 0.033 變 0.001 因為修 X」

維護紀律寫進 [`../AGENTS.md`](../AGENTS.md):「**every experiment
produces both a chart and a Markdown report**」。

---

## 一句話結尾

英文報告**負責什麼**,中文指南**負責怎麼讀**。兩者都該誠實 — 沒做的事不要假裝做了,做過的事要展示得清楚。

---

*最後更新:2026-05-28。對應 reports/ 與程式碼 commit `212877a` 之後的狀態。*
