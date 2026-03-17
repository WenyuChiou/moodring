# GRISI 理論基礎：散戶行為心理學 + 資訊來源

**在寫任何一行 code 之前，我們必須先回答兩個問題：**
1. 散戶投資者的心理是如何運作的？（有哪些已驗證的理論？）
2. 散戶從哪裡獲取資訊並做出決策？（各國資料來源是什麼？）

---

## Part 1: 散戶投資心理學理論

### 1.1 Prospect Theory（展望理論）
**提出者**: Kahneman & Tversky (1979)
**核心概念**: 人對「損失」和「獲利」的感受是不對稱的

- **Loss aversion（損失趨避）**: 損失 $100 的痛苦 ≈ 獲利 $250 的快樂。散戶因此：
  - 太早賣掉賺錢的股票（想鎖住獲利）
  - 太晚賣掉虧錢的股票（不願承認虧損）
- **Reference point（參考點）**: 散戶用「買入價」當參考點，不是用當前市場價值
- **Certainty effect（確定性效應）**: 散戶偏好「確定的小獲利」而非「可能的大獲利」

**→ 對 GRISI Agent 設計的意義**:
- Agent 需要知道「散戶在賺錢和虧錢時會有完全不同的行為」
- 當市場從高點回落時，散戶的痛苦反應會比理性預期更強烈
- 各國散戶的 loss aversion 程度不同（日本 > 台灣 > 美國 > 韓國 > 中國）

---

### 1.2 Disposition Effect（處分效應）
**提出者**: Shefrin & Statman (1985)
**核心概念**: 散戶傾向「賣贏保虧」— 太早賣掉漲的，太晚賣掉跌的

- 這是 Prospect Theory 在投資行為的直接應用
- 學術實證：全球散戶都有此傾向，但程度不同
  - **最嚴重**: 中國 A 股散戶（Chen et al., 2007）
  - **嚴重**: 台灣散戶（Barber, Lee, Liu & Odean, 2007 — 用台灣證交所全量數據）
  - **中等**: 美國散戶（Odean, 1998）
  - **相對輕**: 日本機構型散戶（長期持有文化緩和了處分效應）

**→ 對 Agent 設計的意義**:
- 中國/台灣 Agent 在股票下跌時更傾向「死抱不賣」
- 美國 Agent 可能更快認賠（"cut losses" 文化相對強）
- 韓國 Agent 因為槓桿被強制平倉，處分效應被 margin call 打斷

---

### 1.3 Herding Behavior（羊群效應）
**提出者**: Banerjee (1992), Bikhchandani, Hirshleifer & Welch (1992)
**核心概念**: 個人放棄自己的判斷，跟隨群體行動

**三種驅動機制**:
1. **Information cascade（資訊瀑布）**: 「這麼多人都買了，他們一定知道些什麼」
2. **Reputational herding（名聲從眾）**: 「大家都虧沒關係，只有我虧很丟臉」
3. **Social pressure（社會壓力）**: LINE 群組/PTT/雪球上的同儕壓力

**各國羊群程度（有學術實證）**:

| 市場 | 羊群程度 | 學術來源 | 驅動因素 |
|------|---------|---------|---------|
| 🇨🇳 中國 | ⭐⭐⭐⭐⭐ 極端 | Tan, Chiang et al. (2008) | 散戶比例高、資訊不對稱、社群傳播 |
| 🇰🇷 韓國 | ⭐⭐⭐⭐ 很高 | Choe, Kho & Stulz (1999) | FOMO 文化、社群壓力、槓桿放大 |
| 🇹🇼 台灣 | ⭐⭐⭐⭐ 很高 | Barber, Odean et al. (2009) | PTT/LINE 群組、跟單外資 |
| 🇺🇸 美國 | ⭐⭐⭐ 中等 | Wermers (1999) | Reddit/WSB 局部很強、整體中等 |
| 🇯🇵 日本 | ⭐⭐ 低 | Kim & Wei (2002) | 個人主義投資文化、保守不跟風 |

**→ 對 Agent 設計的意義**:
- 中國/韓國 Agent 需要嵌入很強的從眾邏輯：「其他人在買嗎？」是關鍵問題
- 台灣 Agent 的從眾對象是「外資」和「PTT 風向」
- 美國 Agent 在特定社群（WSB）有局部超強羊群，但整體較獨立
- 日本 Agent 幾乎不受別人影響，獨立判斷

---

### 1.4 Overconfidence（過度自信）
**提出者**: DeBondt & Thaler (1995), Barber & Odean (2001)
**核心概念**: 散戶高估自己預測市場的能力

**三種表現**:
1. **Overestimation**: 高估自己選股的能力
2. **Overplacement**: 認為自己比其他投資者更厲害
3. **Overprecision**: 對自己的預測過度確定，不考慮不確定性

**各國散戶的過度自信程度**:
- 🇰🇷 韓國：極端過度自信（年輕世代尤其，「빚투 = 借錢也要投」）
- 🇺🇸 美國：高（"I did my own research" 文化、options YOLO）
- 🇨🇳 中國：高（但更像「賭博心態」而非真的認為自己厲害）
- 🇹🇼 台灣：中等（存股族反而偏保守，但融資戶過度自信）
- 🇯🇵 日本：低（文化上傾向承認自己不懂，保守投資）

**→ 對 Agent 設計的意義**:
- 過度自信 → 交易頻率高 → 成本侵蝕報酬
- 韓國/美國 Agent 在連續獲利後信心膨脹速度最快
- 日本 Agent 即使獲利也不太會加碼

---

### 1.5 FOMO (Fear of Missing Out) / Regret Theory
**提出者**: Loomes & Sugden (1982), 近年 social media 研究
**核心概念**: 「別人在賺我沒賺」的痛苦驅動非理性買入

- **FOMO**: 看到別人賺錢而衝動買入
- **Regret aversion**: 不想事後後悔「當初為什麼沒買」
- **Social media amplification**: 社群平台放大了 FOMO（只看到別人的獲利截圖）

**各國 FOMO 強度**:
- 🇰🇷 韓國：⭐⭐⭐⭐⭐（全球最強，빚투文化的核心驅動力）
- 🇨🇳 中國：⭐⭐⭐⭐⭐（「全民炒股」時期的主要驅動力）
- 🇹🇼 台灣：⭐⭐⭐⭐（LINE 群組「今天買了嗎？」壓力）
- 🇺🇸 美國：⭐⭐⭐（WSB "YOLO" 文化，但有一定理性聲音）
- 🇯🇵 日本：⭐⭐（FOMO 弱，反而有 FOGO — Fear of Getting in）

**→ 對 Agent 設計的意義**:
- FOMO 是散戶在牛市追高的核心心理機制
- Agent 在市場上漲時，FOMO 強的國家（韓中台）會加速追入
- 日本 Agent 反而可能在別人 FOMO 時更謹慎

---

### 1.6 Mental Accounting（心理帳戶）
**提出者**: Thaler (1985, 1999)
**核心概念**: 人在心理上把錢分成不同「帳戶」，每個帳戶有不同風險容忍度

**在各國散戶的表現**:
- 🇹🇼 台灣：「存股帳戶」（穩定配息）vs「短線帳戶」（融資衝浪）— 同一個人有兩種完全不同的投資行為
- 🇯🇵 日本：「NISA 帳戶」（長期、保守）vs「一般帳戶」（稍微積極）
- 🇺🇸 美國：「401k 退休帳戶」（被動指數）vs「Robinhood 帳戶」（YOLO options）
- 🇰🇷 韓國：界限模糊 — 容易把所有資金（包括借來的）都投入同一個高風險策略
- 🇨🇳 中國：「存款帳戶」（極保守）vs「炒股帳戶」（極激進）— 兩極化

**→ 對 Agent 設計的意義**:
- 需要區分散戶用「哪個心理帳戶」在交易
- 台灣 Agent 的「存股」行為和「融資追多」行為需要分開模擬
- 韓國 Agent 的風險沒有帳戶區隔 → 虧損會連鎖

---

### 1.7 Anchoring（錨定效應）
**提出者**: Tversky & Kahneman (1974)
**核心概念**: 人過度依賴第一個接收到的數字作為判斷基準

**在股市的表現**:
- **Price anchoring**: 「這支股票之前到過 200，現在 150 很便宜」（但可能基本面已變）
- **52-week high/low**: 散戶大量使用 52 週高低點做決策
- **Round number anchoring**: 「大盤破萬八」「台積電破千元」

**各國錨定偏好**:
- 🇹🇼 台灣：極度錨定台積電價格 & 大盤萬八/萬九整數關卡
- 🇨🇳 中國：錨定上證 3000 點（「保衛 3000 點」成為 meme）
- 🇺🇸 美國：錨定 ATH (All-Time High)、52-week high
- 🇰🇷 韓國：錨定 Samsung 股價、KOSPI 歷史高點
- 🇯🇵 日本：錨定泡沫時期高點（日經 38,915 — 1989 年，2024 年終於超越）

**→ 對 Agent 設計的意義**:
- 每個國家 Agent 需要有不同的「錨點」
- 台灣 Agent 問：「台積電離歷史高點多遠？」
- 中國 Agent 問：「上證有沒有守住 3000？」

---

### 1.8 Availability Heuristic（可得性捷思）
**提出者**: Tversky & Kahneman (1973)
**核心概念**: 越容易回想起的事件，人就認為越可能發生

**在股市的影響**:
- 最近的大崩盤（2020 COVID, 2022 Fed升息）讓散戶高估「崩盤」機率
- 最近的大漲讓散戶低估風險
- 媒體越常報導的風險，散戶就越擔心（即使統計上不顯著）

**各國受媒體影響程度**:
- 🇨🇳 中國：極高（官媒一篇文章可以翻轉整個市場情緒）
- 🇹🇼 台灣：高（財經 YouTuber 一支影片可以帶動一波買賣）
- 🇰🇷 韓國：高（Naver 熱搜、KakaoTalk 轉發）
- 🇺🇸 美國：中高（CNN/CNBC 恐慌報導有效但有限）
- 🇯🇵 日本：中等（日經報導風格相對冷靜克制）

---

### 1.9 Narrative Economics / Storytelling Bias
**提出者**: Robert Shiller (2019) "Narrative Economics"
**核心概念**: 經濟事件通過「故事」傳播和放大，故事比數據更影響散戶

**各國流行敘事範例**:
- 🇺🇸 US: "AI is the new internet" / "This time is different" / "Fed put"
- 🇹🇼 TW: "台積電是護國神山" / "存股致富" / "外資站在散戶對面"
- 🇨🇳 CN: "國家隊進場了" / "政策底到了" / "美帝陰謀打壓中國股市"
- 🇰🇷 KR: "半導體 super cycle" / "Korean discount 要消失了" / "삼성이면 충분해" (Samsung 就夠了)
- 🇯🇵 JP: "日本終於走出通縮" / "巴菲特買日本" / "新 NISA 改變一切"

**→ 對 Agent 設計的意義**:
- 每個 Agent 需要理解該國當前流行的「投資故事」
- 當故事太普遍時 = 泡沫信號
- Agent 的 prompt 需要包含這些 narrative context

---

### 1.10 Summary: 理論 → Agent 行為映射

| 心理理論 | 🇺🇸 US Agent | 🇹🇼 TW Agent | 🇨🇳 CN Agent | 🇰🇷 KR Agent | 🇯🇵 JP Agent |
|---------|-------------|-------------|-------------|-------------|-------------|
| Loss aversion | 中 (cut loss文化) | 高 (死抱存股) | 低 (賭徒不在乎) | 中 (但槓桿放大) | 很高 (極度保守) |
| Disposition effect | 中 | 高 | 很高 | 中 (被margin打斷) | 中低 |
| Herding | 中 (WSB局部強) | 高 (PTT/LINE) | 極端 | 很高 | 低 |
| Overconfidence | 高 | 中 | 高 (賭博式) | 極端 | 低 |
| FOMO | 中高 | 高 | 很高 | 極端 | 低 |
| Mental accounting | 分明 (401k vs RH) | 分明 (存股vs融資) | 兩極化 | 模糊 (全投) | 分明 (NISA) |
| Anchoring | ATH 導向 | 台積電+整數關卡 | 上證3000 | Samsung | 89年泡沫高點 |
| Availability | 中高 (媒體) | 高 (YouTuber) | 極端 (官媒) | 高 (Naver) | 中 |
| Narrative | 強 (AI story) | 強 (護國神山) | 很強 (政策故事) | 強 (半導體cycle) | 中 (通縮結束) |

---

## Part 2: 各國散戶資訊來源 & 數據平台

### 2.1 🇺🇸 US Retail Investor Information Ecosystem

**交易平台**:
- Robinhood（最代表性的散戶平台）
- Webull（亞裔美國散戶偏好）
- Charles Schwab / Fidelity（較傳統）
- Interactive Brokers（較進階散戶）
- **Tiger Brokers**（華人跨境散戶重要管道）

**資訊來源（影響決策）**:
- Reddit r/WallStreetBets — meme stocks 發源地、YOLO 文化
- Twitter/X FinTwit — 即時行情討論、KOL 帶風向
- TikTok finance — 年輕散戶的入門管道
- CNBC / Bloomberg — 傳統財經媒體
- YouTube finance channels (Meet Kevin, Graham Stephan)
- Discord trading servers — 小圈子交流

**散戶特有數據指標（可量化）**:
- AAII Sentiment Survey（每週散戶看多/看空比例）
- Robinhood Top 100 / most popular stocks
- 0DTE options volume（當日到期選擇權 = 投機指標）
- Reddit sentiment score (API 可取)
- Put/Call ratio (retail-weighted)

**→ 可用免費數據**:
- yfinance: SPY, QQQ, VIX, 個股
- FRED: Fed funds rate, CPI, unemployment
- Reddit API: WSB sentiment (limited free)
- RSS: CNBC, Bloomberg headlines

---

### 2.2 🇹🇼 Taiwan Retail Investor Information Ecosystem

**交易平台**:
- 各大券商 App（元大、凱基、富邦、永豐金）
- **Tiger Brokers（虎頭蜂）** — 跨境投資美股的台灣散戶大量使用
- Fugle（年輕散戶偏好）

**資訊來源（影響決策）**:
- **PTT Stock 板 (批踢踢股板)** — 台灣散戶的靈魂聖地
  - 每日盤後文、標的討論、法人解讀
  - 鄉民情緒 = 台灣散戶情緒的最佳代理指標
- **LINE 投資群組** — 封閉式群組，跟單文化嚴重
- 財經 YouTuber:
  - 柴鼠兄弟 (存股)
  - Mr. Market 市場先生
  - 股癌 Podcast（影響力巨大）
- CMoney / 財報狗 — 財報分析工具
- 三大法人進出表 — 每日必看（TWSE 公開資料）
- **外資買賣超** — 台灣散戶最在意的單一指標

**散戶特有數據指標（可量化）**:
- **融資餘額** / 融資維持率（TWSE 公開）— 散戶槓桿水位
- **三大法人買賣超**（每日公佈）
- **當沖比率**（短線投機指標）
- 台積電股價（台股的「錨」）
- 集保戶股權分散表（可看散戶持股變化）

**→ 可用免費數據**:
- yfinance: ^TWII (加權指數), 2330.TW (台積電)
- TWSE 開放資料: 三大法人、融資餘額、當沖比率
- RSS: 經濟日報、工商時報

---

### 2.3 🇨🇳 China A-Share Retail Information Ecosystem

**交易平台**:
- 東方財富 (East Money) — 最大散戶平台
- 同花順 (10jqka)
- 通達信
- **Tiger Brokers (老虎證券)** — 中國散戶投資港美股的主要管道

**資訊來源（影響決策）**:
- **東方財富股吧** — 類似 PTT，每支股票都有討論區
- **雪球 (Xueqiu)** — 中國的 seeking alpha，KOL 影響力大
- **微博財經 KOL** — 帶節奏
- 新華社 / 人民日報 — **政策信號源**（極其重要）
  - 人民日報一篇社論可以讓市場漲/跌 5%+
- 央視財經頻道
- 各種「老師」直播間 — 非法薦股但影響力大

**散戶特有數據指標（可量化）**:
- **新增開戶數** — 散戶入場速度（經典的頂部指標）
- **兩融餘額（融資融券）** — 散戶槓桿
- **北向資金（滬港通/深港通）** — 外資風向標，散戶拿來跟單
- 漲停/跌停家數比 — 情緒極端指標
- 上證成交量 — 量能放大 = 散戶活躍

**→ 可用免費數據**:
- yfinance: 000001.SS (上證), 399001.SZ (深成指)
- Tushare (免費 tier): A 股更詳細數據
- RSS: 新華社、經濟觀察報

---

### 2.4 🇰🇷 Korea Retail Information Ecosystem

**交易平台**:
- 키움증권 (Kiwoom) — 最大散戶券商
- 삼성증권 (Samsung Securities)
- NH투자증권
- **Tiger Brokers** — 韓國散戶投資海外的管道之一

**資訊來源（影響決策）**:
- **Naver Finance (네이버 금융)** — 韓國散戶的首頁
  - 每支股票的討論區 = 韓國版股吧
  - Naver 搜尋趨勢 = 散戶興趣指標
- **KakaoTalk 投資群組** — 類似 LINE 群組，封閉式跟單
- YouTube 股票頻道 — 韓國散戶依賴度很高
- **한국경제 (韓國經濟日報)** / 매일경제
- Seeking Alpha Korea

**散戶特有數據指標（可量化）**:
- **信用融資餘額** — 韓國散戶槓桿全球最高
- **개인 순매수 (散戶淨買超)** — KRX 每日公佈
- **외국인 순매수 (外資淨買超)** — 散戶反向指標
- Samsung Electronics 股價 — 韓國散戶的「錨」
- **빚투 (借錢投資) 餘額** — 最核心的風險指標

**→ 可用免費數據**:
- yfinance: ^KS11 (KOSPI), 005930.KS (Samsung)
- KRX 公開資料: 投資者別買賣超
- RSS: 한국경제, 매일경제

---

### 2.5 🇯🇵 Japan Retail Information Ecosystem

**交易平台**:
- SBI証券 — 日本最大網路券商
- 楽天証券 (Rakuten Securities)
- マネックス証券 (Monex)
- **Tiger Brokers (タイガーブローカーズ)** — 日本散戶投資海外

**資訊來源（影響決策）**:
- **日本経済新聞 (日經)** — 最權威、最多人看
- **Yahoo! Finance Japan** — 散戶的主要免費工具
- Twitter Japan 投資クラスタ — 但影響力不如美國 FinTwit
- **投資相關書籍** — 日本散戶文化偏好「讀書學習」而非社群跟風
- 四季報 (Shikiho) — 每季出版的企業報告，散戶必讀
- **株主優待 (股東優惠)** 網站 — 日本獨特的散戶驅動力

**散戶特有數據指標（可量化）**:
- **新 NISA 口座開設數** — 新世代散戶入場指標
- USDJPY 匯率 — 日本散戶對匯率極度敏感
- **信用取引残高 (融資餘額)** — 日本散戶槓桿（但水位相對低）
- **投資信託 (fund) 資金流入** — 間接散戶指標
- **海外投資比例** — carry trade 的代理指標

**→ 可用免費數據**:
- yfinance: ^N225 (日經), USDJPY=X
- JPX 公開資料: 投資部門別賣買狀況
- RSS: 日經新聞

---

### 2.6 Tiger Brokers（老虎證券）的特殊角色

Tiger Brokers 值得特別提出，因為它是 **跨國散戶的共同平台**：

| 市場 | Tiger 的角色 | 用戶特徵 |
|------|------------|---------|
| 🇨🇳 中國 | 投資港美股的主要管道 | 較進階的中國散戶，想逃離 A 股的人 |
| 🇹🇼 台灣 | 投資美股的熱門選擇 | 年輕世代、想投資海外的科技股愛好者 |
| 🇸🇬 新加坡 | 主要券商之一 | 東南亞華人投資者 |
| 🇺🇸 美國 | 華裔散戶偏好 | 在美華人，跨境視角 |

**Tiger Brokers 提供的獨特數據**:
- Tiger 用戶持倉排行 — 反映跨境華人散戶偏好
- Tiger 社區討論 — 多語言散戶對話
- Tiger 用戶交易行為統計

**→ 對 GRISI 的意義**:
- Tiger 用戶代表了一個獨特群體：**有跨境視野的亞洲散戶**
- 可以考慮加一個「Tiger / 跨境散戶 Agent」作為第 6 個 Agent
- Tiger 社區數據可以作為驗證：看我們的 Agent 預測是否與 Tiger 用戶實際行為一致

---

## Part 3: 理論 → Agent Prompt 設計原則

### 每個 Agent 的 Persona Prompt 必須包含：

```
1. 身份設定
   - 你是[國家]的一個典型散戶投資者
   - 你的年齡、收入水平、投資經驗
   - 你常用的交易平台和資訊來源

2. 心理偏差設定（根據理論）
   - Loss aversion 程度: [低/中/高/極高]
   - Herding 傾向: [低/中/高/極端]
   - FOMO 程度: [低/中/高/極端]
   - Overconfidence: [低/中/高/極端]
   - 錨定偏好: [具體錨點描述]

3. 決策框架
   - 你做投資決策時，優先看什麼？（排序）
   - 什麼情況你會買入？（觸發條件）
   - 什麼情況你會賣出？（觸發條件）
   - 你目前的「投資故事」是什麼？

4. 當前市場數據（系統注入）
   - 價格、技術指標、宏觀數據
   - 你的國家的特定指標（融資餘額、法人進出等）
   - 近期新聞標題

5. 輸出格式
   - Sentiment Score (0-100)
   - Action (BUY / HOLD / SELL)
   - Confidence (0-100)
   - Reasoning (用該國散戶的語氣和邏輯)
   - Emotion tag (FOMO / Fear / Greed / Calm / Panic / Euphoria)
   - Key factors (list)
```

---

## Part 4: 數據可行性總結

### 免費可取得的數據（MVP 足夠）

| 數據類型 | 來源 | 覆蓋市場 | 更新頻率 |
|---------|------|---------|---------|
| 股價/成交量 | yfinance | 全部 5 國 | 即時 (delayed 15min) |
| 技術指標 | 自行計算 (ta-lib / pandas_ta) | 全部 5 國 | 日頻 |
| 美國宏觀 | FRED API | 🇺🇸 | 月/季 |
| 台灣法人進出 | TWSE OpenData | 🇹🇼 | 日頻 |
| 融資餘額 (台) | TWSE OpenData | 🇹🇼 | 日頻 |
| 新聞標題 | RSS feeds | 全部 5 國 | 即時 |
| VIX | yfinance | 🇺🇸 (global proxy) | 即時 |

### 付費/進階數據（Phase 3+）

| 數據類型 | 來源 | 用途 |
|---------|------|------|
| Reddit sentiment | Reddit API (limited free) | 🇺🇸 散戶情緒驗證 |
| Tiger 社區 | Tiger Open API | 跨境散戶行為 |
| 韓國融資餘額 | KRX premium | 🇰🇷 槓桿指標 |
| A 股開戶數 | Tushare pro | 🇨🇳 散戶入場指標 |

---

## References

1. Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263-291.
2. Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance*, 40(3), 777-790.
3. Barber, B., & Odean, T. (2001). Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment. *Quarterly Journal of Economics*, 116(1), 261-292.
4. Barber, B., Lee, Y., Liu, Y., & Odean, T. (2007). Is the Aggregate Investor Reluctant to Realise Losses? Evidence from Taiwan. *European Financial Management*, 13(3), 423-447.
5. Tan, L., Chiang, T.C., Mason, J.R., & Nelling, E. (2008). Herding behavior in Chinese stock markets. *Pacific-Basin Finance Journal*, 16(1-2), 61-77.
6. Shiller, R. (2019). *Narrative Economics: How Stories Go Viral and Drive Major Economic Events*. Princeton University Press.
7. Choe, H., Kho, B.C., & Stulz, R.M. (1999). Do foreign investors destabilize stock markets? The Korean experience in 1997. *Journal of Financial Economics*, 54(2), 227-264.
8. Grinblatt, M., & Keloharju, M. (2001). How Distance, Language, and Culture Influence Stockholdings and Trades. *Journal of Finance*, 56(3), 1053-1073.
9. Chui, A., Titman, S., & Wei, K.C. (2010). Individualism and Momentum around the World. *Journal of Finance*, 65(1), 361-392.
10. Thaler, R. (1999). Mental Accounting Matters. *Journal of Behavioral Decision Making*, 12(3), 183-206.

---

*This document serves as the theoretical foundation for GRISI agent design.*
*All agent persona prompts must be grounded in these theories.*
*Last updated: 2026-03-16*
