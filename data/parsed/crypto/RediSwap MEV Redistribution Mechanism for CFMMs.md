## RediSwap : MEV Redistribution Mechanism for CFMMs

Mengqian Zhang Yale University

mengqian.cs@gmail.com Sen Yang Yale University sen.yang@yale.edu

## Abstract

Automated Market Makers (AMMs) are essential to decentralized finance, offering continuous liquidity and enabling intermediary-free trading on blockchains. However, participants in AMMs are vulnerable to Maximal Extractable Value (MEV) exploitation. Users face threats such as front-running, back-running, and sandwich attacks, while liquidity providers (LPs) incur the loss-versus-rebalancing (LVR).

In this paper, we introduce RediSwap , a novel AMM designed to capture MEV at the application level and refund it fairly among users and liquidity providers. At its core, RediSwap features an MEV-redistribution mechanism that manages arbitrage opportunities within the AMM pool. We formalize the mechanism design problem and the desired game-theoretical properties. A central insight underpinning our mechanism is the interpretation of the maximal MEV value as the sum of LVR and individual user losses. We prove that our mechanism is incentive-compatible and Sybil-proof, and demonstrate that it is easy for arbitrageurs to participate.

We empirically compared RediSwap with existing solutions by replaying historical AMM trades. Our results suggest that RediSwap can achieve better execution than UniswapX in 89% of trades and reduce LPs' loss to under 0.5% of the original LVR in most cases.

Keywords: Decentralized Finance, MEV Redistribution, Mechanism Design

## 1 Introduction

Automated Market Makers (AMMs) have become the leading design for facilitating trades on decentralized exchanges (DEXs). A key feature of AMMs is their use of liquidity pools, which are composed of tokens contributed by liquidity providers (LPs) and accumulated from past trades. This structure enables users to trade directly with the pool, eliminating the need for order matching as seen in the traditional order book system used by centralized exchanges (CEXs).

Despite various benefits, two types of participants in AMMs-users and liquidity providers-suffer from the phenomenon known as Maximal/Miner Extractable Value (MEV) [1]. MEV refers to the profit that intermediaries, such as searchers, builders, and proposers, can extract during the block production. Because trades in DEXs are publicly visible in the mempool before they are confirmed, those monitoring the mempool (e.g., searchers) can profit by front-running, back-running, or sandwiching user trades [2, 3, 4]. As a result, user trades execute at a worse price. For liquidity providers, the primary risk comes from Loss-Versus-Rebalancing (LVR) [5], which quantifies the cost they incur when arbitrageurs rebalance the AMM pools in response to price movements at external markets. The existence of LVR makes it challenging for liquidity providers to earn sustainable profits, even with swap fees.

Fan Zhang

Yale University f.zhang@yale.edu One promising direction to mitigate users' loss is refunding them partial MEV extracted from their trades. MEV-Share [6] and MEV Blocker [7] are primary examples used in practice. However, these refunding mechanisms are rather limited, mainly because they operate near the end of the MEV supply chain, after the trades have been exploited by various intermediaries, such as searchers/arbitrageurs and builders. Moreover, some (e.g., application-level) information is lost as transactions pass through the supply chain. One consequence is unfair redistribution. For instance, in MEV Blocker, the majority of refunds for CoWSwap [8] orders were erroneously delivered to solvers rather than users [9].

On the other hand, UniswapX [10] and CoWSwap are two notable solutions at the application level, an upstream stage of the supply chain. In both systems, users submit intents specifying their desired outcomes, and a market of solvers compete to search for the best settlement. These schemes are expected to provide better execution because solvers can aggregate liquidity from various sources and access more resources (information, capital, and sophisticated execution strategies) than users. However, empirical evidence (as detailed in appendix A) suggests that solvers may not exhibit the expected level of sophistication, emphasizing the need for simpler mechanism designs.

Several parallel works have been proposed to mitigate LVR and compensate liquidity providers. A widely studied approach is to auction off exclusive rights earlier before block generation in exchange for compensation to LPs [11, 12]. A major concern with these ex-ante auctions is that arbitrageurs must bid based on their estimation of future profits, which makes it challenging to engage and discourages risk-averse players. Additionally, other LVR mitigation ideas have been explored, such as reducing the inter-block time and involving dynamic fees [13, 14]. However, like all previous MEV mitigation solutions, these approaches focus solely on protecting the interests of one group (LPs in this case), while do not take the other group of participants into account.

The limitations of existing solutions motivate us to explore AMM designs that can capture MEV at the application level, redistribute MEV fairly among users and LPs, and ensure ease of participation for solvers (arbitrageurs). Particularly, we tackle the research question through the lens of mechanism design.

## 1.1 This Work

In this paper, we propose an MEV-redistribution Constant Function Market Maker (CFMM) [15] called RediSwap . RediSwap addresses the above limitations: the refund mechanism takes both users and LP into consideration; the arbitrageurs only need to take simple actions to participate. Looking ahead, our empirical evaluation suggests that RediSwap achieves better execution results than existing systems while mitigating LVR.

RediSwap has two main components: a CFMM and an MEV-redistribution mechanism that manages arbitrage opportunities 1 within the CFMM pool. We focus on the CFMM with a risky asset and a num´ eraire. The CFMM follows the standard design, except that users send trades to the MEV-redistribution mechanism, which uses the CFMM to execute them; the CFMM does not accept trades directly from users.

The overall workflow of RediSwap is as follows: users privately send transactions to the MEVredistribution mechanism, e.g., via an RPC channel. Arbitrageurs interested in the potential ar- bitrage opportunity provide the MEV-redistribution mechanism with their beliefs regarding the external market price of the risky asset. The MEV-redistribution mechanism is essentially an expost auction to sell arbitrage opportunities to arbitrageurs, specifying three key rules: (1) a bundle generation rule, which constructs a list of transactions (i.e., a bundle) with optimal arbitrage profit based on the inputs from users and arbitrageurs; (2) a payment rule, which decides arbitrageurs' payments, capturing a portion of the MEV within the bundle; and (3) a refund rule, which rebates the captured MEV among users and liquidity providers.

1 We focus on non-atomic arbitrage, which capitalizes on price discrepancies between on-chain DEXs and exchanges in another venue (i.e., CEXs like Binance or DEXs on other blockchains). Non-atomic arbitrage is one of the dominant forms of MEV. Empirical studies indicate that over a quarter of the trading volume on Ethereum's biggest five DEXs is likely attributed to non-atomic arbitrage [16], and since the Ethereum Merge [17], the total profits from CEX-DEX arbitrage have reached $ 131.77M [18].

While RediSwap relies on arbitrageurs (as with UniswapX and CoWSwap), arbitrageurs only need to take simple actions, i.e., to provide their beliefs of the external prices and capital. That is, RediSwap internalizes the complexity of computing optimal arbitrage into the mechanism. Moreover, RediSwap has full control over transaction ordering, which enables transparent MEV capturing and can enforce fair redistribution. Unlike MEV-Share or MEV Blocker, RediSwap does not expose transaction information to arbitrageurs.

## 1.2 Our Contributions

We present the first truthful and Sybil-proof MEV-redistribution mechanism for CFMMs.

In section 3, we formalize the problem of designing an MEV-redistribution mechanism and define the desired properties. Intuitively, we aim for a mechanism that is (for arbitrageurs) incentivecompatible (in the sense that truthfully reporting beliefs regarding the price of the risk asset is a dominant strategy) and Sybil-proof (in the sense that creating Sybil transactions will not decrease any user's utility). Such a mechanism would make it simple for arbitrageurs to participate and not require much sophistication.

Capturing MEV and refunding it to every player requires us to understand not only how to maximize MEV, but also each player's contribution to the MEV. Thus in section 4, we revisit a simpler problem, namely, how to construct an optimal non-atomic arbitrage strategy in the scenario with public order flows. We answer this question from a new perspective using potential functions. Based on the potential function characterization, we argue that the optimal MEV value can be interpreted as the sum of LVR and each user's loss so that we can quantify the loss of each player .

This insight naturally leads to a strawman MEV-redistribution mechanism that sells all MEV opportunities to a single arbitrageur and refunds the winner's payment to users and liquidity providers proportional to each player's loss (section 5). Since the MEV-redistribution mechanism is designed to operate in an open and decentralized environment, arbitrageurs can pose as users and mount Sybil attacks . The strawman solution would allow arbitrageurs to submit 'fake' transactions to steal users' refunds. As a result, such a mechanism is shown to be truthful but, unfortunately, fails to be Sybil-proof.

The key idea in RediSwap (section 6) is to sell the MEV opportunities from each pending transaction and the rebalancing arbitrage separately. The challenge is that the execution of a trade in CFMM is sensitive to the ordering, and so is the MEV value it creates. RediSwap solves this problem by ensuring independence among transactions (and corresponding refunds). Theoretically, we prove that Sybil attacks will not reduce any user's utility, whether being truthful or not (Theorem 4). Moreover, if an arbitrageur in RediSwap has the required resource (i.e., tokens) to mount Sybil attacks, there exists a Sybil strategy such that using this strategy and truthfully reporting is a Nash equilibrium (Theorem 5); otherwise, truthfully reporting is a dominant strategy (Theorem 3).

In section 7, we evaluate our mechanism by replaying historical AMM trades from September 1st, 2023, to August 31st, 2024. To simulate arbitrageurs' beliefs in external prices, we use prices in Binance (a centralized exchange) to build price distribution. By comparing the execution prices of the same order on UniswapX or CoWSwap with RediSwap , we show that our mechanism can achieve better execution prices than UniswapX in 89% of cases, and comparable execution prices to CoWSwap. Our evaluation also shows that RediSwap effectively reduces LVR for the two Uniswap v2 liquidity pools (WETH-USDC and WETH-USDT) we experiment with, and the efficiency strengthens as more arbitrageurs participate. For example, WETH-USDC liquidity providers incur less than 0.5% of the LVR they would face without RediSwap in most cases.

## 2 Related Work

MEV mitigation through AMM design. Several works focus on composing networks of AMMs to achieve better settlement and minimize arbitrage and slippage [19, 20, 21]. Instead of executing transactions sequentially, some designs [8, 22] process transactions in batches at a uniform clearing price, eliminating the risk of cyclic arbitrage and sandwich attacks within a block, though not all forms of manipulation are fully addressed [23]. Some studies have also explored the idea of integrating batch trading with CFMMs [24, 25]. Orthogonally, Ferreira and Parkes [26] initiate the study of verifiable sequencing rules and propose a concrete greedy sequencing rule, which structurally inhibits the feasibility of sandwich attacks. Chan, Wu, and Shi [27] initiate the mechanism design approach/philosophy for mitigating MEV and study a model where relevant strategic players (user or miner) aim to obtain risk-free profit , whereas we focus on non-atomic arbitrage. AnimaguSwap [28] presents an AMM design to achieve data-independent ordering of user transactions at the application level. V0LVER [29] presents an AMM against LVR and MEV based on an encrypted transaction mempool.

Other MEV mitigation solutions. Mitigating the negative effects of MEV is a research focus in both academia and industry, with various studies conducted from different perspectives. A commonly used practice for MEV mitigation is using private channels [7, 30], where user transactions are sent directly to block builders, bypassing the public mempool and thus preventing MEV attacks like front-running and sandwich attacks. Another approach focuses on ensuring time-based order fairness [31, 32, 33, 34]. Miners or validators adhering to time-based order fairness must order transactions based on the time they receive the transaction, preventing MEV caused by ex-post order manipulation. A different method to achieve fair ordering involves users first committing to their transactions and revealing them only after the order has been determined. Thus, the transaction order is determined independently of the content. We refer readers to an SoK paper [35] for a comprehensive understanding of various MEV mitigation approaches.

Sybil-proofness in mechanism design in blockchain. The permissionless nature of blockchain makes it very easy for participants to create multiple identities, thus launching Sybil attacks. To see the challenges, the most successful mechanisms in classic auction theory, such as secondprice auctions and VCG auctions, are vulnerable to Sybil attacks. Since the pioneered work by Roughgarden on transaction fee mechanism design [36] and also for practical consideration, Sybilproofness has become one of the most desired properties for mechanism design in blockchain. Notable examples include the rich transaction fee mechanism design literature [36, 37, 38, 39], voting mechanism [40], and the very recent mechanism in ZK-Rollup prover markets [41]. Mazorra and Penna [42] consider a similar MEV rebates problem in the context of MEV-share combinatorial order flow auctions. They discuss the Shapley value-based mechanism and show that in their setting, any symmetric, efficient, and Strong monotonic rebate mechanism is weak against Sybil strategies.

## 3 Model

## 3.1 The Basic Model

This section describes the basic CFMM pool and all involved players, including liquidity providers, users, and arbitrageurs.

CFMM Pool. We consider a CFMM pool with a risky asset X (e.g., ETH) and a num´ eraire asset Y (e.g., USDC). The pool state s = ( x, y ) is specified by the current reserves of tokens and should satisfy a constant function F ( x, y ). The slope at a state ( x, y ) ∈ F is the spot price or marginal exchange rate ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ .

We do not prescribe a constant function but only require two natural properties on F : (1) for any two points ( x, y ) , ( x ′ , y ′ ) ∈ F , we have x &gt; x ′ ⇔ y &lt; y ′ , namely, when the reserve of X increases, the reserve of Y decreases and vice versa; (2) F ( x, y ) is differentiable and the marginal exchange rate ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ is decreasing with respect to x . Most CFMMs satisfy these two properties, including Uniswap v2 and v3. The two properties imply that for any x , there is exactly one y such that ( x, y ) ∈ F and vice versa. To simplify notations, we use F y ( x ) to denote that y such that ( x, y ) ∈ F and similarly define F x ( y ).

We call the pool's state after the latest block its initial state s 0 = ( x 0 , y 0 ).

Liquidity Providers. Liquidity providers contribute pairs of tokens (e.g., ETH and USDC) to a CFMM pool, which is then used to fulfill users' trade orders. In exchange, LPs earn fees from each trade in the pool. A small fraction f ∈ [0 , 1) of each trade's input tokens are charged as swap fees and are shared by liquidity providers proportional to their contribution to liquidity reserves. The fees are temporarily kept by the pool and can be withdrawn by liquidity providers by burning their liquidity tokens. In our design, the swap fees are stored separately like in Uniswap v3, rather than being continuously deposited in the pool as liquidity (e.g., Uniswap v2). Throughout this paper, we only consider swap-like transactions and assume no liquidity deposit or redemption.

Users/Noise Traders. Users are a population of noise traders who intend to trade through the CFMM pool. Each user holds one type of asset and seeks to exchange it for another by creating a swap transaction. Specifically, a transaction TX = ( X → Y , δ in X , δ out Y ) specifies that the user is willing to spend up to δ in X units of asset X , provided they receive at least δ out Y units of asset Y . Similarly, the signer of transaction TX = ( Y → X , δ in Y , δ out X ) allows at most δ in Y units of Y to be taken from their account if they receive at least δ out X units of X . For simplicity of notations, the terms δ in X and δ in Y refer to the actual quantities of input tokens available for trading, after the fees have been deducted. In this paper, we use trade/order/transaction interchangeably.

Arbitrageurs/Informed Traders. Arbitrageurs are informed traders with access to external markets. They continuously monitor the price disparities between the CFMM and external markets, seeking to profit by arbitrage.

Each arbitrageur i holds a private belief v ∗ i regarding the external price of the risky asset X . These beliefs decide when and how to execute arbitrage opportunities. Arbitrageurs may have different beliefs for various reasons. First, they may focus on different external markets or operate on different timelines for executing off-chain trades. Second, prices can exhibit significant volatility, leading to varying price expectations among arbitrageurs. Lastly, arbitrageurs' trading costs may be different, especially in off-chain trading venues.

Remarks. In today's MEV supply chains, when arbitrageurs compete for such MEV opportunities through MEV auctions [1], most MEV is captured by block builders and proposers. This is un- desirable for redistribution and is avoided in RediSwap because arbitrageurs' competition happens on the CFMM side. A notable feature of the MEV-redistribution mechanism is its ability to insert MEV transactions on behalf of arbitrageurs, which do not need to pay swap fees (namely, f = 0 for them). This enables arbitrageurs to correct even tiny price discrepancies [11] and makes it possible to compute the optimal MEV strategy efficiently (otherwise, the problem becomes NP-hard [23]).

## 3.2 MEV-Redistribution Mechanism

The key novelty of RediSwap is a new MEV-redistribution mechanism, which decides which user transactions should be included in the bundle, which arbitrageurs have the right to insert arbitrage transactions, the sequence of these transactions, and how much MEV value should be refunded to users and liquidity providers. These decisions are formalized by three functions: a bundle generation rule, a payment rule, and a refund rule.

Before presenting the formal definitions, we first introduce necessary notations. We use N to denote the set of n arbitrageurs, and q to denote a n -sized vector where q i is arbitrageur i 's report on the external price of the risky asset X . Their true belief is v ∗ i , which may differ from q i . We assume each arbitrageur i can create any number of Sybil transactions, the set of which is denoted by S i . Thus, we use M = R ∪ S to denote the set of pending transactions in the CFMM pool, where R is a set of real transactions from users, and S = S 1 ∪ S 2 ∪ · · · ∪ S n .

Definition 1 (Bundle Generation Rule) . A bundle generation rule is a function b from the pool's initial state s 0 , pending transactions M , and arbitrageurs' report q to an ordered set B of transactions (a bundle). The elements in B are T ∪ A , where T ⊆ M is a subset of pending transactions, and A = A 1 ∪···∪ A n is the set of MEV transactions inserted by the rule on behalf of arbitrageurs.

Definition 2 (Payment Rule) . A payment rule is a function p from the pool's initial state s 0 , pending transactions M , and arbitrageurs' report q to a non-negative number p i ( s 0 , M, q ) for each arbitrageur i ∈ [ n ] .

Definition 3 (Refund Rule) . A refund rule is a function r from the pool's initial state s 0 , pending transactions M , and arbitrageurs' report q to a non-negative number r ( s 0 , M, q , TX j ) for each transaction TX j ∈ M ; the remaining payments from arbitrageurs, i.e., ∑ i ∈ [ n ] p i ( s 0 , M, q ) -∑ TX j ∈ M r ( s 0 , M, q , TX j ) are refunded to liquidity providers.

When the context is clear, we may shorten r ( s 0 , M, q , TX j ) to r ( TX j ) or r j .

Definition 4 (MEV-Redistribution Mechanism) . An MEV-redistribution mechanism is a triple ( b , p , r ) in which b is a bundle generation rule, p is a payment rule, and r is a refund rule.

## 3.3 Desired Properties

This section formalizes what it means for an MEV-redistribution mechanism to be game-theoretically sound. First of all, an arbitrageur should be incentivized to report their true belief in the external price of the risky asset X (defined as 'Truthful' below). Meanwhile, we must prevent arbitrageurs from stealing user refunds by posing as users in Sybil attacks. As a reminder, we assume that arbitrageurs can submit any number of Sybil transactions, which may receive some refunds. We require that inserting Sybil transactions will not harm users' utilities (defined as 'Sybil-proof' below).

Definition 5 (Arbitrageur Utility Function) . For an MEV-redistribution mechanism ( b , p , r ) , pool's initial state s 0 , pending transactions M , arbitrageurs' report q , and generated bundle B , the utility of arbitrageur i with true belief v ∗ i and Sybil transactions S i ⊆ M is

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where A i ⊆ B is i 's arbitrage transactions inserted by the bundle generation rule b and ( x j , y j ) is the pool's state after the j -th transaction in the bundle.

On the LHS of (1), we highlight the dependence of the utility function on the two arguments that are under arbitrageur i 's direct control: the choices of Sybil transactions S i and the report on external price q i . We also explicitly show its dependence on other arbitrageurs' strategy S -i and q -i . Here, q -i means the vector q of all reports, but with the i -th component removed. This is a standard notation in economics, and we will also use similar notations for other objects (e.g., S -i above). The formula (1a) sums over i 's Sybil transactions included in the generated bundle, the first two terms of which represent i 's revenue from transaction execution, and the third term is the refund received by this transaction. The formula (1b) sums over the revenue from i 's arbitrage transactions added in the bundle by the mechanism. The formula (1c) is the cost i needs to pay for the MEV opportunity, the output of the payment rule.

Definition 6 (Truthful) . An MEV-redistribution mechanism ( b , p , r ) is truthful if, for every pool's initial state s 0 , pending transactions M = R ∪ S -i , and other arbitrageurs' report q -i , for every arbitrageur i , it maximizes its utility (1) by reporting its true belief (i.e., setting q i = v ∗ i ), namely,

<!-- formula-not-decoded -->

Note that we separate the discussion of truthfulness from Sybil proofness, and the above definition assumes that arbitrageur i does not add Sybil transactions.

As mentioned above, arbitrageurs may steal refunds by pretending to be users and submitting fake (Sybil) transactions. An MEV-redistribution mechanism is Sybil-proof in that creating Sybil transactions does not reduce any user's utility.

Definition 7 (User Utility Function) . For an MEV-redistribution mechanism ( b , p , r ) , pool's initial state s 0 , pending transactions M = R ∪ S , arbitrageurs' report q , the utility of the originator of a transaction TX j ∈ R is

<!-- formula-not-decoded -->

where ( X j , Y j ) is the number of tokens the originator has after executed through the mechanism, and δ X = δ in X , δ Y = δ out Y if TX = ( X → Y , δ in X , δ out Y ) ; δ X = δ out X , δ Y = δ in Y if TX = ( Y → X , δ in Y , δ out X ) .

Initially, it's assumed that the user of an X → Y transaction holds δ in X units of X token and no Y token, while the user of an Y → X transaction has δ in Y units of Y token and no X token. After execution, the user's utility depends on the results of the mechanism, where X j and Y j in Equation (2) counts not only the direct execution of TX j but also the extra refund it receives. Additionally, we highlight the dependence of the utility function on the (partial) inputs S and q of the mechanism, which are under arbitrageurs' control though.

Definition 8 (Sybil-proof) . An MEV-redistribution mechanism ( b , p , r ) is Sybil-proof if, for any initial state s 0 , pending transactions M = R ∪ S -i , and arbitrageurs' report q , creating Sybil transactions S i will not reduce users' utility:

<!-- formula-not-decoded -->

## 4 Optimal MEV with Public Orders

Before delving into RediSwap , it is helpful to take a slight detour to consider an optimization problem in standard AMMs where user trades are public . (To reiterate, RediSwap hides user transactions from the public, including arbitrageurs.)

In this setting, transactions are visible to everyone, so arbitrageurs can create their own MEV bundles to exploit arbitrage opportunities between the CFMM and external markets (assuming no swap fee). The key question for each arbitrageur is: what is the optimal MEV strategy to maximize utility given the public order flows?

Without loss of generality, we can discuss this problem from the perspective of an arbitrary arbitrageur, whose belief in the external price of the risky asset X is assumed to be v ∗ . Note that for an arbitrary v ∗ &gt; 0, there is exactly one pool state s ∗ = ( x ∗ , y ∗ ) at which the pool's marginal exchange rate ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ = v ∗ . So we use v ∗ and ( x ∗ , y ∗ ) interchangeably to represent the arbitrageur's belief. Also note that arbitrageurs do not need to create Sybil transactions in this setting, as they can insert arbitrary transactions when constructing the bundle.

## 4.1 Optimal MEV Strategy

Algorithm 1 presents an efficient strategy to extract the maximal MEV. A formal definition of the MEV optimization problem and a detailed elaboration of Algorithm 1 are shown in appendix B, in the interest of space. Our optimal MEV strategy generalizes the polynomial-time algorithm for constant product AMM by Bartoletti et al. [43] to work for all CFMMs satisfying the two natural properties defined in section 3.1. Below, we briefly present the main idea, focusing on the new perspective gained by interpreting the optimal MEV strategy using potential function .

In a special case where there is no user transaction, it is not hard to show that the arbitrageur's best strategy is to insert an arbitrage transaction to change the state ( x, y ) to ( x ∗ , y ∗ ) at which ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ = v ∗ . Given v ∗ , the profit from arbitrage only depends on the starting point ( x, y ). In other words, each state ( x, y ) corresponds to an arbitrage profit, which can be understood as the potential value of that state. So, for the arbitrageur with belief v ∗ , we define the potential value of any pool state s = ( x, y ) as

<!-- formula-not-decoded -->

When the context is clear, we abbreviate this as ϕ ( s ).

When there is a set of m pending user transactions, the key observation is that the execution of certain user transactions can increase the potential profits of arbitrage. Intuitively, the user of TX j and arbitrageur form a zero-sum game, so the worst execution of TX j is the best for the arbitrageur, which happens if TX j is executed at its limit state 2 : ( x l j , y l j ) TX j - - → ( x l j +∆ x j , y l j +∆ y j ),

2 TX j 's limit state s ℓ j = ( x ℓ j , y ℓ j ) is defined as the state at which, when executed, the transaction will pay exactly the maximum amount of input token and receive the minimum amount of output token.

## Algorithm 1: Optimal MEV Strategy under Public Order

```
Input: An initial state s 0 = ( x 0 , y 0 ), a set of users transactions { TX j } j ∈ [ m ] , and the arbitrageur's belief v ∗ which corresponds to the state s ∗ = ( x ∗ , y ∗ ). Output: A bundle for the arbitrageur to obtain the maximal MEV. 1 for each j ∈ [1 : m ] do 2 Current state s j -1 = ( x j -1 , y j -1 ). // Token reserves 3 if TX j = ( X → Y , δ in X , δ out Y ) then 4 ( x ℓ j , y ℓ j ) is the limit state satisfying y ℓ j -F y ( x ℓ j + δ in X ) = δ out Y . 5 Let ∆ x ← δ in X , ∆ y ←-δ out Y . 6 else if TX j = ( Y → X , δ in Y , δ out X ) then 7 ( x ℓ j , y ℓ j ) is the limit state satisfying x ℓ j -F x ( y ℓ j + δ in Y ) = δ out X . 8 Let ∆ x ←-δ out X , ∆ y ← δ in Y . 9 Let ∆ ϕ ← ∆ x · v ∗ +∆ y . 10 if ∆ ϕ ≥ 0 then 11 if x j -1 < x ℓ j then 12 Insert a transaction TX = ( X → Y , δ in X = x ℓ j -x j -1 , δ out Y = y j -1 -y ℓ j ) . 13 else if x j -1 > x ℓ j then 14 Insert a transaction TX = ( Y → X , δ in Y = y ℓ j -y j -1 , δ out X = x j -1 -x ℓ j ) . 15 Place the user transaction TX j . 16 Suppose the current state is ( x, y ). 17 if x < x ∗ then 18 Add a transaction TX = ( X → Y , δ in X = x ∗ -x, δ out Y = y -y ∗ ) . 19 else if x > x ∗ then 20 Add a transaction TX = ( Y → X , δ in Y = y ∗ -y, δ out X = x -x ∗ ) .
```

where (∆ x j , ∆ y j ) is TX j 's impact on the trading pool when executed at its limit state, namely,

<!-- formula-not-decoded -->

From the perspective of the arbitrageur, whether a transaction TX j should be executed depends on its impact on the potential value of the pool state, namely, the difference between the potential value of the post-execution state and that of the pre-execution state. We define such difference as TX j 's potential value ∆ ϕ j :

<!-- formula-not-decoded -->

where v ∗ is the arbitrageur's belief in the external price. If ∆ ϕ j ≥ 0, TX j is profitable, then it will be placed in the bundle and executed at its limit state; otherwise, it will be ignored and bring zero profit. Combining these two cases, the actual value of an arbitrary transaction TX j is denoted by

<!-- formula-not-decoded -->

Based on the above intuition, we reach the following result:

Theorem 1. The arbitrageur's maximal MEV is ϕ ( s 0 , v ∗ ) + ∑ j ∈ [ m ] V ( TX j ) . Furthermore, Algorithm 1 can construct the bundle that obtains the maximal MEV in polynomial time.

The proof is non-trivial and can be found in appendix C.1.

In simple terms, Algorithm 1 enumerates each pending transaction TX j ( j ∈ [ m ]), inserts a frontrunning transaction to make TX j execute at its limit state if it has non-negative potential value (i.e., ∆ ϕ j ≥ 0), and at the end, concludes with a single backrunning transaction to capture all arbitrage profits and stop at the no-arbitrage state ( x ∗ , y ∗ ) aligned with the arbitrageur's belief v ∗ . To provide intuition, we use Example 1 to demonstrate how Algorithm 1 operates and illustrate its capability to capture the maximal MEV.

Example 1. Consider a trading curve defined by F ( x, y ) = xy = 400 , with an initial state of s 0 = (4 , 100) and a swap fee f = 0 . The arbitrageur holds a belief about the external price of asset X , valuing it at v ∗ = 4 , which corresponds to the no-arbitrage state (10 , 40) . There are three pending transactions: TX 1 = ( X → Y , δ in X = 8 , δ out Y = 25) , TX 2 = ( X → Y , δ in X = 30 , δ out Y = 12) , and TX 3 = ( Y → X , δ in Y = 20 , δ out X = 10) .

We now compute the potential value of the initial state, as well as each transaction's limit state, its impact on the trading pool, potential value, and actual value:

- Initial state s 0 : ϕ ( s 0 , v ∗ ) = 36 ;
- TX 1 : ( x ℓ 1 , y ℓ 1 ) = (8 , 50) , (∆ x 1 , ∆ y 1 ) = (8 , -25) , ∆ ϕ 1 = 7 , V ( TX 1 ) = 7 ;
- TX 2 : ( x ℓ 2 , y ℓ 2 ) = (20 , 20) , (∆ x 2 , ∆ y 2 ) = (30 , -12) , ∆ ϕ 2 = 108 , V ( TX 2 ) = 108 ;
- TX 3 : ( x ℓ 3 , y ℓ 3 ) = (20 , 20) , (∆ x 3 , ∆ y 3 ) = ( -10 , 20) , ∆ ϕ 3 = -20 , V ( TX 3 ) = 0 .

According to Theorem 1, the arbitrageur's maximal MEV is ϕ ( s 0 , v ∗ ) + ∑ j ∈ [1:3] V ( TX j ) = 151 . To illustrate the operations and correctness of Algorithm 1, we first provide a more intuitive (but less efficient) way to extract the maximal MEV, and then show its simplification by steps, which corresponds to the result of Algorithm 1.

The more intuitive way is to first 'sandwich' TX 1 and TX 2 (by frontrunning each transaction so it executes at its limit state, followed by a backrunning transaction to revert to the initial state), and then arbitrage the pool to eventually reach the no-arbitrage state (10 , 40) , as illustrated in Figure 1a. To calculate the arbitrageur's profit from this bundle, we can split each backrunning transaction into two smaller ones, allowing the revenue from one of them to offset that from the frontrunning transaction. For instance, TX Back 1 can be divided into TX Back1 1 and TX Back2 1 , changing the state as follows: (16 , 25) TX Back1 1 -- - - → (8 , 50) TX Back2 1 -- - - → (4 , 100) . In this way, the revenue from TX Back2 1 cancels out the revenue from TX Front 1 , making it easy to verify that the profit from the first 'sandwich' (i.e., TX Front 1 , TX 1 , and TX Back 1 ) is exactly V ( TX 1 ) . Similarly, the profit from the second 'sandwich' (i.e., TX Front 2 , TX 2 , and TX Back 2 ) is V ( TX 2 ) . Finally, the profit from the last arbitrage transaction TX Arb 0 is -(10 -4) × 4+(100 -40) = ϕ ( s 0 , v ∗ ) . Hence, the bundle in Figure 1a extracts the maximal MEV for the arbitrageur.

Another approach to split the MEV transitions is shown in Figure 1b, where TX Front 2 and TX Back 2 are divided so that the total profit from transactions with the same symbol is 0. Removing the four transactions with symbols leaves a simplified bundle, shown in Figure 1c, which is the outcome of Algorithm 1. This bundle extracts the same profits as the previous one, confirming that Algorithm 1 can capture the maximal MEV.

<!-- image -->

(a) A bundle to extract the maximal MEV by 'sandwiching' each pending transaction with a nonnegative potential value, followed by an arbitrage transaction to reach the no-arbitrage state. TX Back 1(2) can be divided into TX Back1 1(2) and TX Back2 1(2) and the total profit from TX Back2 1(2) and TX Front 1(2) is 0.

(b) Splitting TX Front 2 and TX Back 2 into two smaller ones. The total profit from transactions marked with the same symbol ( ⋄ or ⊚ ) is 0.

<!-- image -->

(c) Removing the symbol-marked transactions from (b) results in a simplified bundle, which corresponds to the outcome of Algorithm 1 and captures the maximal MEV.

<!-- image -->

Figure 1: An illustration of the optimal MEV strategy for Example 1. Blue dotted lines represent pending transactions from users, while red solid lines represent MEV transactions from the arbitrageur. The transactions in each subgraph form an MEV bundle. Pool states ( x, y ) in the figure are shown in ascending order based on the value of x .

## 4.2 Optimal MEV = LVR + Each User's Loss

The maximal MEV value, namely, the arbitrageur's total profit from Algorithm 1, represents the total loss of liquidity providers and users. One key observation in RediSwap is to attribute MEV to the loss of LP and each user as follows:

<!-- formula-not-decoded -->

Justification of ϕ ( s 0 ) = LVR . LVR [5] quantifies the costs incurred by LPs due to rebalancing arbitrage , a process that corrects the pool's stale price when the external market price changes. LVR is based on a rebalancing strategy , which manages an off-chain portfolio of tokens X and Y to mirror the CFMM pool's holdings of the risky asset X at all times. Specifically, whenever an arbitrage transaction occurs in the pool in response to external price movements-causing the pool to either buy or sell the risky asset-the rebalancing strategy replicates the pool's sell/buy behavior in the off-chain portfolio at the external market using the CEX price. The profit from this rebalancing strategy, representing the difference in monetary value between the LPs' portfolio in the AMM pool and the off-chain rebalancing portfolio, is what defines LPs' LVR . More concretely, let ∆ denote the number of risky assets sold by the pool due to the rebalancing arbitrage. Let p CEX represent the external price and p AMM the execution price of the arbitrage transaction in the pool. LPs' LVR from this trade is then calculated as ∆ · ( p CEX -p AMM ), which is always positive 3 .

Note that in addition to rebalancing arbitrage , the authors of LVR also mention the reversion arbitrage , which occurs when user transactions cause the DEX price to deviate from the CEX price, creating arbitrage opportunities. At a high level, LVR focuses on rebalancing arbitrage, whereas the maximal MEV value above considers both rebalancing and reversion arbitrage. Despite this distinction, it is natural to apply the rebalancing strategy in our context to compute LPs' loss within the bundle of Algorithm 1. Specifically, we can apply the rebalancing strategy described above to all transactions in the bundle and compute the cumulative profits, which corresponds to LVR . Suppose there are k transactions in the bundle and the j -th trade alters the pool state from ( x j -1 , y j -1 ) to ( x j , y j ), with the end state being ( x k , y k ) = ( x ∗ , y ∗ ). Then, by definition, we have:

<!-- formula-not-decoded -->

In the paper that introduces LVR [5], the authors state that 'Our model allows us to quantify the magnitude of profits of rebalancing arbitrageurs, but not reversion arbitrageurs.' The above analysis provides a perspective to understand this statement. It does not mean the rebalancing strategy is not applicable to scenarios involving reversion arbitrage. Rather, when taking the strategy to replicate both noise trades and informed trades without distinction, the profit of each step can be positive or negative. Ultimately, the cumulative profits from noise trades and reversion arbitrage will sum to zero, leaving only the profits derived from rebalancing arbitrage.

User loss. Recall that V ( TX j ) = max { 0 , ∆ ϕ j } represents the actual value of transaction TX j to the arbitrageur, where ∆ ϕ j represents TX j 's maximal potential arbitrage value. If ∆ ϕ j ≥ 0, executing TX j increases the arbitrageur's profit. In other words, V ( TX j ) is TX j 's contribution to arbitrage profits, which, from another perspective, is the loss incurred by the owner of TX j .

3 When the pool sells risky assets, ∆ &gt; 0 and p CEX &gt; p AMM ; when the pool buys risky assets, ∆ &lt; 0 and p CEX &lt; p AMM .

Summary. The analysis above gives a clean interpretation for the maximal MEV value ϕ ( s 0 ) + ∑ j ∈ [ m ] V ( TX j ): arbitrageur's profit is the sum of LPs' loss and the individual user losses. This interpretation helps elucidate the relationship between the maximal MEV, LVR, and user losses within a block and paves the way to develop an MEV-redistribution mechanism.

## 5 Strawman Design

Now, we are ready to proceed with the study of MEV-redistribution mechanisms. In the mechanism design problem, we have n arbitrageurs (rather than a single arbitrageur like in section 4); everyone has their own belief v ∗ i of the external price. The inputs of the mechanism contain (1) pool's initial state s 0 = ( x 0 , y 0 ); (2) pending transactions M ; and (3) arbitrageurs' report q = ( q 1 , · · · , q n ).

Note that arbitrageurs may misreport beliefs and/or submit Sybil transactions. So, the report q i may differ from the true belief v ∗ i for any arbitrageur i ∈ [ n ]. For clarity, we use ˆ s i = (ˆ x i , ˆ y i ) ∈ F to denote the pool state corresponding to i 's report q i , and use s ∗ i = ( x ∗ i , y ∗ i ) ∈ F to denote the pool state corresponding to i 's true belief v ∗ i .

Given the characterization of the optimal MEV and its interpretation as the loss of LPs and users in previous sections, it is natural to have the following design.

## 5.1 Mechanism Description

The main idea of the strawman mechanism is to simulate each arbitrageur i 's maximal MEV based on their report q i , sell all MEV opportunities to the one who obtains the highest MEV, and refund his/her payments to LPs and users following the interpretation in Equation (7). In detail, the strawman mechanism contains the following three rules.

- Bundle generation rule: For each arbitrageur i ∈ [ n ], calculate the maximal MEV value that i can obtain based on his/her report q i :

<!-- formula-not-decoded -->

where ϕ i ( s 0 ) = ϕ ( s 0 , q i ) represents the potential value of the initial state s 0 to arbitrageur i , and V i ( TX j ) = max { 0 , ∆ x j · q i +∆ y j } represents the actual value of TX j to arbitrageur i . Note that these are measured by their report q i (rather than their true value v ∗ i ).

Let's denote this winner by w ∈ [ n ] who corresponds to the highest MEV value, i.e., MEV w = max i ∈ [ n ] MEV i (breaking uniformly at random in the case of a tie). Then we construct a single bundle for the winner w by Algorithm 1, which takes the initial state s 0 , all pending transactions M , and arbitrageur w 's report q w as inputs and outputs a bundle including a subset of pending transactions and some newly added MEV transactions from arbitrageur w .

̸

- Payment rule: Arbitrageur w pays the second highest MEV value in units of the num´ eraire. Namely, the winner w pays p w = max i = w MEV i ; for any other arbitrageur i = w , p i = 0.

̸

- Refund rule: Each pending transaction TX j ∈ M gets refunds r j = V w ( TX j ) MEV w · p w . The remaining part, which is ϕ w ( s 0 ) MEV w · p w , is refunded to LPs in the form of swap fees.

## 5.2 Analysis of Strawman Mechanism

Theorem 2. The strawman mechanism is truthful.

We postpone the proof to appendix C.2, which is conceptually similar to the reasoning behind the truthfulness of second-price auctions. Note that there is a key distinction: In the second-price auction (and most classic auction settings), a bidder's true value is fixed and will not be affected by their bid. In contrast, in the strawman mechanism above, an arbitrageur's report (analogous to the bid in the auction) determines the MEV bundle and, consequently, their profit from it (analogous to the true value). In this way, the mechanism can be seen as an auction, where misreporting not only alters one's bid (and potentially the winner), but also his/her true value if the player wins. This makes the game strategically more complex and interesting than in the second-price auction.

However, this mechanism is not Sybil-proof. As shown in Example 2 below, an arbitrageur can steal refunds by creating Sybil transactions, which decreases users' utility.

Example 2. Consider a similar setting to Example 1, where the trading curve is F ( x, y ) = xy = 400 , with the same initial state s 0 = (4 , 100) and swap fee f = 0 . There are three pending transactions, identical to those described in Example 1: TX 1 = ( X → Y , δ in X = 8 , δ out Y = 25) , TX 2 = ( X → Y , δ in X = 30 , δ out Y = 12) , and TX 3 = ( Y → X , δ in Y = 20 , δ out X = 10) . None of these are Sybil transactions. Unlike Example 1 where there is only one arbitrageur with a price belief of 4 , this scenario involves two arbitrageurs, each holding a different belief about the external price of X , valued at v ∗ 1 = 4 and v ∗ 2 = 1 , corresponding to the pool states (10 , 40) and (20 , 20) , respectively. Both players truthfully report their beliefs. By definitions, the following results are derived:

|   Arbitrageur i |   q i |   ϕ i ( s 0 ) |   V i ( TX 1 ) |   V i ( TX 2 ) |   V i ( TX 3 ) |   MEV i |
|-----------------|-------|---------------|----------------|----------------|----------------|---------|
|               1 |     4 |            36 |              7 |            108 |              0 |     151 |
|               2 |     1 |            64 |              0 |             18 |             10 |      92 |

Following the strawman mechanism, arbitrageur 1 is the winner, and the mechanism constructs a bundle as illustrated in Figure 1c, where all MEV transactions are arbitrageur 1's. Additionally, arbitrageur 1 is required to pay 92 as costs, which are refunded to users and liquidity providers. Based on Definition 5, arbitrageur 1's utility is 151 -92 = 59 . By Definition 7, the utilities for users of TX 1 , TX 2 , and TX 3 are 25 + 7 · 92 , 12 + 108 · 92 , and 20 + 0 · 92 , respectively.

However, arbitrageur 1 can improve his/her utility by submitting a Sybil transaction TX 4 = ( X → Y , δ in = 260 , δ out = 271) . This leads to the following outcome:

151 151 151 X Y

|   Arbitrageur i |   q i |   ϕ i ( s 0 ) |   V i ( TX 1 ) |   V i ( TX 2 ) |   V i ( TX 3 ) |   V i ( TX 4 ) |   MEV i |
|-----------------|-------|---------------|----------------|----------------|----------------|----------------|---------|
|               1 |     4 |            36 |              7 |            108 |              0 |            769 |     920 |
|               2 |     1 |            64 |              0 |             18 |             10 |              0 |      92 |

By doing so, arbitrageur 1 still wins, but his/her utility increases to -769 + 769 920 · 92 + 920 -92 = 59+ 769 920 · 92 , while the utilities for TX 1 and TX 2 decrease to 25+ 7 920 · 92 and 12+ 108 920 · 92 , respectively.

## 6 Our Mechanism

This section introduces the MEV-redistribution mechanism in RediSwap . Recall that the strawman mechanism sells all MEV opportunities to a single arbitrageur. In contrast, the core idea of our mechanism is to allocate the MEV opportunities to multiple arbitrageurs simultaneously.

## 6.1 Mechanism Description

- Bundle generation rule: Our mechanism constructs the bundle following Algorithm 2, which consists of two parts. The first part (see line 1 - 21) goes over pending user transactions, and each iteration starts with computing the limit state ( x ℓ j , y ℓ j ) of transaction TX j ∈ M and the corresponding impact on the pool (∆ x j , ∆ y j ) by Equation (4). Then, the mechanism computes the potential value of TX j to each arbitrageur i ∈ [ n ] and selects the winner w j of this iteration who values TX j the most. If this highest value ∆ ϕ w j &lt; 0, the mechanism skips this transaction. Otherwise, it assigns TX j to the winner w j by constructing a 'sandwich' on behalf of arbitrageur w j . Specifically, the mechanism inserts a frontrunning transaction from state ( x 0 , y 0 ) to ( x l j , y l j ) so that TX j executes at its limit state, followed by a backrunning transaction from the post-execution state ( x l j +∆ x j , y l j +∆ y j ) to the initial state ( x 0 , y 0 ).

After enumerating all pending transactions, the second part of Algorithm 2 (see line 22 - 28) sells the rebalancing arbitrage opportunity by computing the potential value of the initial state to each arbitrageur i ∈ [ n ] and assigning it to the arbitrageur who values it the most. Specifically, the mechanism adds an arbitrage transaction on behalf of the winner to reach the no-arbitrage state corresponding to his/her report.

̸

- Payment rule: Through the bundle generation, there are | M | + 1 winners (note that an arbitrageur may win multiple times), corresponding to | M | pending transactions and the initial state. The payment rule requires each winner to pay the second highest value in units of the num´ eraire. Specifically, for each transaction TX j , the winner w j = arg max i ∈ [ n ] V i ( TX j ) pays max i = w j V i ( TX j ), which is non-negative by definition, and all others pay 0. For the initial state, the winner w ′ = arg max i ∈ [ n ] ϕ i ( s 0 ) pays max i = w ′ ϕ i ( s 0 ), while others pay 0.

̸

̸

- Refund rule: The above payment is refunded to users and liquidity providers, respectively. Specifically, the owner of transaction TX j gets max i = w j V i ( TX j ) and LPs get max i = w ′ ϕ i ( s 0 ).

̸

We emphasize that all the quantities ϕ i ( · ) , ∆ ϕ i , V i ( · ) are based on arbitrageur i 's report q i . Payments and refunds are done by the mechanism.

Here, we reuse the basic setting from Example 2 to showcase how the above mechanism operates.

Example 3. Recall that the setting is as follows: The trading curve is defined by F ( x, y ) = xy = 400 , with the initial state s 0 = (4 , 100) and swap fee f = 0 . There are three pending transactions: TX 1 = ( X → Y , δ in X = 8 , δ out Y = 25) , TX 2 = ( X → Y , δ in X = 30 , δ out Y = 12) , and TX 3 = ( Y → X , δ in Y = 20 , δ out X = 10) . Two arbitrageurs hold a different belief about the external price of X , with values of v ∗ 1 = 4 and v ∗ 2 = 1 , corresponding to the pool states (10 , 40) and (20 , 20) , respectively. Both players report their beliefs truthfully, leading to the following outcomes:

|   Arbitrageur i |   q i |   ϕ i ( s 0 ) |   V i ( TX 1 ) |   V i ( TX 2 ) |   V i ( TX 3 ) |
|-----------------|-------|---------------|----------------|----------------|----------------|
|               1 |     4 |            36 |              7 |            108 |              0 |
|               2 |     1 |            64 |              0 |             18 |             10 |

According to our mechanism, arbitrageur 1 wins the MEV opportunity from TX 1 and TX 2 , while arbitrageur 2 wins the MEV opportunity from TX 3 and the initial state s 0 . To be specific, the bundle generation rule forms a bundle as shown in Figure 2. Additionally, arbitrageur 1 pays 18 , which is finally refunded to the owner of TX 2 ; arbitrageur 2 pays 36 , which is refunded to LPs.

Figure 2: The bundle constructed by our mechanism for Example 3.

<!-- image -->

Intuitively, each pending transaction TX j ∈ M and the initial state s 0 can create some MEV. The proposed mechanism auctions off these MEV opportunities separately, based on the value of TX j or s 0 to each arbitrageur i ∈ [ n ], namely, V i ( TX j ) or ϕ i ( s 0 ). The key observations are two-fold.

First, V i ( TX j ) and ϕ i ( s 0 ) solely depend on the objective information of the transaction/state (and the arbitrageur i 's report q i ), independent of other pending transactions in the pool (and other players' reports). This makes it possible to switch from a single-item auction with very complicated valuation functions, as seen in the strawman mechanism, to | M | +1 separate auctions.

Second, winners of these separate auctions can independently capture their MEV value, i.e., V w j ( TX j ) or ϕ w ′ ( s 0 ). Enabling one arbitrageur to extract their MEV value is relatively straightforward; however, due to the 'ripple effect,' 4 allowing all auction winners to obtain their value within a single bundle is more complex. Our mechanism overcomes this by forming the final bundle as | M | +1 independent sub-bundles. Each pending transaction in M forms its own sub-bundle, which is a 'sandwich' if the transaction's potential value is non-negative for at least one arbitrageur (otherwise, the sub-bundle is empty). The final sub-bundle corresponds to the initial state and consists of a single rebalancing arbitrage transaction. By having each 'sandwich' return to the initial state, these sub-bundles are independent of one another, meaning their construction, the winner's revenue, and the associated payments do not interfere with or rely on other sub-bundles.

## 6.2 Analysis of Our Mechanism

Theorem 3. Our mechanism is truthful.

Theorem 4. Our mechanism is Sybil-proof.

4 In the CFMM context, transactions are executed sequentially. The execution of a transaction in the bundle impacts not only its own outcome (and its owner's utility), but also alters the state of the pool, which then affects the outcomes of subsequent transactions and the utility of other participants. This creates a 'ripple effect,' where a change in one transaction can cascade through the pool and impact all others, which complicates the task of managing multiple arbitrageurs' MEV within a single bundle.

```
Algorithm 2: Bundle Generation Rule of MEV-Redistribution Mechanism in RediSwap Input: An initial state s 0 = ( x 0 , y 0 ), a set of pending transactions M , and arbitrageurs' reports q = ( q 1 , · · · , q n ), each corresponding to a state ˆ s i = (ˆ x i , ˆ y i ). Output: A bundle to be executed by CFMM 1 for each j ∈ [1 : | M | ] do 2 if TX j = ( X → Y , δ in X , δ out Y ) then 3 ( x ℓ j , y ℓ j ) is the limit state satisfying y ℓ j -F y ( x ℓ j + δ in X ) = δ out Y . 4 Let ∆ x ← δ in X , ∆ y ←-δ out Y . 5 else if TX j = ( Y → X , δ in Y , δ out X ) then 6 ( x ℓ j , y ℓ j ) is the limit state satisfying x ℓ j -F x ( y ℓ j + δ in Y ) = δ out X . 7 Let ∆ x ←-δ out X , ∆ y ← δ in Y . 8 for each i ∈ [ n ] do 9 Let ∆ ϕ i ← ∆ x · q i +∆ y . 10 Let ∆ ϕ w j ← max i ∈ [ n ] ∆ ϕ i . // Arbitrageur w j values TX j the most 11 if ∆ ϕ w j ≥ 0 then 12 if x 0 < x ℓ j then 13 Insert a transaction on behalf of arbitrageur w j TX = ( X → Y , δ in X = x ℓ j -x 0 , δ out Y = y 0 -y ℓ j ) . 14 else if x 0 > x ℓ j then 15 Insert a transaction on behalf of arbitrageur w j TX = ( Y → X , δ in Y = y ℓ j -y 0 , δ out X = x 0 -x ℓ j ) . 16 Place the user transaction TX j . 17 Let the current state ( x ′ , y ′ ) ← ( x ℓ j +∆ x, y ℓ j +∆ y ). 18 if x ′ < x 0 then 19 Insert a transaction on behalf of arbitrageur w j TX = ( X → Y , δ in X = x 0 -x ′ , δ out Y = y ′ -y 0 ) . 20 else if x ′ > x 0 then 21 Insert a transaction on behalf of arbitrageur w j TX = ( Y → X , δ in Y = y 0 -y ′ , δ out X = x ′ -x 0 ) . 22 for each i ∈ [ n ] do 23 Let ϕ i ← ( x 0 · q i + y 0 ) -(ˆ x i · q i + ˆ y i ). 24 Let ϕ w ′ ← max i ∈ [ n ] ϕ i . // Arbitrageur w ′ values LVR the most 25 if x 0 < ˆ x w ′ then 26 Add a transaction on behalf of arbitrageur w ′ TX = ( X → Y , δ in X = ˆ x w ′ -x 0 , δ out Y = y 0 -ˆ y w ′ ) . 27 else if x 0 > ˆ x w ′ then 28 Add a transaction on behalf of arbitrageur w ′ TX = ( Y → X , δ in Y = ˆ y w ′ -y 0 , δ out X = x 0 -ˆ x w ′ ) .
```

Theorem 4 tells us that, given the report (which may differ from the true belief), Sybil transactions do not reduce any user's utility. This implies that a user's utility depends on the arbitrageurs' reports while being independent of their decisions to use Sybil transactions or not. Additionally, Theorem 3 demonstrates that for any arbitrageur i ∈ [ n ], if i submits no Sybil transaction (i.e., S i = ∅ ), truthful reporting is a dominant strategy. These two properties make our mechanism seem very close to the ideal mechanism. However, there is a subtle and tricky issue: an arbitrageur's utility is jointly determined by their report and their Sybil behavior. Submitting Sybil transactions to maximize profits may introduce the incentive for arbitrageurs to misreport their beliefs, which in turn may affect users' utilities.

Our ultimate goal is to incentivize arbitrageurs to truthfully report their beliefs, under which users get their deserved utilities in our mechanism. This can be achieved by showing that there is a strategy profile ( v ∗ , S ) that is a Nash equilibrium. In the following, we show that this is indeed true when arbitrageurs have some Sybil budget ( b X i , b Y i ) and each arbitrageur's belief is drawn from some known distribution D i . We use D to denote the collection of all D i 's.

In particular, we show the following theorem:

Theorem 5. There is a Sybil strategy S i ( v ∗ i , b X i , b Y i , D ) such that under our mechanism, using ( v ∗ i , S i ) is a Nash equilibrium for every arbitrageur i ∈ [ n ] .

We postpone the proofs of the above theorems to appendix C.3, C.4, and C.5.

Remark. The bundle generation rule in our mechanism creates the maximal MEV over all possible bundles, which is max i ∈ [ n ] ϕ i ( s 0 ) + ∑ j ∈ [ | M | ] max i ∈ [ n ] V i ( TX j ).

## 7 Evaluation

In this section, we evaluate the efficiency of RediSwap -specifically, whether it improves execution results (i.e., price) for users and reduces loss for liquidity providers. For users, we compare RediSwap to two notable application-level solutions, UniswapX and CoWSwap, to evaluate if orders filled through RediSwap achieve better execution prices than in UniswapX or CoWSwap. For LPs, we compare the LVR of Uniswap v2 LPs with and without the MEV-redistribution mechanism.

## 7.1 Evaluation Methodology

Assumptions. We assume that arbitrageurs have sufficient capital to execute trades between CEXs and DEXs, making it potentially profitable for them to use their own assets to fulfill users' orders. Additionally, the liquidity on CEXs is ample enough to ensure that these arbitrage activities do not materially affect the off-chain price. We justify these assumptions in two ways: First, many arbitrageurs engage in CEX-DEX arbitrage in practice [16]; second, the liquidity on CEXs is generally substantial, as indicated by their high trading volumes (e.g., the 24-hour trading volume of ETH on Binance is $ 8 billion as of October 5th, 2024 [44]). Besides, for simplicity, we assume that the gas usage for a transaction of an order in UniswapX or CoWSwap is the same when the order is filled by RediSwap . We also assume that the priority fee paid by arbitrageurs in RediSwap is up to 1 Gwei. We note that this is a reasonable assumption because the arbitrageurs in RediSwap compete for the opportunity to fulfill orders at the CFMM side instead of participating in auctions at the block producer side.

Distribution of arbitrageurs' beliefs. To simulate arbitrageurs' beliefs in external prices, we obtain historical token price data from Binance [45] over a one-year period, from September 1st,

2023, to August 31st, 2024. Since not all tokens are traded on CEXs, our evaluation focuses on the eight popular tokens: BTC, ETH, USDC, USDT, DAI, LINK, MATIC, and PEPE. Specifically, we obtain candlestick data from Binance with one-second intervals for these tokens. The arbitrageurs' beliefs about a token's price in a block are simulated by a distribution between the highest and lowest prices of the token during the time slot of the block (the specific type of distribution and the number of arbitrageurs are discussed in each experiment).

Historical trades. We collect all orders on UniswapX and CoWSwap within the same time range. Specifically, we gather orders from the DEX Analytics Platform [46] and cross-check them against Dune records [47]. Our evaluation focuses on orders where either the buy or sell side is a stablecoin (USDC, USDT, or DAI), while the counterpart is a token for which we have price data from Binance. In the end, we collect 344,936 orders in UniswapX and 100,618 orders in CoWSwap for comparison. To evaluate the efficiency in reducing LVR, we also collect the state of two Uniswap v2 pools (WETH-USDC and WETH-USDT) in each block over the same time range.

## 7.2 Results

Better execution prices. We replay historical trades to compute the execution price on RediSwap and compare it with the actual execution price on UniswapX or CoWSwap. In the simulation, we vary the number of participating arbitrageurs in RediSwap and explore various belief distributions that arbitrageurs might have for a token. We model searchers' beliefs using a Gaussian distribution [48] with a centered mean and controlled standard deviation, as well as a Pareto distribution [49] with a shape parameter α = 1 . 5, where most arbitrageurs expect lower token valuations, but a few anticipate significantly higher ones.

Additionally, since liquidity pools can charge different swap fees, we tested swap fee settings ranging from 0 to 0.5% (we excluded 1% because the token pairs we focus on are typically concentrated in pools with lower fees [50]). Note that the information on swap fees is not available from historical trades on UniswapX and CoWSwap, as those orders may not involve a pool (e.g., some are filled using solvers' assets; see appendix A).

Figure 3: Percentage of orders with execution prices better than those on UniswapX or CoWSwap. Each marker represents the overall result under different settings of arbitrageurs and swap fees.

<!-- image -->

As shown in Figure 3, we find that execution prices in RediSwap are better than those in UniswapX for 89% of orders when the swap fee is 0. The percentage of orders with better execution prices decreases as the swap fee increases, but it remains 40% when the swap fee is 0.3%. Compared to CoWSwap, our mechanism can provide nearly equally competitive execution prices when the swap fee is 0. The distribution of prices and the number of arbitrageurs have no obvious impact on the results. This may be due to the narrow price range on Binance, which affects visible differences.

Figure 4: Candlestick charts of Binance and UniswapX ETH/USDT prices over time. Missing data indicates that our dataset does not contain relevant orders on UniswapX for those days.

<!-- image -->

To understand why RediSwap outperforms UniswapX in most orders, we select ETH/USDTthe most frequently traded token pair in our dataset-to compare price differences on Binance and UniswapX over time. For UniswapX, we analyze the execution price, the best price (the starting price of UniswapX's Dutch auction), and the worst price (the ending price in the auction, representing the lowest price users are willing to accept to fulfill orders). As shown in Figure 4, we observe that prices on Binance are better than the best price on UniswapX in most cases: for swapping ETH for USDT, the price of ETH on Binance is higher, and for swapping USDT for ETH, the price of ETH on Binance is lower. Given that arbitrageurs' beliefs follow a distribution around the prices on Binance in our simulation, RediSwap can provide users with better execution prices by leveraging the more favorable prices on CEX.

Figure 5: The CDF of LVR reduction for WETH-USDC and WETH-USDT using RediSwap for different numbers of arbitrageurs and price distributions. A smaller LVR reduction ratio on the x-axis indicates greater reduction efficiency.

<!-- image -->

Reducing LVR. For each block in our evaluation period, we computed the LVR incurred by two Uniswap v2 liquidity pools (WETH-USDC and WETH-USDT) when the arbitrageurs perform CEX-DEX arbitrages, with and without using RediSwap . By dividing the loss under RediSwap by the LVR without RediSwap , we can evaluate the proportion of LVR reduction achieved by RediSwap . Similar to the previous evaluation, we also test different settings for the number of arbitrageurs and the distribution of their price beliefs for a token.

As shown in Figure 5, we can see that RediSwap effectively reduces LVR for both liquidity pools, and the reduction improves as more arbitrageurs participate. The heightened competition drives arbitrageur bids closer, ultimately minimizing LVR. For example, in over half of the blocks, the LPs in the WETH-USDC pool will only suffer at most 0.5% of the LVR they would experience without using RediSwap , when there are 20 arbitrageurs with beliefs following a Gaussian distribution.

## 8 Conclusion, Discussion, and Future Works

We have introduced RediSwap , a CFMM aided by an MEV-redistribution mechanism that can capture MEV at the application level and then refund it to the relevant participants (e.g., users and liquidity providers in this paper). We proved that the MEV-redistribution mechanism is truthful and Sybil-proof. Moreover, RediSwap is designed to not rely on arbitrageurs' sophistication. Below, we discuss implementation considerations and future directions.

## 8.1 Implementation Considerations

This paper focuses on the mechanism design problem, and we leave its concrete implementation for future work, for which we do not foresee significant challenges. RediSwap consists of a CFMM pool (a smart contract) and an MEV-redistribution mechanism. The main implementation task is to protect the confidentiality of arbitrageurs' reports 5 . Since most smart contract platforms do not offer confidentiality, the mechanism needs to run in an off-chain environment. This also allows off-loading computation burdens to save on gas costs.

Several tools are available to implement the mechanism. The most straightforward option is to use hardware-based Trusted Execution Environments (TEEs), such as Intel SGX [51] and TDX [52], which are readily available from cloud computing platforms and achieve near-native performance. The high-level workflow is to run the mechanism in a TEE, which accepts (encrypted) inputs from users and arbitrageurs, computes the bundles, and invokes the CFMM pool's smart contract at the appropriate time. Appendix D presents more details.

An alternative implementation is to use a combination of fully homomorphic encryption and zero-knowledge proofs; because sensitive information only needs to remain private for a short period (e.g., minutes), a lower security level may be used to improve performance.

## 8.2 Future Directions

Solver Behaviors. The empirical studies presented in appendix A reveal a discrepancy between the intended design of protocols and the actual behaviors of solvers in both UniswapX and CoWSwap. To summarize, in UniswapX, where solvers are expected to utilize diverse liquidity sources to provide better solutions, over 84% of filled orders turned out to be filled with solvers' own assets. Similarly, CoWSwap is known for matching orders with complementary trading intents (hence the name 'coincidences of wants'), but 76.94% of batches consist of just a single order, indicating that matching instances within batches are very rare.

5 For instance, if the reports q of all arbitrageurs are public, the user of an X → Y transaction can pretend to be an arbitrageur and submit a fake report ¯ q -ϵ where ¯ q = max i ∈ [ n ] q i , in order to get more refunds. Protecting the confidentiality of arbitrageurs' reports can prevent such manipulation.

Although both protocols are solver-based, a key difference lies in the nature of solver competition. In CoWSwap, solvers compete internally within the protocol, with only the solver providing the best solution being rewarded and their solution selected for settlement on-chain. This incentivizes solvers to align more closely with user interests, as they must offer the best solution to win the competition. In contrast, in UniswapX, any solver who can successfully fulfill an order can do so by simply sending a transaction. As a result, solvers are incentivized to fulfill orders at the specified limit price without optimizing for the best execution. This difference in competitive structure creates a divergence in solver incentives between the two protocols, with CoWSwap's model better aligning solver behavior with user outcomes, as supported by our evaluation results in section 7.2.

A potential avenue for future research would be to investigate solvers' performance in solverbased protocols using a broader set of metrics and analyze the underlying factors driving these behaviors. This could provide valuable insights into improving protocol design, particularly to align solver incentives more effectively with user needs.

MEV Capturing in other DeFi Applications. Results in this paper can naturally extend to the CFMM pool where both X and Y are risky assets or stablecoins. This extension involves two key modifications. First, the arbitrageur's beliefs are about the external prices of two assets, denoted as v ∗ X and v ∗ Y . Accordingly, the arbitrageurs need to report both values in the mechanism. Second, the potential value of a pool state in Equation (3) is adjusted to be ( x · v ∗ X + y · v ∗ Y ) -( x ∗ · v ∗ X + y ∗ · v ∗ Y ), where ( x ∗ , y ∗ ) represents the no-arbitrage state at which ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ = v ∗ X /v ∗ Y . Consequently, all subsequent related definitions are updated to reflect this modification.

Beyond the non-atomic arbitrage considered in this work, other types of MEV, such as atomic arbitrage within or across DEXs, are also worth studying. Furthermore, similar methods to capturing and redistributing MEV at the application level could potentially be applied to other DeFi applications, such as lending platforms and oracles (c.f. oracle extractable values [53]), where MEV might manifest differently.

## Acknowledgements

We thank DEX Analytics and Allium for providing the historical order data.

## References

- [1] P. Daian, S. Goldfeder, T. Kell, Y. Li, X. Zhao, I. Bentov, L. Breidenbach, and A. Juels, 'Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability,' in 2020 IEEE symposium on security and privacy (SP '20) . IEEE, 2020, pp. 910-927.
- [2] K. Qin, L. Zhou, and A. Gervais, 'Quantifying Blockchain Extractable Value: How dark is the forest?' in 2022 IEEE Symposium on Security and Privacy (SP '22) . IEEE, 2022, pp. 198-214.

- [3] C. F. Torres, R. Camino et al. , 'Frontrunner Jones and the Raiders of the Dark Forest: An Empirical Study of Frontrunning on the Ethereum Blockchain,' in 30th USENIX Security Symposium (USENIX Security '21) , 2021, pp. 1343-1359.
- [4] L. Zhou, K. Qin, C. F. Torres, D. V. Le, and A. Gervais, 'High-Frequency Trading on Decentralized On-Chain Exchanges,' in 2021 IEEE Symposium on Security and Privacy (SP '21) . IEEE, 2021, pp. 428-445.
- [5] J. Milionis, C. C. Moallemi, T. Roughgarden, and A. L. Zhang, 'Automated Market Making and Loss-Versus-Rebalancing,' arXiv preprint arXiv:2208.06046 , 2022.
- [6] Flashbots, 'MEV-Share,' https://docs.flashbots.net/flashbots-protect/mev-share/, 2024, accessed: 2024-10-08.
- [7] MEV Blocker, 'MEV Blocker,' https://mevblocker.io/, 2023, accessed: 2024-10-08.
- [8] CoW DAO, 'CoW Protocol Documentation,' https://docs.cow.fi/cow-protocol, 2022, accessed: 2024-10-05.
- [9] C. Protocol, 'MEV Blocker,' https://dune.com/cowprotocol/mev-blocker, 2023, accessed: 2024-10-10.
- [10] Uniswap, 'UniswapX Overview,' https://docs.uniswap.org/contracts/uniswapx/overview, 2023, accessed: 2024-10-05.
- [11] A. Adams, C. Moallemi, S. Reynolds, and D. Robinson, 'am-AMM: An Auction-Managed Automated Market Maker,' arXiv preprint arXiv:2403.03367 , 2024.
- [12] Josojo, 'MEV capturing AMM (McAMM),' 2022, accessed: 2024-10-08. [Online]. Available: https://ethresear.ch/t/mev-capturing-amm-mcamm/13336
- [13] R. Fritsch and A. Canidio, 'Measuring Arbitrage Losses and Profitability of AMM Liquidity,' in Companion Proceedings of the ACM on Web Conference (WWW '24) , 2024, pp. 1761-1767.
- [14] J. Milionis, C. C. Moallemi, and T. Roughgarden, 'The Effect of Trading Fees on Arbitrage Profits in Automated Market Makers,' in International Conference on Financial Cryptography and Data Security (FC '23) . Springer, 2023, pp. 262-265.
- [15] G. Angeris and T. Chitra, 'Improved Price Oracles: Constant Function Market Makers,' in Proceedings of the 2nd ACM Conference on Advances in Financial Technologies (AFT '20) , 2020, pp. 80-91.
- [16] L. Heimbach, V. Pahari, and E. Schertenleib, 'Non-Atomic Arbitrage in Decentralized Finance,' in 2024 IEEE Symposium on Security and Privacy (SP '24) . IEEE Computer Society, 2024, pp. 224-224.
- [17] Ethereum Foundation, 'The Merge - ethereum.org,' 2024, accessed: 2024-10-10. [Online]. Available: https://ethereum.org/en/roadmap/merge/
- [18] Sorella, 'Sorella dashboard,' 2024, accessed: 2024-10-07. [Online]. Available: https: //sorellalabs.xyz/dashboard

- [19] G. Angeris, A. Evans, T. Chitra, and S. Boyd, 'Optimal Routing for Constant Function Market Makers,' in Proceedings of the 23rd ACM Conference on Economics and Computation (EC '22) , 2022, pp. 115-128.
- [20] D. Engel and M. Herlihy, 'Composing Networks of Automated Market Makers,' in Proceedings of the 3rd ACM Conference on Advances in Financial Technologies (AFT '23) , 2021, pp. 15-28.
- [21] L. Zhou, K. Qin, and A. Gervais, 'A2MM: Mitigating Frontrunning, Transaction Reordering and Consensus Instability in Decentralized Exchanges,' arXiv preprint arXiv:2106.07371 , 2021.
- [22] G. Ramseyer, A. Goel, and D. Mazi` eres, 'SPEEDEX: A Scalable, Parallelizable, and Economically Efficient Decentralized EXchange,' in 20th USENIX Symposium on Networked Systems Design and Implementation (NSDI '23) , 2023, pp. 849-875.
- [23] M. Zhang, Y. Li, X. Sun, E. Chen, and X. Chen, 'Computation of Optimal MEV in Decentralized Exchanges,' Working paper-https://mengqian-zhang.github.io/papers/batch.pdf, Tech. Rep., 2024.
- [24] A. Canidio and R. Fritsch, 'Batching Trades on Automated Market Makers,' in 5th Conference on Advances in Financial Technologies (AFT '23) . Schloss-Dagstuhl-Leibniz Zentrum f¨ ur Informatik, 2023.
- [25] G. Ramseyer, M. Goyal, A. Goel, and D. Mazi` eres, 'Augmenting Batch Exchanges with Constant Function Market Makers,' arXiv preprint arXiv:2210.04929 , 2022.
- [26] M. V. Xavier Ferreira and D. C. Parkes, 'Credible Decentralized Exchange Design via Verifiable Sequencing Rules,' in Proceedings of the 55th Annual ACM Symposium on Theory of Computing (STOC '23) , 2023, pp. 723-736.
- [27] T. Chan, K. Wu, and E. Shi, 'Mechanism Design for Automated Market Makers,' arXiv preprint arXiv:2402.09357 , 2024.
- [28] S. Wadhwa, L. Zanolini, F. D'Amato, A. Asgaonkar, C. Fang, F. Zhang, and K. Nayak, 'Data Independent Order Policy Enforcement: Limitations and Solutions,' Cryptology ePrint Archive , 2023.
- [29] C. McMenamin and V. Daza, 'An AMM minimizing user-level extractable value and lossversus-rebalancing,' arXiv preprint arXiv:2301.13599 , 2023.
- [30] Flashbots, 'Flashbots Protect Overview,' https://docs.flashbots.net/flashbots-protect/ overview, 2024, accessed: 2024-10-20.
- [31] M. Kelkar, F. Zhang, S. Goldfeder, and A. Juels, 'Order-Fairness for Byzantine Consensus,' in 40th Annual International Cryptology Conference, (CRYPTO '20) . Springer, 2020, pp. 451-480.
- [32] M. Kelkar, S. Deb, S. Long, A. Juels, and S. Kannan, 'Themis: Fast, Strong Order-Fairness in Byzantine Consensus,' in Proceedings of the 2023 ACM SIGSAC Conference on Computer and Communications Security (CCS '23) , 2023, pp. 475-489.

- [33] Y. Zhang, S. Setty, Q. Chen, L. Zhou, and L. Alvisi, 'Byzantine Ordered Consensus without Byzantine Oligarchy,' in 14th USENIX Symposium on Operating Systems Design and Implementation (OSDI '20) , 2020, pp. 633-649.
- [34] C. Cachin, J. Mi´ ci´ c, N. Steinhauer, and L. Zanolini, 'Quick Order Fairness,' in International Conference on Financial Cryptography and Data Security (FC '22) . Springer, 2022, pp. 316-333.
- [35] S. Yang, F. Zhang, K. Huang, X. Chen, Y. Yang, and F. Zhu, 'SoK: MEV Countermeasures: Theory and Practice,' arXiv preprint arXiv:2212.05111 , 2022.
- [36] T. Roughgarden, 'Transaction Fee Mechanism Design,' in Proceedings of the 22nd ACM Conference on Economics and Computation (EC '21) , P. Bir´ o, S. Chawla, and F. Echenique, Eds. ACM, 2021, p. 792. [Online]. Available: https://doi.org/10.1145/3465456.3467591
- [37] M. Bahrani, P. Garimidi, and T. Roughgarden, 'Transaction Fee Mechanism Design in a Post-MEV World,' in 6th Conference on Advances in Financial Technologies (AFT '24), September 23-25, 2024, Vienna, Austria , ser. LIPIcs, R. B¨ ohme and L. Kiffer, Eds., vol. 316. Schloss Dagstuhl - Leibniz-Zentrum f¨ ur Informatik, 2024, pp. 29:1-29:24. [Online]. Available: https://doi.org/10.4230/LIPIcs.AFT.2024.29
- [38] H. Chung, T. Roughgarden, and E. Shi, 'Collusion-Resilience in Transaction Fee Mechanism Design,' arXiv preprint arXiv:2402.09321 , 2024.
- [39] Y. Gafni and A. Yaish, 'Barriers to Collusion-resistant Transaction Fee Mechanisms,' arXiv preprint arXiv:2402.08564 , 2024.
- [40] J. Lenzi, 'An Efficient and Sybil Attack Resistant Voting Mechanism,' arXiv preprint arXiv:2407.01844 , 2024.
- [41] W. Wang, L. Zhou, A. Yaish, F. Zhang, B. Fisch, and B. Livshits, 'Mechanism Design for ZK-Rollup Prover Markets,' arXiv preprint arXiv:2404.06495 , 2024.
- [42] B. Mazorra and N. Della Penna, 'Towards Optimal Prior-Free Permissionless Rebate Mechanisms, with applications to Automated Market Makers &amp; Combinatorial Orderflow Auctions,' arXiv preprint arXiv:2306.17024 , 2023.
- [43] M. Bartoletti, J. H.-y. Chiang, and A. Lluch Lafuente, 'Maximizing Extractable Value from Automated Market Makers,' in International Conference on Financial Cryptography and Data Security (FC '22) . Springer, 2022, pp. 3-19.
- [44] Binance, 'ETH Price,' 2024, accessed: 2024-10-05. [Online]. Available: https: //www.binance.com/en/price/ethereum
- [45] Binance, 'Historical market data,' 2024, accessed: 2024-10-05. [Online]. Available: https://www.binance.com/en/landing/data
- [46] D. Analytics, 'DEX Trades Dataset,' https://dexanalytics.org/schemas/dex-trades, 2024, accessed: 2024-10-05.
- [47] Dune Analytics. (2024) Dune. [Online]. Available: https://dune.com/

- [48] W. Feller, An introduction to probability theory and its applications, Volume 2 . John Wiley &amp; Sons, 1991, vol. 81.
- [49] B. C. Arnold, 'Pareto distribution,' Wiley StatsRef: Statistics Reference Online , pp. 1-10, 2014.
- [50] Etherscan, 'Etherscan DEX,' https://etherscan.io/dex, 2024, accessed: 2024-10-17.
- [51] V. Costan, 'Intel SGX explained,' IACR Cryptol, EPrint Arch , 2016.
- [52] Intel, 'Intel Trust Domain Extensions (TDX) Documentation,' https://www.intel.com/ content/www/us/en/developer/tools/trust-domain-extensions/documentation.html, 2023, accessed: 2024-10-23.
- [53] Oracles and the new frontier for application-owned orderflow auctions -multicoin capital. [Online]. Available: https://multicoin.capital/2023/12/14/ oracles-and-the-new-frontier-for-application-owned-orderflow-auctions/
- [54] C. Protocol, 'CowSwap Dashboard,' https://dune.com/cowprotocol/cowswap, 2024, accessed: 2024-10-08.

## A Analysis of the orders in UniswapX and CoWSwap

In this section, we analyze how the users' orders are fulfilled on UniswapX and CoWSwap. In particular, we are interested in the following questions:

1. How many orders are filled through direct exchanges between users and solvers?
2. How many orders are filled through batch auctions?

The first question examines the percentage of orders directly filled by solvers' assets rather than liquidity pools in DEXs. The second question evaluates the effectiveness of the batch auction process, where orders can be fulfilled together by a solver as a group, known as a batch . If a batch contains only one order, it suggests that the batch auction's effectiveness is lower than expected, as there is no counterpart order within the batch.

The answers to these questions reveal how solvers fulfill orders-whether they simply use their own assets or aggregate orders in a more complex manner.

Orders collection. We collect 663,831 orders on CoWSwap from the DEX Analytics Platform [46] during the period from September 1, 2023, to August 31, 2024. We cross-check these CoWSwap orders with records on Dune [54] and find that the number of orders matched. Similarly, we collect 726,789 orders on UniswapX from the DEX Analytics Platform within the same date range and cross-checked them against Dune records. The results from both sources matched, indicating the accuracy of our collected data.

The number of orders filled through direct exchanges. An order can be filled through various solutions, such as existing liquidity pools like Uniswap v2/v3, or through direct exchange between the solver and the user. Since there is no public dataset that directly indicates how an order in UniswapX or CoWSwap is filled, to answer the first question, we need to differentiate the solutions by which an order is filled. A key observation in answering this question is that if an order is directly filled through token exchanges between a filler and a user, the process does not involve any liquidity pool .

Based on this observation, we use a heuristic to determine whether an order is directly filled through a filler-user token exchange. If a transaction includes only a user order, and this order is filled without involving any liquidity pool, we infer that it must be filled by direct exchange.

We apply this heuristic to the historical orders we collected, and the results are shown in Figure 6. A surprising finding is that over 84% of the orders on UniswapX were filled through direct token exchange between solvers and users, suggesting that this solution is widely used by active solvers on UniswapX. In comparison, a smaller percentage of orders on CoWSwap were filled through direct exchange-the percentage ranges from 12.5% to 17.7%.

One possible explanation for the difference between these two protocols is that different sets of solvers are active in UniswapX and CoWSwap, respectively. For example, an active solver 6 on UniswapX did not participate in CoWSwap.

The number of orders per batch. When collecting historical orders on UniswapX and CoWSwap, we also recorded the hash of the transaction in which each order was filled and the solver who fulfilled it. Note that a batch refers to a group of orders filled by a solver within a single transaction. Using the collected data, we can compute the number of orders filled within each batch. The distribution of the number of orders per batch is shown in Figure 7.

6 0xfbeedcfe378866dab6abbafd8b2986f5c1768737

Figure 6: Percentage of orders filled by direct exchange between users and solvers.

<!-- image -->

An interesting observation from Figure 7a is that over 99% of batches on UniswapX contained only a single filled order. In contrast, as shown in Figure 7b, 17.6% of batches on CoWSwap contained two filled orders, while fewer than 6% of batches contained more than three orders, and fewer than 0.5% included more than five orders.

Figure 7: Distribution of the number of orders per batch.

<!-- image -->

## B MEV Optimization Problem under Public Orders

Without loss of generality, we discuss the MEV optimization problem from the perspective of an arbitrary arbitrageur. The setting is summarized as follows:

- There is a CFMM pool with a risky asset X and a num´ eraire asset Y ;
- The pool's initial state is s 0 = ( x 0 , y 0 );
- There is a set of public pending transactions M = { TX 1 , · · · , TX m } from users;
- The arbitrageur's belief in the external price of the risky asset X is v ∗ . Note that for an arbitrary v ∗ &gt; 0, there is exactly one pool state s ∗ = ( x ∗ , y ∗ ) at which the pool's marginal

exchange rate ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ = v ∗ . So sometimes we use v ∗ and ( x ∗ , y ∗ ) interchangeably to represent the arbitrageur's belief.

Note that in this setting, arbitrageurs do not need to create Sybil transactions in advance, as they can insert arbitrary transactions when constructing the bundle. The MEV optimization problem can be formalized by defining the arbitrageur's strategy space and utility function as follows.

Definition 9 (Strategy Space in the MEV Optimization Problem) . Given an initial state s 0 = ( x 0 , y 0 ) and a set of user transactions { TX j } j ∈ [ m ] , an arbitrageur can construct a bundle by selecting a subset of users' transactions T ⊆ [ m ] , creating a set of his/her own transactions A = { TX j } j ∈ [ m +1: m + a ] , and picking an execution order (a permutation) over these transactions π : [ | T | + | A | ] → T ∪ A .

Definition 10 (Utility Function in the MEV Optimization Problem) . Arbitrageur's profit is

<!-- formula-not-decoded -->

where v ∗ is the arbitrageur's belief in the external price of X , and ( x j , y j ) is the pool's state after the j -th transaction in the bundle.

This utility function is a simplified version of Formula (1), as it only contains the profits from arbitrage transactions represented by Formula (1b). The arbitrageur's objective is to find a strategy ( T, A, π ) that maximizes their MEV profits, which we refer to as an optimal MEV strategy .

## B.1 Optimal MEV Strategy

This section elaborates on the strategy stated in Algorithm 1 for the arbitrageur to efficiently extract the maximal MEV value from any set of user transactions.

Roughly speaking, Algorithm 1 can be divided into two parts. The first part (see line 1 - 15) enumerates all transactions and tries to ensure that if a transaction is profitable, it will be executed exactly at its limit state (defined below). Specifically, for each transaction TX j , we first preprocess it in line 3 - 8: Recall that each transaction specifies the maximum input amount ( δ in ) and minimum output amount ( δ out ). Based on the transaction information, TX j 's limit state s ℓ j = ( x ℓ j , y ℓ j ) is defined as the state at which, when executed, the transaction will pay exactly the maximum amount of input token and receive the minimum amount of output token. For example, suppose TX j = ( X → Y , δ in X , δ out Y ), then the limit state ( x ℓ j , y ℓ j ) is the state satisfying y ℓ j -F y ( x ℓ j + δ in X ) = δ out Y . Likewise, if TX j = ( Y → X , δ in Y , δ out X ), then ( x ℓ j , y ℓ j ) satisfies x ℓ j -F x ( y ℓ j + δ in Y ) = δ out X . Furthermore, we denote the transaction TX j 's impact on the trading pool when executed at its limit state by (∆ x j , ∆ y j ) which is defined as

<!-- formula-not-decoded -->

meaning that the transaction will bring δ in amount of input tokens to the pool and take δ out amount of output tokens away from the pool.

Next, the algorithm decides whether to execute TX j depending on the transaction's potential value ∆ ϕ j , which is defined as

<!-- formula-not-decoded -->

where v ∗ is the arbitrageur's belief in the external price. If ∆ ϕ j &lt; 0, the algorithm directly ignores this transaction and moves on to the next iteration; otherwise (see line 10 - 15), inserts an arbitrageur's transaction such that the after-execution state is exactly ( x ℓ j , y ℓ j ), then executes TX j .

After that, we come to the second part of the algorithm (see line 16 - 20), which compares the current pool state ( x, y ) with the no-arbitrage state s ∗ = ( x ∗ , y ∗ ) corresponding to the belief v ∗ , and ensures that the pool will stop at the state s ∗ by adding an arbitrage transaction if needed.

The high-level idea about the Algorithm 1 and an intuitive example can be found in section 4.1.

## C Missing Proofs

## C.1 Proof of Theorem 1

Before going into the formal proofs, we first present a lemma (Lemma 2) that characterizes the upper bound of the arbitrageur's profits. (Later, we will prove that Algorithm 1 can exactly get this value.)

Lemma 1. For any belief v ∗ and any pool state s = ( x, y ) , the state's potential value for the arbitrageur ϕ ( s, v ∗ ) ≥ 0 .

Proof of Lemma 1. Fix an arbitrary belief v ∗ , there is a unique pool state ( x ∗ , y ∗ ) ∈ F at which y ∗ x ∗ = v ∗ . For any state s = ( x, y ) ∈ F , there are three cases:

Case 1: x = x ∗ and y = y ∗ . ϕ ( s

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Lemma 2. Given an initial state s 0 = ( x 0 , y 0 ) , a set of users transactions { TX j } j ∈ [ m ] , and the arbitrageur's price belief v ∗ , the arbitrageur's profit is upper bounded by ϕ ( s 0 , v ∗ ) + ∑ j ∈ [ m ] V ( TX j ) .

Proof of Lemma 2. Fix an arbitrary sequence of the mixed arbitrageur's and users' transactions ( TX π (1) , · · · , TX π ( m + a ) ) , where TX π ( j ) is a user transaction if π ( j ) ∈ [ m ] and it is the arbitrageur's transaction otherwise. We will inductively show that after executing the first k transactions, the arbitrageur's profit U k ≤ ϕ ( s 0 )+ V k where V k := ∑ j ∈ [ k ] ,π ( j ) ∈ [ m ] V ( TX π ( j ) ). This will imply that after executing all m + a transactions, the arbitrageur's profit is upper bounded by ϕ ( s 0 )+ ∑ k ∈ [ m ] V ( TX k ).

Let s k be the state after executing TX π ( k ) and ϕ k = ϕ ( s k ). We focus on U k + ϕ k where U 0 + ϕ 0 = 0+ ϕ ( s 0 ) = ϕ ( s 0 ). Let V ( TX π ( k ) ) = 0 if it is the arbitrageur's transaction. We will show that ( U k + ϕ k ) -( U k -1 + ϕ k -1 ) ≤ V k -V k -1 = V ( TX π ( k ) ) for all k ∈ [ m + a ], which will imply our desired statement U k ≤ ϕ ( s 0 ) + V k for all k ∈ [ m + a ], as ϕ k ≥ 0 always holds according to Lemma 1. For each k ∈ [ m + a ], there are two cases: TX π ( k ) is from a user or the arbitrageur.

Case 1: TX π ( k ) is a user transaction. In this case, U k = U k -1 . So it suffices to show that ϕ k -ϕ k -1 ≤ V ( TX π ( k ) ). According to Equation (3), ϕ k -ϕ k -1 = ( x k -x k -1 ) · v ∗ -( y k -1 -y k ).

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

By the definition of V ( · ), the inequality ∆ ϕ π ( k ) ≤ V ( TX π ( k ) ) naturally holds, so we have ϕ k -ϕ k -1 ≤ V ( TX π ( k ) ) which concludes the first case.

Case 2: TX π ( k ) is the arbitrageur's transaction. In this case, V k = V k -1 . Then it suffices to show that ( U k + ϕ k ) -( U k -1 + ϕ k -1 ) ≤ 0. By definition (see Equation (9)), we have U k -U k -1 =

( x k -1 -x k ) · v ∗ + ( y k -1 -y k ), which is exactly ϕ k -1 -ϕ k according to Equation (3). Thus, ( U k + ϕ k ) -( U k -1 + ϕ k -1 ) = 0, concluding the second case.

This finishes the proof of Lemma 2.

Next, we go back to Theorem 1 and prove that Algorithm 1 captures this upper bound.

Proof of Theorem 1. Algorithm 1 enumerates all given transactions and outputs an execution sequence, including both user transactions and newly inserted/added transactions from the arbitrageur him/herself.

Let s j be the state after the j -th iteration where j ∈ [ m ], ϕ j be the value of state s j according to Equation (3), and U j be the utility of the arbitrageur at that state according to Equation (9). We focus on U j + ϕ j .

Initially, we have U 0 = 0 and ϕ 0 = ϕ ( s 0 ), thus U 0 + ϕ 0 = ϕ ( s 0 ).

Then for each iteration j ∈ [ m ], we decide whether to execute TX j based on ∆ ϕ j . If ∆ ϕ j &lt; 0, we choose to skip, so U + ϕ remains unchanged, namely, U j + ϕ j = U j -1 + ϕ j -1 . Otherwise (i.e., ∆ ϕ j ≥ 0), we execute an arbitrageur's transaction (if needed) followed by the user's transaction TX j . Note that the execution of the arbitrage transaction changes the pool state from ( x j -1 , y j -1 ) to ( x ℓ j , y ℓ j ), during which U j -1 and ϕ j -1 change to be U ′ and ϕ ′ respectively. Then we have

<!-- formula-not-decoded -->

Next, the execution of user transaction TX j changes U ′ and ϕ ′ into U j and ϕ j , respectively. Here, we have U j = U ′ and ϕ j = ϕ ′ +∆ ϕ j . Thus, U j + ϕ j = U ′ + ϕ ′ +∆ ϕ j . In both cases (∆ ϕ j &lt; 0 or ∆ ϕ j ≥ 0), we have U j + ϕ j = U ′ + ϕ ′ +max { 0 , ∆ ϕ j } = U j -1 + ϕ j -1 + V ( TX j ) .

Iteratively, we have U m + ϕ m = ϕ ( s 0 ) + ∑ j ∈ [ m ] V ( TX j ) after the m -th iteration. At the end of the algorithm, we conclude the strategy with an arbitrage transaction such that we will stop at the state s ∗ = ( x ∗ , y ∗ ) corresponding to the arbitrageur's belief v ∗ . In this process, U m and ϕ m change to be U and ϕ ( s ∗ ), where ϕ ( s ∗ ) = 0 by definition. According to Equation (10), U = U m + ϕ m = ϕ ( s 0 ) + ∑ j ∈ [ m ] V ( TX j ).

This finishes the proof.

## C.2 Proof of Theorem 2

Proof of Theorem 2. Fix an arbitrary arbitrageur i , its true belief v ∗ i , and the reports q -i of the other arbitrageurs. We will show that arbitrageur i 's utility is maximized by setting q i = v ∗ i .

̸

Let MEV = max k = i MEV k denote the highest MEV value by some other arbitrageur k = i . Note that the definition of truthfulness assumes arbitrageur i adds no Sybil transactions, namely, S i = ∅ . This implies that by reporting q i , if the induced MEV value MEV i ≥ MEV , then i wins and receives utility ∑ TX π ( j ) ∈ A i [ ( x j -1 -x j ) · v ∗ i +( y j -1 -y j ) ] -p i according to (1), where A i is the set of newly inserted arbitrage transactions for i in the bundle generation step; if the report q i induces that MEV i &lt; MEV , then i loses and receives utility 0.

̸

Denote the MEV value corresponding to i 's true belief v ∗ i by MEV ∗ i . Theorem 1 tells us that ∑ TX π ( j ) ∈ A i [ ( x j -1 -x j ) · v ∗ i +( y j -1 -y j ) ] ≤ MEV ∗ i . We conclude by considering two cases. First, if MEV ∗ i &lt; MEV , the maximum utility that arbitrageur i can obtain is 0, and i achieves this by reporting truthfully (and losing). Second, if MEV ∗ i ≥ MEV , the maximum utility that arbitrageur i can obtain is max { 0 , ∑ TX π ( j ) ∈ A i [ ( x j -1 -x j ) · v ∗ i +( y j -1 -y j ) ] -MEV } = MEV ∗ i -MEV , and i achieves this by reporting truthfully (and winning).

## C.3 Proof of Theorem 3

Proof of Theorem 3. Fix an arbitrary arbitrageur i , its true belief v ∗ i , the reports q -i of all other arbitrageurs, and their Sybil transactions S -i . To prove the truthfulness, we only need to focus on the case where arbitrageur i submits no Sybil transaction, i.e., S i = ∅ . The bundle generation process shows that the final bundle is composed of | M | + 1 sub-bundles, corresponding to | M | pending transactions (for transactions that failed to be executed, the sub-bundle is empty) and the initial state. Denote the sub-bundle constructed for transaction TX j ∈ M and initial state s 0 by SB ( TX j ) and SB ( s 0 ), respectively. Then we can rewrite arbitrageur i 's utility defined in Equation (1) by traversing each sub-bundle and calculating the profit from it as follows:

<!-- formula-not-decoded -->

̸

Consider the scenario where arbitrageur i misreports by setting q i = v ∗ i . For each element e ∈ M ∪ { s 0 } , there are three cases to discuss regarding the winner of its sub-bundle.

Case 1: Arbitrageur i is the winner when reporting truthfully, but not when misreporting. In this case, arbitrageur i 's profit from the sub-bundle constructed when reporting truthfully is the loss of misreporting, which we will show is non-negative. The element e under discussion is either a pending transaction TX j or the initial state s 0 . If the former, arbitrageur i 's profit from this sub-bundle is

̸

<!-- formula-not-decoded -->

̸

which is non-negative. This is because the fact that arbitrageur i is the winner when reporting truthfully implies that ∆ x j · v ∗ i +∆ y j ≥ max k = i V k ( TX j ).

If the latter, the sub-bundle only contains a rebalancing arbitrage transaction from ( x 0 , y 0 ) to the state ( x ∗ , y ∗ ) corresponding to v ∗ i (i.e., y ∗ /x ∗ = v ∗ i ), from which arbitrageur i 's profit is

̸

<!-- formula-not-decoded -->

̸

̸

which is also non-negative as ϕ i ( s 0 ) ≥ max k = i ϕ k ( s 0 ).

̸

Case 2: Arbitrageur i is not the winner when reporting truthfully, but wins when misreporting. In this case, the profit from the sub-bundle is the gain of misreporting, which we will show is negative. If the sub-bundle corresponds to a transaction TX j , the profit is still ∆ x j · v ∗ i + ∆ y j -max k = i V k ( TX j ), which becomes negative in this case, as arbitrageur i loses when reporting truthfully.

If the sub-bundle corresponds to s 0 , the profit becomes

<!-- formula-not-decoded -->

̸

where (ˆ x i , ˆ y i ) corresponding to q i (i.e., ˆ y i / ˆ x i = q i ). We will show that h (ˆ x i , ˆ y i ) is upper bounded by h ( x ∗ , y ∗ ) which is negative in this case. Note that the value of the first and third terms in Equation (12) are fixed regardless of arbitrageur i 's report. Then it's sufficient to prove ˆ x i · v ∗ i +ˆ y i is minimized when (ˆ x i , ˆ y i ) = ( x ∗ i , y ∗ i ) where y ∗ i /x ∗ i = v ∗ i . Note that

<!-- formula-not-decoded -->

By the assumption that ∣ ∣ ∣ ∂F/∂x ∂F/∂y ∣ ∣ ∣ is decreasing with respect to x (see section 3), we have ˆ y i -y ∗ i x ∗ i -ˆ x i &gt; v ∗ i when ˆ x i &lt; x ∗ i , and y ∗ i -ˆ y i ˆ x i -x ∗ i &lt; v ∗ i when ˆ x i &gt; x ∗ i . Both cases imply that (ˆ x i -x ∗ i ) · v ∗ i +(ˆ y i -y ∗ i ) &gt; 0 if (ˆ x i , ˆ y i ) = ( x ∗ i , y ∗ i ), and ˆ x i · v ∗ i + ˆ y i reaches its minimum value when (ˆ x i , ˆ y i ) = ( x ∗ i , y ∗ i ).

̸

̸

Case 3: Arbitrageur i is the winner whether reporting truthfully or misreporting. In this case, we will show that after misreporting, the profit from the sub-bundle is no greater than before. If the sub-bundle corresponds to a transaction TX j , the profit for both scenarios is the same, which is ∆ x j · v ∗ i +∆ y j -max k = i V k ( TX j ). If the sub-bundle corresponds to s 0 , the profit after misreporting decreases because according to the analysis in Case 2, h (ˆ x i , ˆ y i ) &lt; h ( x ∗ , y ∗ ) when (ˆ x i , ˆ y i ) = ( x ∗ i , y ∗ i ).

̸

To sum up, arbitrageur i 's best strategy is to report truthfully by setting q i = v ∗ i , namely,

<!-- formula-not-decoded -->

This concludes the proof.

## C.4 Proof of Theorem 4

̸

Proof of Theorem 4. Fix an arbitrary arbitrageur i and the reports q of all arbitrageurs. Whether a transaction TX j ∈ M can be included in the bundle and thus executed only depends on max k ∈ [ n ] ∆ x j · q k +∆ y j , where (∆ x j , ∆ y j ) is determined by TX j itself (see Equation (4)). Suppose the maximal value is ∆ ϕ w achieved by arbitrageur w ∈ [ n ]. If ∆ ϕ w ≥ 0, TX j will be deterministically executed at its limit state, causing a deterministic change in the user's account balance, and receive a refund max k = w max { 0 , ∆ x j · q k +∆ y j } . As a result, the number of tokens that the user of TX j owns after executing through our mechanism is only determined by the transaction itself and q , which are fixed and independent of arbitrageur i 's strategy S i . This concludes the proof.

## C.5 Proof of Theorem 5

Proof of Theorem 5. Our proof strategy below follows from two steps: We first give a comprehensive analysis of arbitrageur i 's profit with arbitrary strategy given everyone's belief v ∗ i . The analysis will provide the intuition of our definition of the Sybil strategy. We then formally define the Sybil strategy S i ( v ∗ i , b X i , b Y i , D ) and show that ( v ∗ i , S i ( v ∗ i , b X i , b Y i , D )) is a best strategy of arbitrageur i when everyone else follows this strategy and their belief v ∗ k is drawn from D k .

̸

̸

Given an arbitrary arbitrageur i 's strategy ( q i , S ′ i ), i 's utility u ( S ′ i , q i ; S -i , v ∗ -i ) can be calculated by enumerating all sub-bundles in the output bundle of our mechanism. Our analysis and proof will be based on analyzing the profit of two different groups of the sub-bundles.

First step. Fix an arbitrageur i , its true belief v ∗ i , its budget ( b X i , b Y i ), and the strategies of all other arbitrageurs { ( v ∗ k , S k ( v ∗ k , b X k , b Y k , D )) } k = i . Here let's say S k ( v ∗ k , b X k , b Y k , D ) is some abstract Sybil strategy and it doesn't affect the analysis in the first step. We use S k as a shortening of S k ( v ∗ k , b X k , b Y k , D ) for every k ∈ [ n ] for simplicity of notations.

The proof of Theorem 3 implies that for every sub-bundle for which the middle transaction e ∈ R ∪ S -i ∪ { s 0 } , we have the profit from reporting q i is no more than the profit from reporting v ∗ i . Thus, we will be mainly focusing on the arbitrageur i 's profit of the sub-bundle of every e ∈ S ′ i when i reports q i .

̸

<!-- formula-not-decoded -->

̸

Let's consider any e ∈ S ′ i such that e = TX = ( X → Y , δ in X , δ out Y ). The other case will be similar. Note that if TX is sandwiched by i itself (which means q i ≥ max k = i { v ∗ k } ), then the profit of i is 0; if TX is sandwiched by someone else, denoted by w , then arbitrageur i 's utility from this sub-bundle is

̸

To analyze the profit formula above, note that H ( · , · ) is an increasing function of both parameters. However, there are also two upper bounds of these parameters based on the fact that this sub-bundle is won and sandwiched by w = i :

- w is the winner of all arbitrageur, which means q i ≤ v ∗ w ;
- the profit of w is no less than 0, which means δ out Y ≤ δ in X · v ∗ w .

We need the further property of H ( · , · ), stated below:

Claim 1. For any t such that t ≤ v ∗ w , we have H ( t, δ in X · t ) = H ( q i , δ in X · t ) for all q i ≤ t .

Proof. Note that for the parameter regime that we are considering, we have δ in X · q i -δ in X · t ≤ 0. Thus

̸

<!-- formula-not-decoded -->

The claim above essentially says that, the arbitrageur i 's profit from its own Sybil transactions is the same for any report q i ≤ δ out Y /δ in X regardless how small it is. Note that the arbitrageur i also has the profit from users' transactions. Thus this provides a good intuition about what kind of Sybil strategy everyone is using could form a Nash equilibrium. We formalize it in the second step.

Second step. We first specify the Sybil strategy S i ( v ∗ i , b X i , b Y i , D ) for every arbitrageur i . Fix an arbitrageur i , it includes two Sybil transactions: TX = ( X → Y , δ in X = b X i , δ out Y = t ∗ Y ) and TX = ( Y → X , δ in Y = b Y i , δ out X = t ∗ X ). To specify the t ∗ Y above, we recall the profit function of i given q i and δ out Y as parameters:

̸

̸

<!-- formula-not-decoded -->

Importantly, note that in the definition of Γ() above, we should use b X i as the parameter of δ in X when we refer the H function of Equation (13).

Now we are ready to define t ∗ Y and t ∗ X can be defined similarly.

<!-- formula-not-decoded -->

Namely, we choose t ∗ Y that maximizes the expected profit of Sybil transactions given that i reports v ∗ i truthfully . Note that by Theorem 3, reporting truthfully can maximize arbitrageur i 's profit of transactions that are not i 's Sybil transactions. Thus, we only need to show that arbitrageur i 's profit of its Sybil transactions is maximized when i uses our specified strategy, comparing with arbitrary report q i and set of Sybil transactions S ′ i . We consider the case where S ′ i only contains one Sybil transaction of ( X → Y , δ in X = b X i , δ out Y ) (and only contains one Sybil transaction of ( Y → X , δ in Y = b Y i , δ out X )). This is without loss of generality because we can easily merge multiple Sybil transactions in the same direction. It is easy to see that δ out Y should be at least b X i · v ∗ i .

̸

It remains for us to show that E v ∗ -i ∼D -i [ Γ( v ∗ i , t ∗ Y , v ∗ -i ) i ] ≥ E v ∗ -i ∼D -i [ Γ( q i , δ out Y , v ∗ -i ) i ] . The proof will be purely based on the properties of the H function. Recall that H is increasing for both parameters and Γ is non-zero only if q i ≤ max k = i { v ∗ k } and δ out Y ≤ b X i · max k = i { v ∗ k } . Letting α = max( q i , δ out Y /b X i ), we have that

<!-- formula-not-decoded -->

Furthermore, by Claim 1, we know that

<!-- formula-not-decoded -->

Finally, by the definition of t ∗ Y , we conclude

<!-- formula-not-decoded -->

The optimal choice of t ∗ X and its analysis is analogous. This concludes the proof.

## D Implementation Considerations

Below, we outline the architecture and workflow of a TEE-based implementation. We assume TEEs achieve confidentiality and integrity; in practice, one must carefully deal with side-channel attacks.

## D.1 Overview

Figure 8 illustrates the architecture of RediSwap . As shown, there are four main entities: users, arbitrageurs, a TEE, and a smart contract.

- Users are traders who use RediSwap for asset swaps. They submit transactions to the TEE, specifying the swap direction, the maximum input amount, and the minimum output amount.
- Arbitrageurs are a combination of MEV searchers, market makers, and/or other participants seeking non-atomic arbitrage opportunities. Arbitrageurs must grant the RediSwap smart contract permission to manage a portion of their token holdings in advance. They provide a signed message to the TEE indicating their belief in the external price of the risk asset.

̸

Figure 8: Overview of the RediSwap architecture and workflow. Users and arbitrageurs privately submit transactions and reports to the TEE, where the MEV-redistribution mechanism operates. Once the registration phase ends (as determined by the parameter ∆), the TEE executes the MEVredistribution process, constructs a bundle containing the swap, payment, and refund details, and then sends it publicly to trigger on-chain operations by invoking smart contracts.

<!-- image -->

- TEE processes submissions from users and arbitrageurs, running the MEV-redistribution mechanism to form bundles that include token swaps (i.e., outcome of the bundle generation rule) and transfers (for payments and refunds). The bundle is forwarded to the RediSwap smart contract for execution.
- RediSwap smart contract executes the bundle from the TEE by interacting with the transfer and swap functions to move tokens among users, arbitrageurs, and the CFMM pool.

## D.2 Workflow

We now elaborate on the workflow in Figure 9. RediSwap operates in slots, each with a duration T consistent with the block time (e.g., T = 12 s on Ethereum). Each slot consists of two stages: the registration stage and the execution stage. During the first registration stage, users and arbitrageurs submit their signed messages to the TEE, indicating their desire to participate. During the second execution stage, the TEE processes these messages, executes the MEV-redistribution mechanism, constructs the bundle accordingly, and invokes the smart contract to complete on-chain operations. The detailed steps of the protocol execution are as follows:

- (1a) A user P j prepares a transaction TX j , specifying the swap direction ( X → Y or Y → X ), a maximum input amount δ in , and a minimum output amount δ out . The user signs the order with their private key sk P j , producing the signature σ P j := Sig ( sk P j , TX j ). The user then sends a message, ('order' , ( TX j , σ P j )), to the TEE as described in Lines 1-4 of Prot RediSwap .
- (1b) An arbitrageur A i provides a report q i on the external price of the risky asset X . Like users, the arbitrageur signs the report with their private key sk A i , generating a signature σ A i := Sig ( sk A i , q i ). The arbitrageur sends the signed message, ('arbitrage' , ( q i , σ A i )), to the TEE, as specified in Lines 5-8.
- (2) Upon receiving the messages from users and arbitrageurs, the TEE maintains two lists: M for pending orders and q for arbitrage reports. When the protocol-defined time ∆ ( &lt; T ) is reached, the registration stage ends. The TEE then executes the MEV-redistribution mechanism based on the pool's initial state s 0 , pending transactions M , and the arbitrageurs'

```
Prot RediSwap (∆ , pool ) 1 : Users P j : 2 : TX j = (direction, δ in , δ out ) // swap 3 : σ P j := Sig ( sk P j , TX j ) 4 : send ('order' , ( TX j , σ P j )) to TEE 5 : Arbitrageurs A i : 6 : q i = A i 's report on the external price 7 : σ A i := Sig ( sk A i , q i ) 8 : send ('arbitrage' , ( q i , σ A i )) to TEE 9 : TEE : 10 : s 0 ← pool 's initial state 11 : Initialize M = [ ] // pending transactions 12 : Initialize q = [ ] // arbitrageurs in waiting 13 : On receive ('order' , ( TX j , σ P j )): 14 : M = M ∪ TX j 15 : On receive ('arbitrage' , ( q i , σ A i )): 16 : q = q ∪ q i 22 : TEE (Cont'd): 23 : On time (∆): 24 : // execute the MEV-redistribution mechanism 25 : bundle ← Algorithm 2 ( s 0 , M, q ) 26 : for i ∈ [ | M | +1] // payment and refund rules 27 : A w i ← winner , amount ←A w i 's payment 28 : to ← owner of TX i or pool 's address 29 : TX w i = (token, amount, to) // transfer 30 : bundle .append( TX w i ) 31 : call RediSwap .settle ( bundle ) 32 : RediSwap Smart Contract : 33 : settle ( info ): 34 : for TX ∈ bundle 35 : if TX .type = swap then 36 : call pool.swap(direction, δ in , δ out ) 37 : else 38 : call token.transfer(token, amount, to)
```

Figure 9: RediSwap Protocol.

reports q . It starts by applying Algorithm 2 (the bundle generation rule) to produce an MEV bundle. Next, the TEE implements the payment and refund rules. For each MEV opportunity from a pending transaction TX i or the initial state s 0 , the TEE constructs a transfer transaction from the winner A w i to the owner of TX i or the pool (i.e., LPs), and adds it to the bundle. The whole process is indicated in Lines 9-30.

- (3) The TEE sends the final bundle to the RediSwap smart contract and calls the settle() function. This function parses the bundle and proceeds each transaction sequentially: for trades, it invokes the pool's swap() function; for token transfers, it calls the transfer() function. This completes the settlement phase, ensuring all token transfers and trades are executed on-chain.