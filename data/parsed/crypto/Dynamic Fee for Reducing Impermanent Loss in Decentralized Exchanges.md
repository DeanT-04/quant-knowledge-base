## Dynamic Fee for Reducing Impermanent Loss in Decentralized Exchanges

Irina Lebedeva ∗ , Dmitrii Umnov † , Yury Yanovich ∗ , Ignat Melnikov ∗ , George Ovchinnikov ∗‡

∗ Skolkovo Institute of Science and Technology, Moscow, Russia

† Faculty of Computer Science, HSE University, Moscow, Russia

‡ Kharkevich Institute for Information Transmission Problems, RAS, Moscow, Russia

Abstract -Decentralized exchanges (DEXs) are crucial to decentralized finance (DeFi) as they enable trading without intermediaries. However, they face challenges like impermanent loss (IL), where liquidity providers (LPs) see their assets' value change unfavorably within a liquidity pool compared to outside it. To tackle these issues, we propose dynamic fee mechanisms over traditional fixed-fee structures used in automated market makers (AMM). Our solution includes asymmetric fees via block-adaptive, dealadaptive, and the "ideal but unattainable" oracle-based fee algorithm, utilizing all data available to arbitrageurs to mitigate IL. We developed a simulation-based framework to compare these fee algorithms systematically. This framework replicates trading on a DEX, considering both informed and uninformed users and a psychological relative loss factor. Results show that adaptive algorithms outperform fixed-fee baselines in reducing IL while maintaining trading activity among uninformed users. Additionally, insights from oracle-based performance underscore the potential of dynamic fee strategies to lower IL, boost LP profitability, and enhance overall market efficiency.

Index Terms -Blockchain, DEX, Impermanent Loss, Liquidity Provider, Dynamic Fee Mechanisms, Arbitrage

## I. INTRODUCTION

Decentralized exchanges (DEXs) are integral to decentralized finance (DeFi), enabling trading without intermediaries [1], [2]. Despite advantages over centralized exchanges (CEXs), such as eliminating middlemen [3], DEXs face challenges like Impermanent Loss (IL) and arbitrage [4]. IL occurs when liquidity providers (LPs) see a reduction in asset value within a liquidity pool compared to holding them outside, especially in volatile markets, diminishing their incentive to provide liquidity. Transaction fees can partly offset these losses, providing some compensation for LPs. Arbitrage exploits price discrepancies between exchanges, often exacerbating IL and destabilizing DEX market efficiency [5].

To address these issues, dynamic fee mechanisms [6] have been proposed as alternatives to fixed fees in automated market makers (AMMs) [7]. These fees adjust to market conditions such as volatility and trading volume, potentially mitigating excessive arbitrage and IL. By increasing fees during high volatility, DEXs can capture more value from arbitrage trades, compensating LPs for increased risk.

Recent studies indicate a rise in DEX popularity, with platforms like Uniswap, PancakeSwap, and SushiSwap gaining traction [5], [8], [9]. Research highlights risks faced by LPs, particularly IL [10]-[13]. Solutions to IL include Impermanent Gain products [14] and frameworks for generalizing IL across exchanges [15]. Arbitrage between DEXs and CEXs remains a significant IL factor, with studies exploring architectural differences and arbitrage strategies [16], [17].

Our contributions are: (i) a mathematical model for optimal fee structures in AMMs based on market participant preferences; (ii) exploration of dynamic fee mechanisms to mitigate IL and reduce arbitrage inefficiencies; (iii) a framework for comparing fee structures, considering LP IL, DEX user profits, and market scenarios; and (iv) an algorithm for dynamic fee setting based on a CEX price oracle, providing insights into potential IL reduction.

The code accompanying this study is publicly available on GitHub [18].

## II. DEX USER EXCHANGE MODEL

This study aims at solving real-world problems by testing the proposed methods in simulations that are close to realworld scenarios. To this end, we focus on two primary types of users commonly observed in DEXs: liquidity providers, who provide liquidity to earn transaction fee, and traders who exchange crypto assets. For the purpose of this study, traders are further classified into two distinct groups: (i) informed users (IU) , who execute trades to maximize their profit, and (ii) uninformed users (UU) , who make trades based on internal principles, which may not always be optimal. Informed users are modeled through profitable arbitrage opportunities with CEXs, while uninformed users conduct more random transactions with a tolerance for inefficiency.

CEX asset prices are considered the ground truth in this study. CEX users operate using an order book, and we define the true price as the mean of the highest bid and lowest ask prices. While there are multiple CEXs, each with its own order book, price deviations are typically smaller on CEXs due to higher liquidity. These characteristics motivate our model, which assumes a single aggregated CEX and one DEX liquidity pool.

The DEX pool is defined by a token pair, which we will call Token A and Token B . At any given time t the pool contains x units of Token A and y units of Token B. The DEX exchange rate for Token B in terms of Token A, p DEX , is a function of x and y : p DEX = p DEX ( x, y ) . The DEX operates under an automated market maker mechanism, characterized by an invariant function I ( x, y ) , which determines both the pricing and the allowable trade amounts: (∆ x, ∆ y ) = (∆ x ( x, y, ∆ y ) , ∆ y ( x, y, ∆ x )) , where (∆ x, ∆ y ) are the amounts of the exchanged tokens A and B by a user. The values of (∆ x, ∆ y ) are determined by the invariant function and fee policy. The sign of a component determines the exchange direction: positive values correspond to tokens bought from the pool, while negative values correspond to tokens sold to the pool. In this paper, the constant product automated market maker (CPMM) is considered. Therefore, the price curve for this AMM type adheres to the equation I ( x, y ) = x · y .

Transaction fees in the pool are represented as ( x f , y f ) = f ( x, y, ∆ x, ∆ y ) .

The asset prices on CEX in a base currency are denoted as p A = p A ( t ) and p B = p B ( t ) and the exchange rate is given by p CEX = p B /p A .

Let us consider each type of user's behavior in more detail. The behavior of users is influenced by the current state of the DEX pool and token prices on CEX. The capital function is defined as follows: P ( a, b ) = a · p A + b · p B , where ( a, b ) represents an arbitrary pair of real numbers.

At the moment t LPs have capital P ( x, y ) = x · p A + y · p B . This capital is distributed among LPs via liquidity tokens. Liquidity providers aim to maximize their returns through transaction fees. While fees increase LPs' capital, imbalances in the token quantities x and y can lead to IL. Such imbalances may also reduce overall liquidity in the pool, potentially making the pool less attractive to users. Users pay a α = α ( t ) for exchange transaction to the network. The change in an users' capital, δP , is given by:

<!-- formula-not-decoded -->

## A. Informed User

As previously mentioned, the informed user executes a transaction only when it will bring a profit. The IU aims to exchange a specific amount of tokens ∆ x, ∆ y to maximize the change in the capital function δP over (∆ x, ∆ y ) .

If the maximum of δP is positive, the IU broadcasts the exchange transaction with corresponding optimal amounts (∆ x ∗ , ∆ y ∗ ) .

Let us illustrate it with an example of the CPMM model with fixed fee f fx. Suppose IU wants to exchange ∆ x tokens of Token A to ∆ y tokens of Token B. The invariant equation for the pool is expressed as:

<!-- formula-not-decoded -->

The IU's goal is to maximize the change in their capital function δP . By rearranging (2) to express ∆ y as a function of ∆ x , and substitutiong in (1) the IU will receive:

<!-- formula-not-decoded -->

Once ∆ x ∗ is determined, the corresponding value of ∆ y ∗ can be computed using the CPMM invariant (2). These optimal values allow the IU to execute the most profitable trade, accounting for both the DEX pool's transaction fees and the price discrepancy between the DEX and the CEX. By consistently optimizing their trades in this manner, IUs contribute to rebalancing the pool and ensuring arbitrage opportunities are exploited efficiently. However, excessive arbitrage activity may also exacerbate IL for liquidity providers, highlighting the importance of carefully calibrated fee structures to maintain equilibrium in the system.

Fig. 1. LP's profit as a function of fee

<!-- image -->

## B. Uninformed User

The primary goal of uninformed users is to exchange one token for another, often with limited sensitivity to small losses incurred during the transaction. However, psychological factors significantly influence the likelihood of a user completing a transaction, especially when the perceived or actual losses become substantial. This insight underscores that setting excessively high transaction fees is not a sustainable solution to address the issue of IL faced by liquidity providers. While high fees may temporarily increase the LP's revenue per transaction, they discourage users from participating in transactions, resulting in lower transaction volume and ultimately lower overall LP profits (see Fig. 1).

To capture this behavioral aspect, we introduce a 'psychological' relative loss factor r , which quantifies the ratio of deal losses to transaction volume:

<!-- formula-not-decoded -->

This metric reflects the UU's propensity to complete a transaction, depending on the extent of perceived losses relative to the total transaction value. A lower value of r indicates that users perceive the transaction as less favorable, reducing their willingness to proceed.

Uninformed users exhibit a distinct behavior compared to informed users, as they tend to make trades based on internal principles or heuristics, rather than optimizing for arbitrage opportunities. Their actions may follow patterns such as balancing portfolios, rebalancing assets after market shifts, or making trades based on external, non-financial motivations. Unlike informed users, UUs are less likely to evaluate the transaction in terms of maximizing returns and more likely to be influenced by perceived fairness or simplicity of the trade. When r exceeds a tolerable threshold, UUs are less likely to proceed with the exchange.

## III. FEE ALGORITHMS

To address the issue of IL, we propose the concept of asymmetric or directed fees: fee rates that vary depending on the direction of the swap. Specifically, the fee for swaps from Token A to Token B may be set higher than for swaps in the reverse direction. Ideally, we would set a higher fee in direction of potential arbitrage.

However, this approach is limited by the inherent limitations of DEX in accessing external data. Since fee algorithms in DEX are restricted to using data available on the blockchain, they face a fundamental information asymmetry when compared to arbitrageurs, who can leverage off-chain data sources to identify profitable opportunities. This asymmetry poses a challenge to fee optimization strategies.

In this paper, we evaluate the performance of the following fee algorithms:

## A. Fixed (FX, baseline)

The fixed fee is the traditional approach where the fee rate is constant for both A → B and B → A swaps, denoted as f fx. For the purposes of our experiments, we set f fx = 30 bps (basis points, 0 . 01% ).

## B. Block-Adaptive (BA)

This fee algorithm is based on the observation that if an arbitrage transaction occurs in block N , the likelihood of another arbitrage transaction in block N + 1 in the same direction is higher than in the opposite direction:

- 1) Begin with two separate fee rates for each direction, denoted as f A → B and f B → A .
- 2) If q DEX decreases during a block (indicating a net increase in A → B transactions and a potential arbitrage opportunity in the A → B direction), and f B → A ≥ f step , increase f A → B by f step and decrease f B → A by f step .
- 3) Similarly, if q CEX increases during a block (indicating a potential arbitrage opportunity in the B → A direction), and f A → B ≥ f step, increase f B → A by f step and decrease f A → B by f step .
- 4) If the price remains unchanged during the block, fee rates are left unaltered.

## C. Deal-Adaptive (DA)

This algorithm dynamically adjusts the fee based on the direction of the previous transaction. For instance, if the last transaction involved exchanging Token A for Token B, the fee in the direction from A to B ( f A → B ) increases by 1 bps, while the fee in the reverse direction ( f B → A ) decreases by 1 bps. The algorithm ensures that the average of the fees, f A → B and f B → A , does not exceed 30 bps. Consequently, in cases of frequent transactions in a single direction (an indicator of arbitrage activity), the fee in that direction gradually increases, while it decreases in the opposite direction. This mechanism helps boost the profit of LPs and encourage users to make transactions in the less active direction, improving market balance and efficiency.

## D. Oracle-Based (OB)

The discrete fee algorithm with a perfect oracle represents an idealized scenario designed to establish an upper bound on the effectiveness of fee mechanisms in mitigating IL.

This algorithm assumes access to the exact "fair prices" used by arbitrageurs to calculate their optimal trades, thereby eliminating the information asymmetry. While this assumption is highly unrealistic in practical settings, it serves as a benchmark for comparing more feasible algorithms.

To reduce the attractiveness of arbitrage opportunities, the algorithm dynamically adjusts the fee rates based on the direction of arbitrage. Specifically, the fee for swaps in the "arbitrage" direction (either A → B or B → A ) is set to f ad , while the fee in the opposite direction is set to f nad. In our experiments, we use f ad = 45 bps and f nad = 15 bps.

## IV. EVALUATION FRAMEWORK FOR FEE ALGORITHMS

To systematically compare and evaluate the proposed fee algorithms, we develop a simulation-based framework that emulates trading activity on a DEX at the granularity of individual blockchain blocks.

The initial pool size is set to 25 MUSDT, evenly distributed between the two tokens. For each block in the simulation, we model user behavior and trading dynamics as follows:

- 1) Uninformed User Activity : With a probability of p UU, an uninformed user attempts to trade. If a trade occurs, the user selects the direction and amount randomly. The traded amount is modeled as a fraction of the pool's assets, following a normal distribution N ( µ UU , σ 2 UU ) .
- 2) Informed User Arbitrage : Informed users execute arbitrage transactions whenever profitable opportunities exist, based on the "fair" prices for the block.
- 3) Metrics Calculations : For all market participants, metrics are computed relative to the block's fair prices.

The parameters governing pool dynamics and user behavior are calibrated to closely match the characteristics of the ETHSHIB liquidity pool on Uniswap V2.

Throughout the simulation, we calculate the markouts (MO), representing the profitability of trades in USDT for each type of participant: IU, UU, and LP. For LPs, the MO is the negative of the IL, adjusted using a hold strategy. A higher markout value indicates better performance, while the smaller IL the better.

The simulation utilizes two types of price data to ensure robustness under diverse market conditions. Synthetic Data : Simulating near-realistic token prices using geometric Brownian motion. A total of 1,000 paths, each spanning one day (1,440 blocks), were generated. We use 4 sets of parameters for GBM (estimated on corresponding segments of real data) Historical Data : Real-world price data for ETH and SHIB is sourced from Binance, with 1-minute snapshots. To account for different market conditions, we simulate four distinct periods: Bear Market (April 2024), Bull Market (November 2024), High Volatility (March 2024), Low Volatility (August 2024). Each period consists of approximately 40 , 000 samples, which are treated as individual blocks in the simulation.

## V. NUMERICAL RESULTS

## A. Psychological Factor Modeling

As highlighted in Section II-B, excessively high fees do not benefit LPs as they result in reduced transaction volumes, ultimately leading to lower overall profits for LPs. To account for this, our model includes a 'psychological factor' r (4), which determines the likelihood of a user completing a transaction. To illustrate this effect, we conducted simulations using the following setup: we fixed the quantities of tokens A and B in the pool ( x, y ), set the number of A tokens to be exchanged ( ∆ x ), and maintained constant CEX prices for tokens A and B. The number of tokens B returned ( ∆ y ) was then calculated for varying fee levels (using (2)). Subsequently, the transaction probability was modeled as P = exp( -| r | ) . Figure 1 presents the results averaged over 10 6 simulations, demonstrating that at higher fees, LP revenue decreases due to diminished transaction demand.

TABLE I SYNTHETIC DATA SIMULATION RESULTS

| Market        | Alg.        | IU MO                                                 | UU MO                                               | LP MO                                                       |
|---------------|-------------|-------------------------------------------------------|-----------------------------------------------------|-------------------------------------------------------------|
| High Volatile | FX DA BA OB | 85640 ± 8477 85620 ± 8478 84742 ± 8409 * 69766 ± 7414 | - 8768 ± 611 - 8766 ± 615 - 8773 ± 587 - 8804 ± 563 | - 84133 ± 8222 - 84115 ± 8215 - 83220 ± 8167 - 67541 ± 7193 |
| Low Volatile  | FX DA BA OB | 595 ± 103 597 ± 101 591 ± 99 434 ± 93                 | - 8116 ± 284 - 8115 ± 284 - 8113 ± 279 - 8118 ± 279 | 3450 ± 226 3447 ± 223 3460 ± 219 3742 ± 224                 |
| Bull          | FX DA BA OB | 2976 ± 341 2982 ± 344 2909 ± 338 2207 ± 312           | - 8150 ± 317 - 8152 ± 318 - 8155 ± 308 - 8160 ± 291 | 502 ± 407 499 ± 409 596 ± 401 1557 ± 389                    |
| Bear          | FX DA BA OB | 1193 ± 170 1192 ± 169 1167 ± 166 872 ± 158            | - 8116 ± 294 - 8117 ± 294 - 8112 ± 286 - 8105 ± 288 | 2640 ± 281 2642 ± 282 2679 ± 264 3139 ± 278                 |

* For each metric, the best algorithms among FX, DA , and BA are in bold.

TABLE II HISTORICAL DATA SIMULATION RESULTS

| Market        | Alg.        | IU MO                           | UU MO                               | LP MO                               | IL                                      |
|---------------|-------------|---------------------------------|-------------------------------------|-------------------------------------|-----------------------------------------|
| High Volatile | FX DA BA OB | 883,900 883,295 878,088 745,471 | -314,528 -315,492 -319,057 -318,141 | -713,551 -711,763 -702,735 -562,275 | 2,146,636 2,145,809 2,140,245 1,995,396 |
| Low Volatile  | FX DA BA OB | 21,547 21,326 21,556 17,768     | -222,801 -224,479 -222,936 -223,127 | 86,924 88,922 86,584 93,014         | -129,736 -130,708 -130,465 -135,422     |
| Bull          | FX DA BA OB | 183,885 183,091 180,639 148,360 | -272,720 -273,177 -269,788 -271,359 | -37,780 -36,148 -36,720 2,719       | -497,942 -512,479 -505,210 -541,723     |
| Bear          | FX DA BA OB | 63,221 61,989 63,081 53,033     | -221,017 -222,020 -222,168 -222,757 | 43,210 45,000 44,126 58,253         | -183,518 -182,912 -181,757 -192,818     |

## B. Synthetic Data

We evaluate fee algorithms using synthetic data simulating various market conditions: high/low volatility, bull, and bear markets (Table I). Our goal is to analyze result variability and establish statistical significance. LP's IL is excluded due to high variance.

The OB algorithm consistently surpasses the FX baseline, demonstrating the benefits of fixed fee strategies. In all conditions, BA outperforms FX in LP Markout, proving its effectiveness, though OB yields superior results. The DA algorithm shows minor improvements over FX , but is less effective compared to BA .

## C. Historical Data

We evaluate fee algorithms under various market conditions, comparing MOs and LP's IL to the FX baseline (Table II).

In a high volatile market , proposed algorithms reduce IU markout significantly compared to FX (883,900), with BA (878,088) and OB (745,471) showing effectiveness. LP markout improves with adaptive algorithms; BA enhances LP profitability to -702,735 from -713,551. OB minimizes IL from 2,146,636 to 1,995,397 in high-volatility environments.

Under low volatile market , the DA algorithm significantly improves metrics, reducing IU profit from 21,547 to 21,326 and increasing LP profit by 2.3% (from 86,924 to 88,922). The OB method further decreases IU markouts by 17% and boosts LP markouts by 7%. Overall, all algorithms ( DA, BA, OB ) enhance IL.

In a bull market , changes in metrics are minor. OB achieves a positive LP markout of 2,719, setting a benchmark for LP profitability. FX records the highest IL (-497,942), while DA and BA reduce IL by 3% and 1.5%, respectively, improving LP markout slightly.

In a bear market , dynamic fee strategies prove resilient. IU markout decreases across all algorithms, with OB achieving superior LP markout (58,253). DA and BA improve LP markout to 45,000 and 44,126, outperforming FX (43,210) by 4% and 2%, respectively.

## VI. CONCLUSIONS AND FUTURE WORK

This study shows that dynamic fee mechanisms, including block-adaptive, deal-adaptive, and oracle-based algorithms, effectively reduce impermanent loss (IL) for liquidity providers on decentralized exchanges (DEXs), outperforming traditional fixed fee models. These dynamic fees adapt to market volatility, compensating LPs during high volatility and reducing inefficiencies and arbitrage between DEXs and CEXs, thus enhancing market efficiency.

Future research should test these algorithms in live DEX environments to verify theoretical results and uncover practical challenges. Incorporating machine learning could further refine fee adaptability by predicting market conditions and user behavior. Additionally, exploring arbitrage opportunities and LP and trader responses to dynamic fees can inform improved algorithm designs that balance market efficiency with user satisfaction.

## REFERENCES

- [1] S. Malamud and M. Rostek, 'Decentralized exchange,' American Economic Review , vol. 107, no. 11, pp. 3320-3362, 2017.
- [2] D. A. Zetzsche, D. W. Arner, and R. P. Buckley, 'Decentralized finance,' Journal of Financial Regulation , vol. 6, no. 2, pp. 172-203, 2020.
- [3] A. Barbon and A. Ranaldo, 'On the quality of cryptocurrency markets: Centralized versus decentralized exchanges,' arXiv preprint arXiv:2112.07386 , 2021.
- [4] Y. Wang, Y. Chen, H. Wu, L. Zhou, S. Deng, and R. Wattenhofer, 'Cyclic arbitrage in decentralized exchanges,' in Companion Proceedings of the Web Conference 2022 , 2022, pp. 12-19.
- [5] S. Hägele, 'Centralized exchanges vs. decentralized exchanges in cryptocurrency markets: A systematic literature review,' Electronic Markets , vol. 34, no. 1, p. 33, 2024.
- [6] A. Nezlobin, 'Post: How do we cut the losses of lps to arbitrageurs by 95%?' 2023. [Online]. Available: https://x.com/0x94305/status/1674857993740111872
- [7] M. Pourpouneh, K. Nielsen, and O. Ross, 'Automated market makers,' IFRO Working Paper, Tech. Rep., 2020.
- [8] J. Nartey, 'The rise of decentralized exchanges and their impact on traditional stock markets,' Available at SSRN 4843453 , 2024.
- [9] C. A. Makridis, M. Fröwis, K. Sridhar, and R. Böhme, 'The rise of decentralized cryptocurrency exchanges: Evaluating the role of airdrops and governance tokens,' Journal of Corporate Finance , vol. 79, p. 102358, 2023.
- [10] A. Capponi and R. Jia, 'The adoption of blockchain-based decentralized exchanges,' arXiv preprint arXiv:2103.08842 , 2021.
- [11] L. Heimbach, Y. Wang, and R. Wattenhofer, 'Behavior of liquidity providers in decentralized exchanges,' arXiv preprint arXiv:2105.13822 , 2021.
- [12] L. Heimbach, E. Schertenleib, and R. Wattenhofer, 'Risks and returns of uniswap v3 liquidity providers,' in Proceedings of the 4th ACM Conference on Advances in Financial Technologies , 2022, pp. 89-101.
- [13] A. A. Aigner and G. Dhaliwal, 'Uniswap: Impermanent loss and risk profile of a liquidity provider,' arXiv preprint arXiv:2106.14404 , 2021.
- [14] N. Bardoscia and A. Nodari, 'Liquidity providers greeks and impermanent gain,' arXiv preprint arXiv:2302.11942 , 2023.
- [15] R. Tangri, P. Yatsyshin, E. A. Duijnstee, and D. Mandic, 'Generalizing impermanent loss on decentralized exchanges with constant function market makers,' arXiv preprint arXiv:2301.06831 , 2023.
- [16] M. Jansen, 'Secure arbitrage trades between centralized and decentralized exchanges,' Edited by Sergey Y. Yurish , p. 5, 2023.
- [17] N. Boonpeam, W. Werapun, and T. Karode, 'The arbitrage system on decentralized exchanges,' in 2021 18th International Conference on Electrical Engineering/Electronics, Computer, Telecommunications and Information Technology (ECTI-CON) . IEEE, 2021, pp. 768-771.
- [18] L. Irina, U. Dmitrii, Y. Yury, M. Ignat, and O. George, 'Dynamic fee for reducing impermanent loss in decentralized exchanges,' https://github.com/swnirk/Dex-Dynamic-Fee/tree/camera-ready, 2025, accessed: 2025-03-25.