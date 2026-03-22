/**
 * Mispricing Detection Module for Trading Dashboards
 *
 * This module provides functionalities to detect mispricing in financial instruments (SPY, QQQ)
 * based on probabilistic scenarios, analyze contributions, simulate scenario changes,
 * track historical trends, and suggest trading strategies.
 *
 * All display strings are in Traditional Chinese.
 */

// --- Constants ---
const SIGNAL_LEVELS = {
    SEVERELY_OVERPRICED: { min: 10, max: Infinity, zh: '嚴重高估' },
    OVERPRICED: { min: 5, max: 10, zh: '高估' },
    SLIGHTLY_OVERPRICED: { min: 2, max: 5, zh: '輕微高估' },
    FAIR: { min: -2, max: 2, zh: '合理' },
    SLIGHTLY_UNDERPRICED: { min: -5, max: -2, zh: '輕微低估' },
    UNDERPRICED: { min: -Infinity, max: -5, zh: '低估' },
};

const STRATEGY_PARAMS = {
    'bearish vertical spreads (put debit spreads)': { delta: '0.15-0.30', DTE: '30-45', zh: '看跌垂直價差 (賣權多頭價差)' },
    'neutral-bearish (iron condors with downside bias)': { delta: '0.10-0.20', DTE: '30-45', zh: '中性偏空 (向下傾斜的鐵鷹價差)' },
    'theta strategies (short strangles, iron butterflies)': { delta: '0.10-0.20', DTE: '30-45', zh: '時間價值策略 (空方價差, 鐵蝶式價差)' },
    'bullish vertical spreads (call debit spreads)': { delta: '0.15-0.30', DTE: '30-45', zh: '看漲垂直價差 (買權多頭價差)' },
};

// --- State ---
// Stores historical mispricing data for trend analysis.
// Each entry: { timestamp: string, mispricing_spy_pct: number, mispricing_qqq_pct: number, signal_spy: string, signal_qqq: string, strategy: string }
let historicalMispricing = [];

// --- Helper Functions ---

/**
 * Checks if a market price is valid (a positive number).
 * @param {number} price - The price to check.
 * @returns {boolean} True if the price is valid, false otherwise.
 */
function isMarketPriceValid(price) {
    return typeof price === 'number' && price > 0;
}

/**
 * Calculates the weighted average of target values based on probabilities.
 * @param {number[]} targets - An array of target values.
 * @param {number[]} probabilities - An array of probabilities corresponding to the targets.
 * @returns {number} The calculated weighted average.
 */
function calculateWeightedAverage(targets, probabilities) {
    if (!Array.isArray(targets) || !Array.isArray(probabilities) || targets.length !== probabilities.length || probabilities.length === 0) {
        return 0;
    }
    let weightedSum = 0;
    let totalProb = 0;
    for (let i = 0; i < targets.length; i++) {
        weightedSum += targets[i] * probabilities[i];
        totalProb += probabilities[i];
    }
    // Normalize if probabilities don't sum exactly to 1, to prevent issues.
    if (totalProb === 0) return 0;
    return weightedSum / totalProb;
}

/**
 * Determines the mispricing signal level and its Traditional Chinese description.
 * @param {number} mispricingPct - The calculated mispricing percentage.
 * @returns {{level: string, zh: string, pct: number}} An object containing the signal level, its Chinese translation, and the percentage.
 */
function getSignal(mispricingPct) {
    for (const key in SIGNAL_LEVELS) {
        const level = SIGNAL_LEVELS[key];
        if (mispricingPct >= level.min && mispricingPct <= level.max) {
            return { level: key, zh: level.zh, pct: mispricingPct };
        }
    }
    // Fallback for edge cases not covered by finite ranges (e.g., Infinity, -Infinity).
    if (mispricingPct >= SIGNAL_LEVELS.SEVERELY_OVERPRICED.min) return { level: 'SEVERELY_OVERPRICED', zh: SIGNAL_LEVELS.SEVERELY_OVERPRICED.zh, pct: mispricingPct };
    if (mispricingPct <= SIGNAL_LEVELS.UNDERPRICED.max) return { level: 'UNDERPRICED', zh: SIGNAL_LEVELS.UNDERPRICED.zh, pct: mispricingPct };
    return { level: 'UNKNOWN', zh: '未知', pct: mispricingPct };
}

/**
 * Suggests a trading strategy based on the average mispricing percentage.
 * @param {number} mispricingPctSpy - The mispricing percentage for SPY.
 * @param {number} mispricingPctQqq - The mispricing percentage for QQQ.
 * @returns {{key: string, zh: string, delta: string, DTE: string} | null} - The suggested strategy details or null if no strategy is recommended.
 */
function getStrategy(mispricingPctSpy, mispricingPctQqq) {
    // Use the average mispricing for strategy suggestion.
    const avgMispricing = (mispricingPctSpy + mispricingPctQqq) / 2;

    let strategyKey = null;

    if (avgMispricing > SIGNAL_LEVELS.OVERPRICED.min) { // Covers >5% (SEVERELY_OVERPRICED and OVERPRICED)
        strategyKey = 'bearish vertical spreads (put debit spreads)';
    } else if (avgMispricing >= SIGNAL_LEVELS.SLIGHTLY_OVERPRICED.min && avgMispricing <= SIGNAL_LEVELS.SLIGHTLY_OVERPRICED.max) { // 2-5%
        strategyKey = 'neutral-bearish (iron condors with downside bias)';
    } else if (avgMispricing >= SIGNAL_LEVELS.FAIR.min && avgMispricing <= SIGNAL_LEVELS.FAIR.max) { // -2 to 2%
        strategyKey = 'theta strategies (short strangles, iron butterflies)';
    } else if (avgMispricing < SIGNAL_LEVELS.SLIGHTLY_UNDERPRICED.max) { // Covers <-2% (SLIGHTLY_UNDERPRICED and UNDERPRICED)
        strategyKey = 'bullish vertical spreads (call debit spreads)';
    }

    if (strategyKey && STRATEGY_PARAMS[strategyKey]) {
        const params = STRATEGY_PARAMS[strategyKey];
        return {
            key: strategyKey,
            zh: params.zh,
            delta: params.delta,
            DTE: params.DTE,
        };
    }
    return null; // No strategy suggestion
}

// --- Core Functions ---

/**
 * Calculates the expected prices and mispricing percentage for SPY and QQQ based on scenarios.
 * @param {Array<{prob: number, spy_target: number, qqq_target: number}>} scenarios - Array of probability-weighted scenarios.
 * @param {{spy: number, qqq: number}} marketPrices - Current market prices for SPY and QQQ.
 * @returns {{expected_spy: number, expected_qqq: number, mispricing_spy_pct: number, mispricing_qqq_pct: number, signal_spy: {level: string, zh: string, pct: number}, signal_qqq: {level: string, zh: string, pct: number}}}
 */
function calculateMispricing(scenarios, marketPrices) {
    if (!Array.isArray(scenarios) || scenarios.length === 0) {
        return {
            expected_spy: 0,
            expected_qqq: 0,
            mispricing_spy_pct: 0,
            mispricing_qqq_pct: 0,
            signal_spy: { level: 'UNKNOWN', zh: '未知', pct: 0 },
            signal_qqq: { level: 'UNKNOWN', zh: '未知', pct: 0 },
        };
    }

    const spyTargets = scenarios.map(s => s.spy_target);
    const qqqTargets = scenarios.map(s => s.qqq_target);
    const probabilities = scenarios.map(s => s.prob);

    const expected_spy = calculateWeightedAverage(spyTargets, probabilities);
    const expected_qqq = calculateWeightedAverage(qqqTargets, probabilities);

    let mispricing_spy_pct = 0;
    let mispricing_qqq_pct = 0;

    if (isMarketPriceValid(marketPrices.spy)) {
        mispricing_spy_pct = ((marketPrices.spy - expected_spy) / marketPrices.spy) * 100;
    }
    if (isMarketPriceValid(marketPrices.qqq)) {
        mispricing_qqq_pct = ((marketPrices.qqq - expected_qqq) / marketPrices.qqq) * 100;
    }

    const signal_spy = getSignal(mispricing_spy_pct);
    const signal_qqq = getSignal(mispricing_qqq_pct);

    return {
        expected_spy,
        expected_qqq,
        mispricing_spy_pct,
        mispricing_qqq_pct,
        signal_spy,
        signal_qqq,
    };
}

/**
 * Analyzes the contribution of each scenario to the total mispricing for SPY and QQQ.
 * Identifies the biggest driver scenario for each instrument.
 * @param {Array<{prob: number, spy_target: number, qqq_target: number}>} scenarios - Array of probability-weighted scenarios.
 * @param {{spy: number, qqq: number}} marketPrices - Current market prices for SPY and QQQ.
 * @returns {{contributions: Array<{scenario_index: number, prob: number, mispricing_pct_spy: number, mispricing_pct_qqq: number, driver_of_mispricing: string}>, biggest_driver_spy: string, biggest_driver_qqq: string}}
 */
function analyzeContributions(scenarios, marketPrices) {
    if (!Array.isArray(scenarios) || scenarios.length === 0 || !isMarketPriceValid(marketPrices.spy) || !isMarketPriceValid(marketPrices.qqq)) {
        return {
            contributions: [],
            biggest_driver_spy: 'N/A',
            biggest_driver_qqq: 'N/A',
        };
    }

    const contributions = [];
    let maxContributionSpy = -Infinity;
    let maxContributionSpyIndex = -1;
    let maxContributionQqq = -Infinity;
    let maxContributionQqqIndex = -1;

    for (let i = 0; i < scenarios.length; i++) {
        const scenario = scenarios[i];
        const { prob } = scenario;

        // Contribution to SPY mispricing = probability * (market - target) / market * 100
        const contribution_spy = prob * ((marketPrices.spy - scenario.spy_target) / marketPrices.spy) * 100;
        // Contribution to QQQ mispricing = probability * (market - target) / market * 100
        const contribution_qqq = prob * ((marketPrices.qqq - scenario.qqq_target) / marketPrices.qqq) * 100;

        const currentContribution = {
            scenario_index: i,
            prob: prob,
            mispricing_pct_spy: contribution_spy,
            mispricing_pct_qqq: contribution_qqq,
            driver_of_mispricing: '', // Will be populated after loop
        };
        contributions.push(currentContribution);

        // Track the largest positive contribution for each
        if (contribution_spy > maxContributionSpy) {
            maxContributionSpy = contribution_spy;
            maxContributionSpyIndex = i;
        }
        if (contribution_qqq > maxContributionQqq) {
            maxContributionQqq = contribution_qqq;
            maxContributionQqqIndex = i;
        }
    }

    // Mark the biggest driver in the contributions array and return summary strings
    let biggest_driver_spy_str = 'N/A';
    if (maxContributionSpyIndex !== -1) {
        contributions[maxContributionSpyIndex].driver_of_mispricing = 'SPY 的主要驅動因素';
        biggest_driver_spy_str = `場景 ${maxContributionSpyIndex}`;
    }

    let biggest_driver_qqq_str = 'N/A';
    if (maxContributionQqqIndex !== -1) {
        contributions[maxContributionQqqIndex].driver_of_mispricing = 'QQQ 的主要驅動因素';
        biggest_driver_qqq_str = `場景 ${maxContributionQqqIndex}`;
    }

    return {
        contributions,
        biggest_driver_spy: biggest_driver_spy_str,
        biggest_driver_qqq: biggest_driver_qqq_str,
    };
}

/**
 * Simulates changing the probability of a specific scenario and redistributes the remaining probability
 * proportionally among other scenarios. Returns the new expected prices and mispricing percentages,
 * along with the deltas from the original calculation.
 *
 * @param {number} scenarioId - The index of the scenario whose probability is to be changed.
 * @param {number} newProb - The new probability for the specified scenario (must be between 0 and 1).
 * @param {Array<{prob: number, spy_target: number, qqq_target: number}>} scenarios - The current array of scenarios.
 * @param {{spy: number, qqq: number}} marketPrices - Current market prices for SPY and QQQ.
 * @returns {{new_expected_spy: number, new_mispricing_spy_pct: number, delta_expected_spy: number, new_expected_qqq: number, new_mispricing_qqq_pct: number, delta_expected_qqq: number} | null} - The simulation results or null if inputs are invalid.
 */
function whatIfProbChange(scenarioId, newProb, scenarios, marketPrices) {
    if (!Array.isArray(scenarios) || scenarios.length === 0 || scenarioId < 0 || scenarioId >= scenarios.length || newProb < 0 || newProb > 1) {
        console.error("Invalid input for whatIfProbChange: scenarioId out of bounds or newProb not between 0 and 1.");
        return null;
    }

    // Ensure probabilities sum to approximately 1 initially for accurate redistribution calculation.
    let currentTotalProb = scenarios.reduce((sum, s) => sum + s.prob, 0);
    const normalizedScenarios = scenarios.map(s => ({ ...s, prob: s.prob / (currentTotalProb || 1) }));

    const originalScenarioProb = normalizedScenarios[scenarioId].prob;
    const newRemainingProb = 1.0 - newProb;

    if (newRemainingProb < 0) {
        console.error("Error in probability calculation: newRemainingProb is negative.");
        return null;
    }

    const otherScenariosOriginalProbs = normalizedScenarios
        .filter((_, index) => index !== scenarioId)
        .map(s => s.prob);
    const sumOfOtherOriginalProbs = otherScenariosOriginalProbs.reduce((sum, p) => sum + p, 0);

    let newScenarios = normalizedScenarios.map((s, index) => {
        if (index === scenarioId) {
            return { ...s, prob: newProb };
        }
        return { ...s };
    });

    // Distribute the newRemainingProb proportionally to other scenarios.
    if (sumOfOtherOriginalProbs > 1e-9) {
        newScenarios = newScenarios.map((s, index) => {
            if (index !== scenarioId) {
                const originalProb = normalizedScenarios[index].prob;
                const newProbForOther = newRemainingProb * (originalProb / sumOfOtherOriginalProbs);
                return { ...s, prob: newProbForOther };
            }
            return s;
        });
    } else if (newRemainingProb > 1e-9 && scenarios.length > 1) {
        console.warn("Sum of other original probabilities is zero. Redistribution might not be proportional or complete.");
    }

    // Final re-normalization to ensure probabilities strictly sum to 1.
    const finalTotalProb = newScenarios.reduce((sum, s) => sum + s.prob, 0);
    if (finalTotalProb > 1e-9) {
        newScenarios = newScenarios.map(s => ({ ...s, prob: s.prob / finalTotalProb }));
    } else {
        console.error("Final total probability is zero after redistribution. Cannot proceed.");
        return null;
    }

    const originalMispricingResult = calculateMispricing(normalizedScenarios, marketPrices);
    const newMispricingResult = calculateMispricing(newScenarios, marketPrices);

    const delta_expected_spy = newMispricingResult.expected_spy - originalMispricingResult.expected_spy;
    const delta_expected_qqq = newMispricingResult.expected_qqq - originalMispricingResult.expected_qqq;

    return {
        new_expected_spy: newMispricingResult.expected_spy,
        new_mispricing_spy_pct: newMispricingResult.mispricing_spy_pct,
        delta_expected_spy: delta_expected_spy,
        new_expected_qqq: newMispricingResult.expected_qqq,
        new_mispricing_qqq_pct: newMispricingResult.mispricing_qqq_pct,
        delta_expected_qqq: delta_expected_qqq,
    };
}

/**
 * Appends the current mispricing data and suggested strategy to the historical log.
 * @param {Array<{prob: number, spy_target: number, qqq_target: number}>} scenarios - Array of probability-weighted scenarios.
 * @param {{spy: number, qqq: number}} marketPrices - Current market prices for SPY and QQQ.
 */
function appendHistory(scenarios, marketPrices) {
    const mispricingResult = calculateMispricing(scenarios, marketPrices);
    const strategy = getStrategy(mispricingResult.mispricing_spy_pct, mispricingResult.mispricing_qqq_pct);

    historicalMispricing.push({
        timestamp: new Date().toISOString(),
        mispricing_spy_pct: mispricingResult.mispricing_spy_pct,
        mispricing_qqq_pct: mispricingResult.mispricing_qqq_pct,
        signal_spy: mispricingResult.signal_spy.level,
        signal_qqq: mispricingResult.signal_qqq.level,
        strategy: strategy ? strategy.zh : '無建議',
    });
}

/**
 * Analyzes the historical trend of mispricing for SPY and QQQ.
 * @param {Array<{timestamp: string, mispricing_spy_pct: number, mispricing_qqq_pct: number, signal_spy: string, signal_qqq: string, strategy: string}>} history - The array of historical mispricing data.
 * @param {number} [tolerance=1.0] - Tolerance percentage to consider prices "at the same level".
 * @returns {{direction_spy: string, rate_of_change_spy: number, days_at_current_level_spy: number, direction_qqq: string, rate_of_change_qqq: number, days_at_current_level_qqq: number}}
 */
function analyzeTrend(history, tolerance = 1.0) {
    if (!Array.isArray(history) || history.length < 2) {
        return {
            direction_spy: 'N/A', rate_of_change_spy: 0, days_at_current_level_spy: 0,
            direction_qqq: 'N/A', rate_of_change_qqq: 0, days_at_current_level_qqq: 0,
        };
    }

    const numDays = history.length;
    const spyPrices = history.map(h => h.mispricing_spy_pct);
    const qqqPrices = history.map(h => h.mispricing_qqq_pct);

    // Rate of Change: difference between last and first divided by number of intervals
    const rate_of_change_spy = (spyPrices[numDays - 1] - spyPrices[0]) / (numDays - 1);
    const rate_of_change_qqq = (qqqPrices[numDays - 1] - qqqPrices[0]) / (numDays - 1);

    // Direction: positive rate = worsening (more overpriced or less underpriced), negative = improving
    const direction_spy = rate_of_change_spy > 0.1 ? '改善中' : (rate_of_change_spy < -0.1 ? '惡化中' : '持平');
    const direction_qqq = rate_of_change_qqq > 0.1 ? '改善中' : (rate_of_change_qqq < -0.1 ? '惡化中' : '持平');

    // Days at current level: consecutive days from end within tolerance
    const currentSpyMispricing = spyPrices[numDays - 1];
    const currentQqqMispricing = qqqPrices[numDays - 1];
    let days_at_current_level_spy = 0;
    let days_at_current_level_qqq = 0;

    for (let i = numDays - 1; i >= 0; i--) {
        if (Math.abs(spyPrices[i] - currentSpyMispricing) <= tolerance) {
            days_at_current_level_spy++;
        } else {
            break;
        }
    }
    for (let i = numDays - 1; i >= 0; i--) {
        if (Math.abs(qqqPrices[i] - currentQqqMispricing) <= tolerance) {
            days_at_current_level_qqq++;
        } else {
            break;
        }
    }

    return {
        direction_spy,
        rate_of_change_spy,
        days_at_current_level_spy,
        direction_qqq,
        rate_of_change_qqq,
        days_at_current_level_qqq,
    };
}

/**
 * Suggests a trading strategy based on mispricing magnitude and direction for SPY and QQQ.
 * @param {number} mispricingPctSpy - Mispricing percentage for SPY.
 * @param {number} mispricingPctQqq - Mispricing percentage for QQQ.
 * @returns {{key: string, zh: string, delta: string, DTE: string} | null}
 */
function suggestStrategy(mispricingPctSpy, mispricingPctQqq) {
    return getStrategy(mispricingPctSpy, mispricingPctQqq);
}

/**
 * Resets the historical mispricing data.
 */
function resetHistory() {
    historicalMispricing = [];
}

/**
 * Retrieves the current historical mispricing data.
 * @returns {Array} The historical data (copy).
 */
function getHistory() {
    return [...historicalMispricing];
}


// --- Module Exports ---
const MispricingModule = {
    // Constants
    SIGNAL_LEVELS: Object.fromEntries(Object.entries(SIGNAL_LEVELS).map(([key, value]) => [key, { min: value.min, max: value.max, zh: value.zh }])),
    STRATEGY_PARAMS: Object.fromEntries(Object.entries(STRATEGY_PARAMS).map(([key, value]) => [key, { delta: value.delta, DTE: value.DTE, zh: value.zh }])),

    // State management
    getHistory,
    resetHistory,

    // Core functionalities
    calculateMispricing,
    analyzeContributions,
    whatIfProbChange,
    appendHistory,
    analyzeTrend,
    suggestStrategy,
};

// For embedding in HTML via <script> tag:
// window.MispricingModule = MispricingModule;
//
// For ES modules:
// export default MispricingModule;
