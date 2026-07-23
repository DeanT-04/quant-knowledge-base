## From Impermanent Loss to Sustainable Gain: Quantifying Profitability Zones for Liquidity Providers on DEX

Ignat Melnikov ∗ , Roman Vlasov † , Vladimir Gorgadze †‡ , Andrey Seoev § , Yury Yanovich ∗ ∗ Skolkovo Institute of Science and Technology, Moscow, Russia † Moscow Institute of Physics and Technology, Moscow, Russia ‡ IDEAS: Inter-Disciplinary &amp; Advanced Studies Center, Moscow, Russia §

MEV-X, Moscow, Russia

Abstract -Decentralized Finance (DeFi) is a rapidly evolving segment of blockchain technology that enables a transformative approach to financial services through Web3 applications. By leveraging smart contracts, DeFi allows developers to build flexible and innovative financial instruments. Among the most prominent DeFi primitives by liquidity are decentralized exchange (DEX) swap protocols (such as Uniswap, Curve, and Balancer) that facilitate fast token-to-token exchanges. However, new exchange mechanisms also introduce new market inefficiencies that can be systematically exploited by arbitrageurs. This paper focuses on swap protocols based on the Automated Market Maker (AMM), where the product of reserves is preserved as an invariant. We analyze the interaction between arbitrageurs and AMM liquidity pools and develop a mathematical model grounded in empirical pool configurations. Using this model, we derive bounds on the joint revenue of liquidity providers (LPs) and arbitrageurs, propose a method to estimate the expected number of blocks until the occurrence of Impermanent Loss (IL), and obtain a lower bound on the pool fee required to achieve a fixed target probability of staying in the Impermanent Gain (IG) zone within a block. The proposed framework extends existing LP risk-assessment methodologies by quantifying symbiotic profitability zones, providing a principled basis for fee selection that aligns LP-arbitrageur incentives and enhances market stability.

Index Terms -Arbitrage, Blockchain, Constant Product Market Maker, Decentralized Finance, Risk Assessment, Smart Contract, Impermanent Loss, Uniswap, Balancer

## I. INTRODUCTION

Decentralized Exchanges (DEXs) powered by Automated Market Makers (AMMs) are a foundational pillar of Decentralized Finance (DeFi) [1], enabling trustless asset exchange without intermediaries [2]-[6]. Liquidity Providers (LPs) are the essential counterparties in this system, depositing assets into liquidity pools in return for a share of trading fees. The market microstructure of these automated market makers has been analyzed from both adoption and efficiency perspectives [7], [8]. However, a well-documented risk for LPs is Impermanent Loss (IL)-the reduction in portfolio value compared to simply holding the assets, caused by adverse price movements relative to an external market [9], [10].

Conventional wisdom frames arbitrage-which aligns prices between different trading venues-as the primary driver of IL. Consequently, a significant line of research focuses on mitigating IL through mechanisms like dynamic fee adjustments [11]-[13]. However, this perspective is incomplete. Trading fees, the LP's reward, are generated predominantly by arbitrage activity. This creates a fundamental tension: the same trades that can cause IL also provide the fee income intended to compensate for it.

Recent work has introduced the concept of Impermanent Gain (IG)-the scenario in which fees earned from an arbitrage trade exceed the associated IL, resulting in a net profit for the LP [14]. This occurs when the price deviation between the DEX and a reference market (typically a CEX) is sufficiently small. This finding reframes the LP's risk-reward profile: rather than universally suffering from arbitrage, LPs can profit from it within a specific range of price discrepancies.

This paper moves from identifying the existence of IG to formally characterizing its stable profitability zone and demonstrating its practical feasibility. We develop a joint model of arbitrageur and LP profitability for Constant Function Market Makers (CFMMs), including Uniswap V2 and Balancer. Within this model, we derive closed-form analytical bounds for Uniswap that define the exact price ratio interval where arbitrage is profitable for both the arbitrageur and the LP-a state of symbiotic equilibrium. Crucially, we validate this theoretical framework through a controlled on-chain experiment, deploying both baseline and private pools with a whitelisted arbitrageur, demonstrating the practical feasibility of collaborative systems where LPs can achieve stable returns with reduced impermanent loss.

Our core contributions are:

- 1) A Formal Model of Joint Profitability: We formulate the arbitrageur's optimization problem for aligning DEX and CEX prices and solve it for Uniswap and Balancer, explicitly deriving the LP's resulting profit function.
- 2) Analytical Characterization of the IG Zone: For Uniswap V2, we provide closed-form expressions for the boundaries of the price ratio region where LPs experience net impermanent gain.
- 3) Probabilistic Risk Framework: By modeling external price dynamics as a Geometric Brownian Motion, we translate the IG zone boundaries into an upper bound for
4. the one-block probability of IL, establishing a direct link between market volatility, protocol fees, and LP risk.
- 4) Fee Optimization Insight: We demonstrate how this probabilistic bound can serve as a constraint for determining protocol fee parameters that align with a target LP risk tolerance.
- 5) Experimental Validation: We conduct controlled onchain experiments with private pools, demonstrating that 76% of arbitrage transactions occur in win-win zones and revealing the regularization effect of fees against volatile arbitrage.

Importantly, our experimental results reveal a nuanced tradeoff: zero-fee pools generate 50% more arbitrage activity but expose LPs to impermanent loss up to -20 MATIC, while even minimal fees (0.03%) regularize arbitrage, stabilizing LP returns near zero IL. This suggests fee structures act as coordination mechanisms, not merely revenue sources.

By quantifying the stable zone of impermanent gain and demonstrating its practical viability, this work provides LPs with a clearer expectation of returns and offers protocol designers a mathematical tool for fee optimization based on measurable market risk. The subsequent sections detail our methodology (Section III), present the theoretical analysis (Section IV), show experimental validation (Section V), and discuss the implications of our findings (Section VI).

## II. RELATED WORK

Automated Market Makers (AMMs) enable decentralized token exchange by replacing the traditional order book with a liquidity pool and a pricing function implemented in a smart contract [2], [3]. The quality and efficiency of these decentralized markets compared to centralized exchanges have been empirically studied [6], revealing trade-offs in market depth and price discovery. In a two-asset AMM, the pool holds reserves ( x, y ) and defines a trading rule via an invariant, e.g., a curve F ( x, y ) = const. Traders swap against the pool by moving the state along this curve: adding one asset requires removing the other so that the invariant is (approximately) preserved. The instantaneous exchange rate is given by the pool's marginal price, which corresponds to the local slope of the invariant, p = -d y/ d x . Because this slope changes with the reserves, AMMs naturally exhibit slippage (larger trades move the price more). Liquidity providers (LPs) supply both assets to the pool and receive LP shares, earning a fraction of swap fees, but their returns depend on how prices evolve, since changes in the reserve ratio can lead to effects such as impermanent loss.

Impermanent Loss is classically defined as the difference between the value of a liquidity provider's position in an AMM and the value of holding the same assets outside the pool [2], [15]-[18]. Mathematical formalizations have further refined this concept through the lens of 'Greeks' for liquidity providers [19] and generalized treatments across constant function market makers [20]. When the relative market price of the two tokens changes, arbitrage trades rebalance the pool reserves to the new price, so the LP ends up with a different asset mix. This mix can be worth less than the original hold portfolio because of the AMM's convex rebalancing rule. The loss is called impermanent because it depends on the current price ratio and can shrink if prices revert, while accumulated swap fees may partially or fully offset it [14]. This view, however, primarily captures the LP's perspective relative to a passive 'hold' baseline. Recent research has critically expanded this understanding by introducing the symmetrical concept of impermanent gain , reframing IL not merely as a loss but as a transfer of value between counterparties in a trade. As shown by Kim et al. [21], impermanent gain is the positive financial outcome for the AMM (and thus collectively for its LPs) that arises from the exact same price movement that causes an impermanent loss for an individual LP when evaluated against the hold strategy. This duality is most clearly articulated by Labadie, who demonstrates that for AMMs with a constant-product formula, the trader's slippage is mathematically equivalent to the AMM's negative IL-that is, the trader's loss from slippage is precisely the AMM's (and LPs') impermanent gain [22]. This establishes that IL and slippage are two sides of the same coin, representing a fundamental wealth transfer from traders to the liquidity pool during non-infinitesimal swaps. Building on this, Lee and Kim [23] provide a significant theoretical advancement by defining a sufficient condition for guaranteed impermanent gain, which they term 'origin crossing' . They prove that a swap transaction results in a net impermanent gain for the liquidity pool if the trade moves the pool's reserve state ( x, y ) in such a way that the post-trade state is on the opposite side of a line connecting the pre-trade state to the origin (i.e., the ray from the origin to the state changes quadrant). This provides a concrete, testable criterion for when LPs benefit from price divergence, moving the discussion from probabilistic fee offsets to deterministic transaction-based outcomes.

Popular AMM designs primarily differ in their choice of invariant, which directly shapes the impermanent loss (IL) profile. For instance, Uniswap V2 employs a constant product invariant [2]:

<!-- formula-not-decoded -->

where K is a constant determined by the initial pool reserves and maintained (up to fees) during trading. In contrast, Balancer extends this framework to a weighted constant product invariant [24].

<!-- formula-not-decoded -->

Comparative analyses like Kim et al. [25] show how different invariant curves (constant product, constant sum, stable swap) lead to distinct IL landscapes under the same market movements, informing LP choice of platform. Beyond basic invariant designs, concentrated liquidity markets such as Uniswap V3 have introduced more complex risk-return profiles for LPs. Analyses of these markets include predictable losses in concentrated liquidity [26], risks and returns of Uniswap V3 liquidity providers [27], strategic liquidity provision in Uniswap V3 [28], mathematical derivations of concentrated liquidity mechanics [29], and thorough mathematical modeling of Uniswap v3 dynamics [30].

A primary line of defense against net IL is the accumulation of swap fees. In [14], the authors study several AMM designs (UniswapV2, Balancer, and Curve). They emphasize that swap fees, when reinvested into the liquidity pool, make the pool invariant effectively non-constant over time. As a consequence, there exists a non-trivial region of impermanent gain for liquidity providers when the trade size is sufficiently small. For UniswapV2, the paper derives an exact expression for the threshold swap size, where ϕ 1 and ϕ 2 are the fees for the input and output tokens and γ i = 1 -ϕ i :

<!-- formula-not-decoded -->

It also provides an approximate bound that applies to all considered protocols, where p ( x 0 , K 0 ) denotes the pool's marginal price at the initial moment of time:

<!-- formula-not-decoded -->

The strategic setting of these fees is itself a complex optimization problem. Recent work explores dynamic fee mechanisms as a sophisticated tool for IL mitigation. Baggiani et al. [13] formulate the problem of determining optimal dynamic fees in a constant function market maker as a stochastic control problem. Their analysis reveals two distinct optimal regimes: a high-fee regime to deter arbitrage and preserve LP value, and a low-fee regime designed to attract beneficial 'noise' trading volume and increase fee income, with the optimal fee adapting linearly to the pool's inventory and external price changes. This aligns with empirical observations in stable-swap markets, where fee compression is driven by competition, yet ultra-low fees can paradoxically attract more toxic, MEV-driven order flow [31]. The broader ecosystem impact of MEV includes consensus instability and frontrunning in decentralized exchanges [32], while systematic approaches to arbitrage in DEXs have been formalized [33]. Game-theoretic models, such as those by Fritsch [34], further analyze fee competition between pools, proving the existence of equilibria where traders endogenously split order flow. Beyond fees, advanced strategies focus on optimizing liquidity deployment . For concentrated liquidity AMMs like Uniswap V3, Zeller et al. (2025) formalize the problem of selecting optimal liquidity provision intervals as a tractable stochastic optimization problem, balancing expected fee rewards against divergence loss and reallocation costs [35]. This approach aims to move LPs from heuristic methods to mathematically grounded strategies for profitable liquidity concentration.

Finally, the management of IL sits within the broader DeFi landscape where protocols expose sensitive hyperparameters. System outcomes are highly dependent on these choices because user behavior adapts endogenously. Thus, tuning parameters becomes a coupled optimization problem under strategic interaction rather than a simple offline calibration task. This principle is evident not only in AMM fee games [12], [34] but also in lending protocols, where parameters like collateral factors and interest rates are optimized through the lens of default probability and risk assessment [36], [37].

The design of optimal liquidity provision mechanisms has been formalized through Myersonian frameworks that consider incentive compatibility and social welfare [38]. However, liquidity provision in decentralized exchanges exhibits paradoxes where more providers can sometimes mean less effective liquidity due to fragmentation and coordination challenges [39]. Broader DeFi risk measurement frameworks address both protocol-specific risks and systemic vulnerabilities [40], [41].

In summary, the related work reveals impermanent loss as a central, multifaceted challenge in DeFi. The discourse has evolved from viewing it as a simple passive holding penalty to understanding it as one side of a value transfer (impermanent gain), with deterministic conditions for its occurrence. Mitigation strategies are advancing from static fee models to dynamic, optimized approaches for both fee setting and liquidity placement, all within a complex, game-theoretic ecosystem of interacting agents.

## III. METHODOLOGY

Our methodology aims to establish a quantitative framework for analyzing the symbiotic relationship between liquidity providers (LPs) and arbitrageurs in AMM-based DEXs. We conceptualize three distinct price ratio zones that determine profitability outcomes for both parties, as illustrated in Figure 1. By combining this zonal analysis with stochastic modeling of price movements, we derive probabilistic measures of IL risk and corresponding fee optimization strategies.

## A. Joint Profitability Zones

The core of our approach lies in identifying three mutually exclusive regions defined by the ratio between the external market price p cex and the DEX pool's marginal price p dex :

- 1) No-Arbitrage Zone: When | p cex /p dex -1 | is very small, arbitrage opportunities are insufficient to cover transaction costs. In this zone, no arbitrage transactions occur, and LPs neither gain nor lose from price movements.
- 2) Impermanent Gain (IG) Zone: For moderate price discrepancies beyond the no-arbitrage threshold but within a specific bound, arbitrage becomes profitable. Crucially, the arbitrage trade volume in this region is small enough that the fees collected by LPs exceed the IL caused by the price realignment. This creates a win-win scenario where both arbitrageurs and LPs profit.
- 3) Impermanent Loss (IL) Zone: When price discrepancies are large, arbitrage remains profitable for arbitrageurs, but the required trade volume is substantial. In this zone, the resulting IL outweighs the fee income for LPs, leading to a net loss.

The boundaries between these zones depend on the pool's fee structure ( ϕ 1 , ϕ 2 ) and invariant curve parameters. For the constant product AMMs we analyze (Uniswap V2 and Balancer), these boundaries are symmetric around 1 when expressed as price ratios. Specifically, if we denote the upper boundary as τ &gt; 1 , then the lower boundary is 1 /τ , creating an interval [1 /τ, τ ] where arbitrage results in impermanent gain for LPs. This symmetry arises from the mathematical structure of these AMMs and is not a general requirement for all market makers.

## B. Stochastic Risk Assessment

To translate zonal boundaries into practical risk metrics, we model the evolution of the external price p cex as a Geometric Brownian Motion (GBM). Given the IG zone boundaries [1 /τ, τ ] , we compute the probability that a price movement within one block time ∆ t crosses from the IG zone into the IL zone. This one-block IL probability, P IL, serves as a key risk metric for LPs.

Under the GBM assumption, the distribution of price ratios is log-normal, allowing us to derive an upper bound for P IL . This bound depends explicitly on market volatility σ , block time ∆ t , and the fee-dependent boundary parameter τ .

## C. Fee Parameter Optimization

The final component of our methodology links the risk metric to protocol design. Given a target maximum acceptable IL probability ξ (e.g., 1% per block), we solve for the minimum fee parameters ( ϕ 1 , ϕ 2 ) that satisfy P IL ≤ ξ . This provides a principled approach to fee setting that aligns protocol parameters with LP risk tolerance, moving beyond heuristic or purely competitive fee selection.

## IV. THEORETICAL ANALYSIS

In this section, we present the detailed mathematical derivations underlying our methodology. We begin with the arbitrageur's optimization problem, derive explicit profitability zones for Uniswap V2 and Balancer, and establish the probabilistic risk framework.

## A. Arbitrageur Model

An arbitrageur maximizes profit by exploiting price differences between a DEX pool and an external CEX. We assume the CEX is infinitely liquid at price p cex, where p cex denotes the external market price of the asset pair. The DEX follows a constant function market maker curve with fees, and its marginal price is denoted by p dex , representing the instantaneous exchange rate implied by the pool reserves. Let γ i = 1 -ϕ i where ϕ i is the fee rate for token i , so that γ i represents the effective fraction of input remaining after fees. The arbitrageur's profit when p dex &lt; p cex (buy on DEX, sell on CEX) is:

<!-- formula-not-decoded -->

where dy ( dx ) is the output from the DEX for input dx , accounting for fees. The arbitrageur chooses dx to maximize Π arb .

1) Balancer: For Balancer with weights w x , w y ( w x + w y = 1 ), the trading function with fees is:

<!-- formula-not-decoded -->

Solving for the optimal arbitrage amounts yields:

<!-- formula-not-decoded -->

While Balancer generalizes the constant product invariant through asset weights, this added flexibility reduces analytical tractability. In particular, closed-form expressions for the joint profitability (IG) zone boundaries are generally not available due to the nonlinear dependence on the weight parameters. As a result, in this work we focus on deriving explicit analytical results for Uniswap V2, while the corresponding results for Balancer are obtained numerically based on the arbitrage optimization framework.

2) Uniswap V2: Uniswap V2 is a special case of Balancer with w x = w y = 0 . 5 . Substituting into (4) gives:

<!-- formula-not-decoded -->

## B. Joint Profitability Zones

The LP experiences impermanent gain when the arbitrage volume is below a threshold ∆ x max (or ∆ y max ). For Uniswap V2, this threshold is given by [14]:

<!-- formula-not-decoded -->

The joint profitability zone occurs when the arbitrageur's optimal trade (5) is less than the LP's gain threshold (6). Solving these inequalities yields the price ratio interval for win-win outcomes:

<!-- formula-not-decoded -->

where τ = γ 2 (2 -γ 1 ) 2 γ 1 (2 γ 2 -1) 2 . Note that the interval is symmetric around 1 in logarithmic space ( log(1 /τ ) = -log( τ ) ), which is a specific property of constant product AMMs with the fee structure considered. This symmetry simplifies the probabilistic analysis but is not a general requirement for all AMM designs.

## C. Probability of Impermanent Loss

Assuming GBM dynamics for p cex with drift µ and volatility σ , the one-block transition probability density is log-normal. The probability of exiting the IG zone in one block, starting from price ratio y = p cex /p dex , is:

TABLE I: Simulation parameters based on USDC/RAD pool

| Pool     | Ethereum Address                           | Ethereum Address                           | Ethereum Address                           | Ethereum Address                           | Ethereum Address                           |
|----------|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|
| USDC/RAD | 0x8C1c499b1796D7F3C2521AC37186B52De024e58c | 0x8C1c499b1796D7F3C2521AC37186B52De024e58c | 0x8C1c499b1796D7F3C2521AC37186B52De024e58c | 0x8C1c499b1796D7F3C2521AC37186B52De024e58c | 0x8C1c499b1796D7F3C2521AC37186B52De024e58c |
| σ        | µ                                          | γ 1                                        | γ 2                                        | x                                          | y                                          |
| 0.0027   | 0                                          | 0.997                                      | 1                                          | 997 348                                    | 3 751 882                                  |

<!-- formula-not-decoded -->

where Φ is the standard normal CDF.

An upper bound for P IL is obtained by evaluating at the worst-case starting point within the IG zone. For µ = 0 , this occurs at the boundaries:

<!-- formula-not-decoded -->

## D. Fee Optimization

Given a target IL probability ξ , we solve for the fee parameters that satisfy P up IL ≤ ξ . For one-sided fees ( ϕ 1 = ϕ , ϕ 2 = 0 ), this reduces to a one-dimensional root-finding problem. The solution provides the minimum fee required to achieve the desired risk level given market volatility σ .

## V. EXPERIMENTAL RESULTS

We conduct two sets of experiments: (1) simulation studies to validate our theoretical framework and illustrate the methodology, and (2) real-world on-chain experiments with private pools to demonstrate practical feasibility.

## A. Illustration of Methodology

We first apply our framework to simulated Uniswap V2 and Balancer pools with parameters matching real volatile pairs (Table I). Figure 1 visualizes the three profitability zones and the profit functions for both LPs and arbitrageurs. The green region represents the win-win zone where both parties profit, validating our theoretical bounds.

1) IL Block Distribution: We simulate price paths under GBM to estimate the distribution of blocks until first IL occurrence. Specifically, we simulate 10 , 000 independent price trajectories following a Geometric Brownian Motion with drift µ and volatility σ , using a discrete-time approximation with block interval ∆ t = 12 seconds. For each trajectory, we record the number of blocks until the first transition from the IG zone to the IL zone occurs. Figure 2 compares the empirical cumulative distribution function (CDF) with theoretical predictions. The geometric distribution model with experimentally estimated P IL closely matches simulation results, while the conservative upper bound P up IL provides a safe overestimate.

<!-- image -->

Fig. 1: LP and arbitrageur profit functions for Uniswap (solid) and Balancer with w x = 0 . 2 , w y = 0 . 8 (dashed). The blue shaded area indicates the no-arbitrage zone, while green areas represent the joint profitability (IG) zone.

<!-- image -->

x

(b) Balancer,

w

= 0

.

2

,

w

y

= 0

.

8

.

Fig. 2: CDF of the block number until first IL occurrence. The geometric distribution (GD) model with experimental P IL closely matches simulations.

2) Optimal Fee Analysis: Figure 3 shows the minimum fee required to achieve target IL probabilities ξ = { 0 . 001 , 0 . 01 , 0 . 05 } across different volatility levels. Our theoretical bound provides a practical approximation for protocol designers, with close alignment to experimental results.

## B. On-Chain Experiment with Private Pools

To demonstrate the practical feasibility of our theoretical framework, we conducted a controlled on-chain experiment using two Algebra V3 (Uniswap V3-style) concentrated liquidity pools deployed on the Polygon network [42]. The experiment ran from December 1st to December 26th, 2025, providing sufficient data to analyze the dynamics of joint profitability under real market conditions.

Fig. 3: Minimum fee required to achieve target IL probability ξ at different volatility levels. Theoretical bounds (black lines) provide close approximations to simulation results (points with error bars).

<!-- image -->

1) Experimental Setup: We deployed two pools with identical parameters except for their fee structure. Both pools used the USDT/WMATIC pair, where WMATIC represents the wrapped version of Polygon's native MATIC token (wrapping is standard practice in DEXs prior to Uniswap V4 for technical simplicity and uniform token interfaces). Pool A implemented a 0.03% swap fee, while Pool B served as a zero-fee alternative. The small fee in Pool A was intentionally chosen to create a narrower IG zone, making impermanent loss more probable-thereby testing our risk framework under challenging conditions-and to test the regularization effect of fees against low-profit, volatile arbitrage. This low-fee approach also aligns with recent trends in stable-swap markets, where fee compression has become prevalent due to intense competition [43].

To establish exclusive arbitrage access-a critical requirement for testing our collaborative LP-arbitrageur modelwe implemented a whitelist mechanism that restricted swap permissions to our designated arbitrage bot. This setup ensured that all price alignment transactions originated from our controlled arbitrage strategy, eliminating interference from external arbitrageurs and MEV bots. This design choice is methodologically motivated. In real-world DEX environments, arbitrage is highly competitive and often dominated by MEVdriven strategies, as documented in prior work [32]-[34], [39]. By restricting access to a single arbitrageur, we intentionally remove competitive and MEV-related effects in order to isolate the core LP-arbitrageur interaction. This allows us to evaluate the underlying mechanism in a controlled setting.

Both pools were configured with liquidity concentrated in a single wide price range [0.0001, 10000] to approximate the behavior of a Uniswap V2 pool while maintaining the gas efficiency benefits of concentrated liquidity. We deployed $3,000 worth of liquidity in each pool, split appropriately between USDT and WMATIC to establish an initial price aligned with the external market. Table II summarizes the key experimental parameters.

TABLE II: Private pool experiment parameters

| Parameter   | Pool A (0.03% fee)                           | Pool B (0% fee)                              |
|-------------|----------------------------------------------|----------------------------------------------|
| Address     | 0x1C890425Cc2FFF65891 Be6c87A07E9Dd4613C65 8 | 0x5A5E71Dc833e49F4cE2 9F72518d0D4877aA581b B |
| Token Pair  | USDT/WMATIC                                  | USDT/WMATIC                                  |
| Liquidity   | $3,000                                       | $3,000                                       |
| Fee Tier    | 0.03%                                        | 0%                                           |
| Range       | [0.0001, 10000]                              | [0.0001, 10000]                              |
| Duration    | Dec 1-26, 2025                               | Dec 1-26, 2025                               |
| Whitelisted | Arbitrage bot only                           | Arbitrage bot only                           |

Our arbitrage bot continuously monitored both pools and external DEX pools. When price discrepancies exceeded the no-arbitrage threshold, the bot executed optimal arbitrage trades according to the strategy derived in Section IV. All transactions, profits, and impermanent loss events were tracked on-chain for subsequent analysis.

2) Results and Analysis: Figure 5 shows the distribution of transactions across profitability zones for Pool A (0.03% fee). Consistent with our theoretical predictions, 76% of all transactions occurred within the joint profitability (IG) zone where both the arbitrageur and LPs profit and 24% in IL zone, but there were no transactions in most of the blocks, which corresponds to the no-arbitrage zone. This distribution validates our model's key insight: properly calibrated fees can create a sustainable win-win regime even under competitive market conditions.

The temporal evolution of profits provides further insight into the system dynamics. Figure 4 tracks the key metrics over the experiment duration. Both pools exhibited stable results. Pool A (with 0.03% fee) shows impermanent gain (IG) remaining close to zero, concluding at -1 MATIC, while its arbitrage profit reaches up to 36 MATIC. Pool B (zero fee) demonstrates impermanent loss (negative IG) up to -19 MATIC, with arbitrage profit peaking at 45 MATIC. The resulting sum of arbitrage and IG is positive in both cases: Pool A achieves a combined profit of approximately 35 MATIC, while Pool B reaches about 26 MATIC. This demonstrates that a fair distribution of profit between arbitrageur and LP, as facilitated by a positive fee structure in Pool A, can result in simultaneous stable profit for both parties, underscoring that collaboration matters. Furthermore, the positive fee in Pool A acts as a regularization mechanism, preventing lowprofit arbitrage transactions that would be risky due to price volatility.

We note an important observation: the zero-fee pool generated 50% more arbitrage transactions and 25% higher arbitrageur profit than the fee-charging pool. This demonstrates that eliminating fees increases arbitrage frequency and potential arbitrageur profits. In principle, an arbitrageur operating in a zero-fee pool could share a portion of their increased profits with LPs, potentially creating a win-win scenario even without fees. However, such profit-sharing arrangements require explicit coordination or protocol mechanisms that were not implemented in our experiment. In our baseline zerofee setup without profit sharing, LPs bore the full brunt of impermanent loss while arbitrageurs captured all gains.

Fig. 4: Profit evolution over the 26-day experiment. Pool A (with 0.03% fee) shows impermanent gain (IG) fluctuating around 0 MATIC with a final result of -1 MATIC, and arbitrage profit reaching up to 36 MATIC. Pool B (zero fee) exhibits impermanent loss (negative IG) up to -19 MATIC and arbitrage profit up to 45 MATIC. The combined profit (arbitrage + IG) is positive in both cases, with Pool A achieving approximately 35 MATIC and Pool B 26 MATIC.

<!-- image -->

The comparative performance metrics reveal the economic implications of our framework. Pool A achieved a combined annualized return of 3.2% APR, outperforming Pool B's 2.4% APR by 33%. However, both private pools underperformed relative to a comparable public pool (contract address 0x604 229c960e5cacf2aaeac8be68ac07ba9df81c3) which yielded a 9.5% APR. This performance gap highlights the competitive efficiency of open, multi-arbitrageur markets in extracting value from price discrepancies. Nevertheless, the superior performance of Pool A relative to Pool B stems from the symbiotic relationship enabled by the fee structure: LPs provide compensation (through fees) to arbitrageurs for stabilizing the pool, while arbitrageurs return value to LPs by maintaining prices within the IG zone. The zero-fee pool generated 1.5 × more arbitrage transactions, confirming that the absence of fees incentivizes greater arbitrage activity. This suggests that explicit, protocol-enforced profit-sharing mechanisms in zerofee pools could potentially bridge the performance gap with public pools by redistributing a portion of the higher arbitrageur profits to LPs.

These experimental results validate several key aspects of our theoretical framework:

- 1) Existence of IG zones: The concentration of transactions in the win-win region for Pool A confirms that properly calibrated fees create sustainable profitability zones where both LPs and arbitrageurs benefit simulta-
2. neously.
- 2) Risk reduction: The zero-fee pool (Pool B) exhibited impermanent loss up to -20 MATIC, while the feecharging pool (Pool A) maintained IG near zero, demonstrating that fees provide a stabilizing regularization effect against volatile, low-profit arbitrage.
- 3) Collaborative value creation: The combined profit was positive in both pools, with Pool A achieving a higher total ( ≈ 35 MATIC vs. ≈ 25 MATIC). This indicates that the fee structure in Pool A fostered a more efficient collaboration, leading to greater overall value extraction from price discrepancies.
- 4) Arbitrage volume vs. fee trade-off: Zero-fee arbitrage generated greater absolute profit for the arbitrageur (+45 MATIC vs. +36 MATIC), confirming that the absence of fees incentivizes more arbitrage activity. However, this does not automatically translate to better LP outcomes without explicit coordination.
- 5) Practical feasibility: The successful implementation proves that a collaborative LP-arbitrageur system is practically achievable. The results suggest that protocol designs incorporating fee-based regularization can create more sustainable and predictable profit zones for LPs.

The experimental results demonstrate two distinct pathways to sustainable liquidity provision: (1) Fee-based coordination (Pool A) creates an automatic win-win zone through builtin fee mechanisms, providing predictable returns with lower volatility. (2) Zero-fee operation (Pool B) generates more arbitrage opportunities and higher potential arbitrageur profits, but requires explicit profit-sharing arrangements to benefit LPs. Our theoretical framework works well for fee-based pools despite modeling simplifications, while the zero-fee case highlights the need for additional coordination mechanisms to realize its full potential.

It is important to acknowledge that our theoretical model makes several simplifying assumptions that differ from our experimental setup. The theoretical analysis assumes an ideal arbitrageur operating between a DEX and a CEX with perfect monitoring and immediate execution every block. In contrast, our experimental implementation used a real arbitrage bot operating between DEX pools (our private pool and public DEXs) with practical constraints including network latency, gas price competition, and occasional missed opportunities. Furthermore, the exclusive whitelist access eliminated competition from other arbitrageurs, creating conditions different from open markets. Despite these differences in assumptions and implementation, the experimental results align closely with the theoretical predictions-particularly the existence of the IG zone and the win-win transactions comprising 76% of all trades. This demonstrates that while the theoretical model simplifies reality, it captures the essential dynamics and provides a useful approximation for real-world scenarios.

The experiment also revealed an important practical consideration: the 0.03% fee, while sufficient to create an IG zone, resulted in relatively infrequent arbitrage activity compared to the zero-fee pool. This suggests a trade-off between fee income frequency and protection against IL-a consideration that could inform dynamic fee strategies in future implementations.

Fig. 5: Transaction distribution across profitability zones for Pool A (0.03% fee). The central blue region shows noarbitrage blocks, green regions represent win-win trades, and red regions indicate IL-causing arbitrage.

<!-- image -->

A key limitation of our experimental setup is the use of a single, whitelisted arbitrageur, which eliminates competition and MEV considerations present in public pools. While this simplifies analysis, future work should explore multi-arbitrageur competitive equilibria and their impact on the IG zone boundaries. Additionally, our 26-day experiment captures limited market regimes; longer-term studies across varying volatility environments would strengthen the empirical validation.

## VI. CONCLUSION

This paper presents a comprehensive framework for quantifying profitability zones in Automated Market Maker-based decentralized exchanges, transforming the conventional view of impermanent loss from an unavoidable risk to a manageable parameter. We bridge theoretical modeling with empirical validation to demonstrate that properly calibrated fee structures can create sustainable win-win scenarios for both liquidity providers and arbitrageurs.

Our primary contribution is the formal characterization of Impermanent Gain zones-price ratio intervals where arbitrage transactions benefit both parties simultaneously. For constant product AMMs like Uniswap V2 and Balancer, we derived explicit analytical boundaries for these zones and developed a probabilistic risk framework that translates these boundaries into practical metrics for liquidity providers. By modeling external price dynamics as Geometric Brownian Motion, we enable LPs to quantify impermanent loss probability and duration, providing a principled basis for fee optimization based on market volatility and risk tolerance.

Through controlled on-chain experiments with private pools, we empirically validated our theoretical framework. The experimental results confirmed that 76% of arbitrage transactions occurred within the predicted win-win zone when using a 0.03% fee, demonstrating that collaborative LP-arbitrageur systems can eliminate impermanent loss while enhancing combined returns. Crucially, our experiment revealed a fundamental trade-off: zero-fee pools generate 50% more arbitrage transactions and 25% higher arbitrageur profits (45 MATIC vs. 36 MATIC), yet the combined total wealth (arbitrageur profit + LP impermanent gain) is 40% higher in the fee-charging pool (35 MATIC vs. 25 MATIC). This demonstrates that fee-based regularization enhances overall economic efficiency and common wealth creation, not merely redistributing value between participants. While zero-fee pools create greater arbitrageur value extraction potential, this comes at the expense of total system efficiency, highlighting that fees serve as coordination mechanisms that optimize collective outcomes.

The implications of this work extend to multiple stakeholders in decentralized finance. Protocol designers gain a quantitative framework for optimizing fee structures based on measurable market risk, potentially reducing toxic order flow and improving overall market stability. Liquidity providers acquire tools for assessing pool risk and selecting positions aligned with their risk-return preferences, moving beyond heuristic approaches to liquidity provision. Our analysis of private versus public pool performance provides guidance for sophisticated LPs considering exclusive arrangements with arbitrageurs, particularly in emerging markets or for exotic trading pairs where these advantages are most pronounced.

Several promising directions emerge for future research. Extending this framework to concentrated liquidity AMMs like Uniswap V3 would address the more complex zonal boundaries created by liquidity fragmentation. Investigating multiasset pools and cross-pool arbitrage could reveal additional dimensions of the LP-arbitrageur relationship. Developing dynamic fee mechanisms that adjust based on real-time volatility estimates and arbitrage competition could enhance protocol responsiveness to changing market conditions. Finally, exploring decentralized profit-sharing mechanisms for zero-fee pools-such as bonding curves for arbitrageur-LP agreements or protocol-level profit distribution systems-could enable zerofee pools to realize their full potential without relying on trusted relationships, bringing the benefits of private pool arrangements to public settings.

By bridging rigorous theoretical analysis with practical on-chain experimentation, this work advances decentralized finance toward more sustainable and predictable liquidity provision. Rather than viewing impermanent loss as an inevitable hazard, our framework treats it as a quantifiable parameter within a win-win market design. Regulatory considerations will also shape the evolution of DEX design and adoption, as cryptocurrency regulation impacts trading markets and compliance requirements [44]. As DeFi continues to mature, such quantitative approaches will be essential for building robust, efficient, and equitable financial systems on blockchain infrastructure.

## REFERENCES

- [1] F. Sch¨ ar, 'Decentralized finance: On blockchainand smart contractbased financial markets,' SSRN Electronic Journal , 2020. [Online]. Available: https://www.ssrn.com/abstract=3571335
- [2] H. Adams, N. Zinsmeister, and D. Robinson, 'Uniswap v2 core,' 2020, whitepaper.
- [3] D. A. Zetzsche, D. W. Arner, and R. P. Buckley, 'Decentralized finance,' Journal of Financial Regulation , vol. 6, no. 2, pp. 172-203, 2020.
- [4] S. Malamud and M. Rostek, 'Decentralized exchange,' American Economic Review , vol. 107, no. 11, pp. 3320-3362, 2017.
- [5] S. H¨ agele, 'Centralized exchanges vs. decentralized exchanges in cryptocurrency markets: A systematic literature review,' Electronic Markets , vol. 34, p. 33, 12 2024.
- [6] A. Barbon and A. Ranaldo, 'On the quality of cryptocurrency markets: Centralized versus decentralized exchanges,' SSRN Electronic Journal , 2021.
- [7] A. Capponi and R. Jia, 'The adoption of blockchain-based decentralized exchanges: A market microstructure analysis of the automated market maker,' SSRN Electronic Journal , 2021.
- [8] G. Angeris and T. Chitra, 'Improved price oracles: Constant function market makers,' in AFT 2020 - Proceedings of the 2nd ACM Conference on Advances in Financial Technologies , 2020.
- [9] Y. Wang, Y. Chen, H. Wu, L. Zhou, S. Deng, and R. Wattenhofer, 'Cyclic arbitrage in decentralized exchanges,' in Companion Proceedings of the Web Conference 2022 , 2022, pp. 12-19.
- [10] S. H¨ agele, 'Centralized exchanges vs. decentralized exchanges in cryptocurrency markets: A systematic literature review,' Electronic Markets , vol. 34, no. 1, p. 33, 2024.
- [11] I. Lebedeva, D. Umnov, Y. Yanovich, I. Melnikov, and G. Ovchinnikov, 'Dynamic fee for reducing impermanent loss in decentralized exchanges,' in 2025 IEEE International Conference on Blockchain and Cryptocurrency (ICBC) , 2025, pp. 1-5.
- [12] B. Krishnamachari, Q. Feng, and E. Grippo, 'Dynamic automated market makers for decentralized cryptocurrency exchange,' in 2021 IEEE International Conference on Blockchain and Cryptocurrency (ICBC) , 2021, pp. 1-2.
- [13] L. Baggiani, M. Herdegen, and L. S´ anchez-Betancourt, 'Optimal dynamic fees in automated market makers,' 2025. [Online]. Available: https://arxiv.org/abs/2506.02869
- [14] R. Vlasov, V. Gorgadze, and A. Barger, 'The Impact of the Exchange Fees on Impermanent Loss of Liquidity Providers for Conservative Automated Market Makers,' The Journal of The British Blockchain Association , may 27 2025.
- [15] J. Xu, K. Paruch, S. Cousaert, and Y. Feng, 'Sok: Decentralized exchanges (dex) with automated market maker (amm) protocols,' ACM Computing Surveys , vol. 55, no. 11, p. 1-50, Feb. 2023. [Online]. Available: http://dx.doi.org/10.1145/3570639
- [16] A. A. Aigner and Gurvinder Dhaliwal, 'Uniswap: Impermanent loss and risk profile of a liquidity provider,' 2021. [Online]. Available: https://www.researchgate.net/doi/10.13140/RG.2.2.32419.58400/6
- [17] A. A. Aigner and G. Dhaliwal, 'Uniswap: Impermanent loss and risk profile of a liquidity provider,' 6 2021. [Online]. Available: http://arxiv.org/abs/2106.14404
- [18] S. Loesch, N. Hindman, M. B. Richardson, and N. Welch, 'Impermanent loss in uniswap v3,' arXiv , 11 2021.
- [19] N. Bardoscia and A. Nodari, 'Liquidity providers greeks and impermanent gain,' arXiv , 3 2023.
- [20] R. Tangri, P. Yatsyshin, E. A. Duijnstee, and D. Mandic, 'Generalizing impermanent loss on decentralized exchanges with constant function market makers,' arXiv , 1 2023.
- [21] H. J. Kim, S. Choi, Y. T. Yoon, and S. Yoo, 'Impermanent loss and gain of automated market maker smart contracts,' TechRxiv , 2022.
- [22] M. Labadie, 'Impermanent loss and slippage in automated market makers (amms) with constant-product formula,' SSRN Electronic Journal , 2022.
- [23] G. M. Lee and H. J. Kim, 'Impermanent loss mitigation for decentralized exchanges through optimization,' International Journal of Industrial Engineering : Theory Applications and Practice , vol. 31, 2024.
- [24] F. Martinelli and N. Mushegian, 'A non-custodial portfolio manager, liquidity provider, and price sensor,' Balancer Labs, Tech. Rep., 2019. [Online]. Available: https://docs.balancer.fi/whitepaper.pdf
- [25] H. J. Kim, G. M. Lee, J. Lee, S. Kang, S. W. Chae, and J.-S. Park, 'A comparison of impermant loss for various cfmms,' in 2024 IEEE International Conference on Blockchain (Blockchain) . IEEE, 8 2024, pp. 542-548.
- [26] ´ Alvaro Cartea, F. Drissi, and M. Monga, 'Predictable losses of liquidity provision in constant function markets and concentrated liquidity markets,' Applied Mathematical Finance , vol. 30, 2023.
- [27] L. Heimbach, E. Schertenleib, and R. Wattenhofer, 'Risks and returns of uniswap v3 liquidity providers,' 5 2022. [Online]. Available: http://arxiv.org/abs/2205.08904
- [28] Z. Fan, F. Marmolejo-Coss´ ıo, D. J. Moroz, M. Neuder, R. Rao, and D. C. Parkes, 'Strategic liquidity provision in uniswap v3,' arXiv , 8 2024.
- [29] M. B. Richardson and S. Loesch, 'Defi's concentrated liquidity from scratch,' arXiv , 8 2024.
- [30] H. Rigneault, N. G. Kumar, R. Cossart, D. Septier, G. Br´ evalleWaslilewki, A. Kudlinski, and A. Kaszas, 'Thorough mathematical modelling and analysis of uniswap v3,' Focus on Microscopy , p. 255, 9 2023. [Online]. Available: https://hal.science/hal-04214315
- [31] A. Khailuk, T. Kiriienko, N. Ovchinnik, and A. Prokhorov, 'The state of stable swaps,' May 2025, initial version: 30 May 2025. [Online]. Available: https://barterswap.xyz/resources/The-State-of-Stable-Swaps. pdf
- [32] P. Daian, S. Goldfeder, T. Kell, Y . Li, X. Zhao, I. Bentov, L. Breidenbach, and A. Juels, 'Flash boys 2.0: Frontrunning in decentralized exchanges, miner extractable value, and consensus instability,' in 2020 IEEE Symposium on Security and Privacy (SP) . IEEE, 5 2020, pp. 910927.
- [33] N. Boonpeam, W. Werapun, and T. Karode, 'The arbitrage system on decentralized exchanges,' in 2021 18th International Conference on Electrical Engineering/Electronics, Computer, Telecommunications and Information Technology (ECTI-CON) . IEEE, 5 2021, pp. 768-771.
- [34] R. Fritsch, 'A note on optimal fees for constant function market makers,' in Proceedings of the 2021 ACM CCS Workshop on Decentralized Finance and Security , ser. CCS '21. ACM, Nov. 2021, p. 9-14. [Online]. Available: http://dx.doi.org/10.1145/3464967.3488589
- [35] S. C. Zeller, P. K. Kandora, D. Kirste, N. Kannengießer, S. Rebennack, and A. Sunyaev, 'Automated market makers: A stochastic optimization approach for profitable liquidity concentration,' in 2025 IEEE International Conference on Blockchain and Cryptocurrency, ICBC 2025, Pisa, Italy, June 2-6, 2025 . IEEE, 2025, pp. 1-9. [Online]. Available: https://doi.org/10.1109/ICBC64466.2025.11114638
- [36] I. Melnikov, I. Lebedeva, D. Bogutsky, and Y. Yanovich, 'Smarter risks for smart contracts: Machine learning approach to credit scoring and risk assessment in defi,' in 2025 IEEE International Conference on Blockchain and Cryptocurrency (ICBC) , 2025, pp. 1-5.
- [37] I. Melnikov, I. Lebedeva, A. Petrov, and Y. Yanovich, 'Defi risk assessment: Makerdao loan portfolio case,' Blockchain: Research and Applications , vol. 6, no. 2, p. 100259, 2025. [Online]. Available: https://www.sciencedirect.com/science/article/pii/S2096720924000721
- [38] J. Milionis, C. C. Moallemi, and T. Roughgarden, 'A myersonian framework for optimal liquidity provision in automated market makers,' in Leibniz International Proceedings in Informatics, LIPIcs , vol. 287, 2024.
- [39] A. Capponi, R. JIA, and B. Zhu, 'The paradox of just-in-time liquidity in decentralized exchanges: More providers can sometimes mean less liquidity,' SSRN Electronic Journal , 2023.
- [40] J. Bertomeu, X. Martin, and I. Sall, 'Measuring defi risk,' Finance Research Letters , vol. 63, p. 105321, 5 2024.
- [41] N. Carter and L. Jeng, 'Defi protocol risks: The paradox of defi,' SSRN Electronic Journal , 2021.
- [42] J. Kanani, S. Nailwal, and A. Arjun, 'Matic Whitepaper Version 1.1,' 2018. [Online]. Available: https://github.com/maticnetwork/whitepaper
- [43] I. Khailuk, 'The state of stable swaps,' BarterSwap Research, Tech. Rep., November 2025, accessed: 2025-12-01. [Online]. Available: https://barterswap.xyz/resources/The-State-of-Stable-Swaps.pdf
- [44] B. D. Feinstein and K. Werbach, 'The impact of cryptocurrency regulation on trading markets,' SSRN Electronic Journal , 8 2021. [Online]. Available: https://papers.ssrn.com/abstract=3649475