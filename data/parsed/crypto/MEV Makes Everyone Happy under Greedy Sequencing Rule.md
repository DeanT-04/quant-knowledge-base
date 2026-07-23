## MEV Makes Everyone Happy under Greedy Sequencing Rule

Yuhao Li ∗ Columbia University yuhaoli@cs.columbia.edu Mengqian Zhang ∗ New York University mengqian.zhang@stern.nyu.edu

Elynn Chen New York University elynn.chen@stern.nyu.edu Jichen Li ∗ Peking University limo923@pku.edu.cn Xi Chen New York University xc13@stern.nyu.edu

## Abstract

Trading through decentralized exchanges (DEXs) has become crucial in today's blockchain ecosystem, enabling users to swap tokens efficiently and automatically. However, the capacity of miners to strategically order transactions has led to exploitative practices ( e.g. , front-running attacks, sandwich attacks) and gain substantial Maximal Extractable Value (MEV) for their own advantage. To mitigate such manipulation, Ferreira and Parkes recently proposed a greedy sequencing rule such that the execution price of transactions in a block moves back and forth around the starting price. Utilizing this sequencing rule makes it impossible for miners to conduct sandwich attacks, consequently mitigating the MEV problem.

However, no sequencing rule can prevent miners from obtaining risk-free profits. This paper systemically studies the computation of a miner's optimal strategy for maximizing MEV under the greedy sequencing rule, where the utility of miners is measured by the overall value of their token holdings. Our results unveil a dichotomy between the no trading fee scenario, which can be optimally strategized in polynomial time, and the scenario with a constant fraction of trading fee, where finding the optimal strategy is proven NP-hard. The latter represents a significant challenge for miners seeking optimal MEV.

Following the computation results, we further show a remarkable phenomenon: Miner's optimal MEV also benefits users. Precisely, in the scenarios without trading fees, when miners adopt the optimal strategy given by our algorithm, all users' transactions will be executed, and each user will receive equivalent or surpass profits compared to their expectations. This outcome provides further support for the study and design of sequencing rules in decentralized exchanges.

Keywords: Decentralized Finance, Maximal Extractable Value, Sequencing Rule

∗ Equal contribution.

Xiaotie Deng Peking University xiaotie@pku.edu.cn

## 1 Introduction

Decentralized finance (also known as DeFi), as the main application of blockchain and smart contracts, has grown incredibly popular and attracted more than 40 billion dollars [1]. Within the DeFi ecosystem, decentralized exchange (DEX) becomes a fundamental service that allows users to trade cryptocurrency directly without any centralized authority. Nowadays, the daily volume of these DEXs has reached billions of US dollars [2].

Most DEXs ( e.g. , Uniswap, SushiSwap, Curve Finance, and Balancer) are organized as constant function market makers (CFMMs). Uniswap [3], for example, utilizes a constant product formula to make sure that the product of the quantity of two tokens remains constant before and after a swap. The exchange rate, or say the price that the swap executes at, is automatically determined by the reserves of the pair. So the outcome of each trade is sensitively influenced by system status at execution time.

In the blockchain, it is the block builders (also referred to as miners or validators) that select pending transactions and specify their execution order. This gives an exploitable chance for miners to extract profit by strategically including, excluding, and reordering transactions in a block. This is known as Maximal Extractable Value (MEV) [4]. A prevalent MEV example is the sandwich attack [5] on DEX transactions: the attacker 'sandwiches' a profitable victim transaction by frontrunning and back-running it and earns from the spread between buying and selling prices.

To mitigate this market manipulation by miners, Ferreira and Parkes [6] recently introduced a greedy sequencing rule . Simply put, when dealing with a bunch of transactions from the liquidity pool of tokens X and Y , this sequencing rule requires miners to take the starting price as a benchmark. Then at any point during the execution in the block, if the current price of Y is higher than the benchmark, the priority should be given to the transactions selling token Y . Conversely, the transactions selling token X should be executed next. This sequencing rule structurally makes the sandwich attack impossible. It restricts miners from manipulating transaction orders, thus mitigating the impact of MEV. More importantly, it introduces verifiability by allowing users to efficiently verify whether the execution order of transactions complies with the rule.

## 1.1 Our Contributions

As mentioned in [6], miners can always obtain risk-free profits in some cases under arbitrary sequencing rule. In this paper, we systematically study the computation of miner's optimal MEV strategy under the greedy sequencing rule. The study is based on the utility model where the worth of miners is the overall value of all their tokens. Like the similar work [7] aiming to maximize extractable value without rules or limits, the value of a token is measured by its price, which is exogenous, given by an oracle, and fixed throughout the attack. It was explicitly emphasized by Ferreira and Parkes [6] to also consider miner's utility as a real-valued function when studying sequencing rules. The monetary function we considered is arguably the most natural choice.

We highlight our results on the computation of miners' optimal strategies, as well as their surprising consequences. We give a computation dichotomy, supported by our two main theorems (Theorem 1 and Theorem 3). For the scenario where there is no trading fee, a polynomial time algorithm for a miner to compute an optimal strategy is given (Theorem 1); In contrast, when the fraction of trading fees is any constant larger than 0 ( e.g. , f = 0 . 3% in most Uniswap pools), we prove it is NP-hard to find an optimal strategy (Theorem 3).

The computational intractability implies hardness for a miner to hope for optimal MEV. More surprisingly, in the f = 0 regime, when miners adopt the optimal strategy provided by our algorithm

(Algorithm 1), users will also benefit in the following sense: all users' transactions will be executed (Corollary 1), and every user gets at least as good as if their transaction was the only transaction in the block (Corollary 2). The latter was one of the main motivations to propose the greedy sequencing rule, even though it is generally not true when the miner truthfully follows the greedy sequencing rule.

We conclude this paper by discussing many interesting future directions and open problems in the last section (Section 5).

## 1.2 Related Work

## 1.2.1 Sequencing Rules

Typically, miners organize transactions based on their gas prices. In order to protect users from order manipulation, Kelkar et al. [8] investigate the notion of fair transaction ordering for Byzantine consensus, which is further extended to the permissionless setting in [9]. Cachin et al. [10] introduce a new differential order-fairness property and present the quick order-fair atomic broadcast protocol which is much more efficient than previous solutions. The general idea of these approaches is to rely on a committee rather than a single miner to order transactions. A main threat to fair transaction ordering is the Condorcet attack [11]. Vafadar and Khabbazian [11] show that an attacker can undermine fairness by imposing Condorcet cycles even when all others in the system behave honestly.

Another category is content-oblivious ordering [12, 13] which guarantees that the transaction data is not accessible to the committee responsible for sequencing them until an order has been determined. This could be achieved using methods like threshold public key encryption schemes.

## 1.2.2 MEV Mitigation

It has long been discovered that miners could exploit transaction ordering for their own benefit [14]. The term Maximal Extractable Value (MEV) was introduced in [4], formally defined in [15], and its growth has resulted in network congestion and high gas prices [4, 16]. Besides the sequencing rules, some other approaches are also explored to mitigate the impact of MEV. To avoid sandwich attacks, users are suggested to reduce the trading volume by splitting transactions [17] and to restrict the slippage tolerance [18]. This method, however, may also increase the transaction costs for users. Zhou et al. [19] propose a new DEX design called A 2 MM, which helps users to immediately execute an arbitrage following their swap transactions. It also allows users to benefit from MEV atomically. Another popular way is to rely on the service from trusted third parties like flashbots [20], Eden [21], and OpenMEV [22]. Then can help to order transactions without broadcasting them to the whole network, thus protecting from front-running and sandwich attacks.

## 2 Preliminaries

## 2.1 Constant Function Market Makers

Let A be an AMM for trading between token X and token Y . The exchange has state s = ( x, y ), where x and y are current reserves of token X and Y , respectively. When A is a CFMM, the trading invariant can be modeled by a constant function with two variables F ( x, y ) = C . We will focus on CFMMs that satisfy Axiom 1 and Axiom 2, which are defined as follows. We note that all currently known CFMMs are consistent with these two properties. 1

Axiom 1. For different pairs ( x, y ) and ( x ′ , y ′ ) such that F ( x, y ) = F ( x ′ , y ′ ) = C , we have x &lt; x ′ if and only if y &gt; y ′ .

By this axiom, we know that for any x (reserves of token X ), there is a unique y such that F ( x, y ) = C and vice versa. So we will use F y ( x ) to denote the y such that F ( x, y ) = C and similarly define F x ( y ).

Axiom 2. F y ( x ) is differentiable and the marginal exchange rate | dF y ( x ) /dx | is decreasing with respect to x .

In the rest of the paper, we use r ( x ) to denote the marginal exchange rate of swapping tokens X for Y , i.e. , r ( x ) := | dF y ( x ) /dx | .

## 2.2 Execution of Transactions

Users can submit a transaction of the following two types: Sell ( X , · ) and Sell ( Y , · ), where · is a real parameter representing how many units of token the user wants to trade.

To be more concrete, suppose that the current state of CFMM A is s = ( x, y ). For each swap, part of tokens are charged as fees and we use f ∈ [0 , 1) to denote the fraction of this trading fee. When executing a transaction Sell ( X , q ), the user will pay q units of token X and get y -F y ( x +(1 -f ) q ) units of token Y . Similarly, when executing a transaction Sell ( Y , q ), the user will pay q units of token Y and get x -F x ( y +(1 -f ) q ) units of token X .

The executing of multiple transactions { TX i } i ∈ [ n ] will be well-defined if an order among them is determined. In particular, suppose that τ : [ n ] → [ n ] is a permutation. Then the execution will work as follows: Let s 0 = ( x 0 , y 0 ) be the initial state and iteratively execute each transaction TX τ ( i ) . For the i -th iteration, if TX τ ( i ) = Sell ( X , q ), then s i = ( x i , y i ) where x i = x i -1 + (1 -f ) q and y i = F y ( x i ); if TX τ ( i ) = Sell ( Y , q ), then s i = ( x i , y i ) where y i = y i -1 +(1 -f ) q and x i = F x ( y i ).

It is easy to see the order under which the transactions are executed crucially influences the trades outcomes. However, due to the same reason, it is also well-known that the decentralized exchange systems suffer from order manipulation , where an anonymous miner can manipulate the context of a block, even including inserting their own attacking transactions. Ferreira and Parkes [6] considered the notion of verifiable sequencing rules and proposed a greedy sequencing rule to limit miners' ability to manipulate (therefore in general it also benefits users). We recap their definitions below.

## 2.3 Sequencing Rules

We start with the definition of the verifiable sequencing rule.

Definition 1 (Verifiable sequencing rule, [6]) . A sequencing rule R is a map from initial state s 0 and a set of transactions { TX i } i ∈ [ n ] to a set of permutations { τ : [ n ] → [ n ] } , where each permutation is a valid order to execute these transactions under this sequencing rule.

A sequencing rule is efficiently computable , if there is a polynomial time algorithm that can compute a permutation τ : [ n ] → [ n ] that satisfies R (i.e., τ ∈ R ( s 0 , { TX i } i ∈ [ n ] ) ) for any initial state s 0 and transactions { TX i } i ∈ [ n ] .

1 This also includes Uniswap v3, which is less trivial.

A sequencing rule is efficiently verifiable , if there is a polynomial time algorithm such that for any permutation τ : [ n ] → [ n ] , the algorithm accepts τ if and only if τ ∈ R ( s 0 , { TX i } i ∈ [ n ] ) .

Along this way, Ferreira and Parkes [6] proposed a greedy sequencing rule (we use GSR to denote it), which is efficiently computable and verifiable.

Definition 2 (Greedy sequencing rule, [6]) . A permutation τ satisfies the greedy sequencing rule ( τ ∈ GSR ( s 0 , { TX i } i ∈ [ n ] ) ) if the following conditions hold for all i ∈ [ n ] :

- TX τ ( i ) is a Sell ( X , · ) transaction only if either x i -1 ≤ x 0 or TX τ ( j ) is Sell ( X , · ) for all i &lt; j ≤ n ; and
- TX τ ( i ) is a Sell ( Y , · ) transaction only if either y i -1 ≤ y 0 or TX τ ( j ) is Sell ( Y , · ) for all i &lt; j ≤ n ,

where s i -1 = ( x i -1 , y i -1 ) is the state before executing TX τ ( i ) .

Besides efficiency, the greedy sequencing rule enjoys the property that for every transaction, either its receive is as good as it was the only transaction in the block or it does not suffer from a sandwich attack.

However, it is totally possible for a miner to gain profits by manipulating the content of the block, even if it follows some given sequencing rule (e.g., the greedy sequencing rule). In the rest of the paper, we study the computation of miners' optimal strategies.

## 3 Miner's Strategy Space

We define the miner's strategy space in the most general way. To make the profits of the miner comparable, we assume that there are exogenous prices of X (denoted by p x ) and Y (denoted by p y ) and the miner wants to collect as much money as possible. Like previous work [7], p x and p y are assumed to remain the same during the attack (usually the timeslot for a block, e.g. , about 12 seconds in Ethereum).

Definition 3 (Strategy Space) . Given a sequencing rule R , an initial state s 0 = ( x 0 , y 0 ) , and a set of users' transactions { TX i } i ∈ [ n ] , a miner could create m number of its own transactions { TX i } i ∈ [ n +1: n + m ] , select a subset of all these n + m transactions S ⊆ [ n + m ] , compute an order τ ∈ R ( s 0 , { TX i } i ∈ S ) (here instead of permutation, τ should be a one-to-one mapping from [ | S | ] to S ) that satisfies the sequencing rule, and execute them under the order τ .

The miner's profit U ( { TX i } i ∈ [ n +1: n + m ] , S, τ ) is defined as

where f ∈ [0 , 1) is the fraction of trading fees.

<!-- formula-not-decoded -->

Here, ✶ { x i &gt;x i -1 } indicates that TX τ ( i ) is a Sell ( X , · ) transaction and ✶ { y i &gt;y i -1 } indicates that TX τ ( i ) is a Sell ( Y , · ) transaction. These two events will not happen simultaneously.

## 3.1 Arbitrage-Free Interval

In this subsection, we present a clean lemma that characterizes (what we call) arbitrage-free interval, which provides the first intuition behind the proofs later. It may also serve as the first step in other scenarios of decentralized exchanges when concerning the miner's strategies, e.g. , optimal sandwich attacks of a miner who wants to collect money.

Before we state and prove the lemma, we first introduce a notation, which is also used in the subsequent sections. We use L x to denote the x such that the marginal exchange rate r ( L x ) = 1 1 -f p x p y and R x to denote the x such that r ( R x ) = (1 -f ) p x p y .

Lemma 1. Given the exogenous prices p x and p y , and the current state s ∗ = ( x ∗ , y ∗ ) , miner's optimal profit is positive if and only if x ∗ ̸∈ [ L x , R x ] . Furthermore, when x ∗ &lt; L x , miner's optimal strategy is to execute Sell ( X , ( L x -x ∗ ) / (1 -f )) ; when x ∗ &gt; R x , miner's optimal strategy is to execute Sell ( Y , ( F y ( R x ) -y ∗ ) / (1 -f )) .

Proof. We first argue that it suffices for the miner to execute at most one transaction. This is because if miner executes two transactions with the same type (say Sell ( X , q 1 ) and Sell ( X , q 2 )), then it is equivalent to execute Sell ( X , q 1 + q 2 ); if miner executes two transactions with different types (say Sell ( X , q 1 ) and Sell ( Y , q 2 )), then it is better to replace them by one single transaction since miner can avoid additional cost of trading fees.

So next we consider the case where the miner executes one of its transactions TX . Suppose that TX = Sell ( X , q ), then miner's profit is

<!-- formula-not-decoded -->

We show below that when x ∗ ≥ L x , U ( X , q ) ≤ 0 for all q ≥ 0.

<!-- formula-not-decoded -->

Symmetrically we can define U ( Y , q ) when miner executes Sell ( Y , q ) and conclude that when x ∗ ≤ R x , U ( Y , q ) ≤ 0 for all q ≥ 0. This finishes the proof that when x ∗ ∈ [ L x , R x ], miners cannot obtain positive profits.

Then we consider what is an optimal attack when x ∗ ̸∈ [ L x , R x ]. Suppose that x ∗ &lt; L x , then by previous argument, the miner should not execute Sell ( Y , · ) (as x ∗ &lt; L x ≤ R x ). So let's focus on the case where the miner executes Sell ( X , q ).

Letting x ′ = x ∗ +(1 -f ) q , note that

<!-- formula-not-decoded -->

where ( ∫ L x x ∗ r ( x ) dx ) · p y -( L x -x ∗ ) / (1 -f ) · p x is the profits that miner can get by executing Sell ( X , ( L x -x ∗ ) / (1 -f )) as states in the lemma. Next we show that

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

which is a decreasing function as r ( x ′ ) is decreasing. Since g ′ ( L x ) = 0, we have the maximal value of g is at L x , which is 0.

This finishes the proof.

## 4 Strategies under Greedy Sequencing Rule

In this section, we systemically analyze the strategic behaviors of the miners who follow the greedy sequencing rule.

̸

We specifically focus on the case that the initial state s 0 = ( x 0 , y 0 ) satisfies r ( x 0 ) = p x /p y . Note that this is without loss of generality in our context: On the one hand, when f = 0, L x = R x ( i.e. , the arbitrage-free interval becomes an arbitrage-free point). Supported by Lemma 1, if the current X reserves are not L x ( R x ), anyone can make money by a single arbitrage transaction, namely, by selling X or Y to reach the arbitrage-free point. Thus, it is reasonable to think the last transaction ends up with the state s 0 = ( x 0 , y 0 ) satisfying r ( x 0 ) = p x /p y , which is also the initial state of this attack; On the other hand, when f &gt; 0, we show that the NP-hardness holds even if r ( x 0 ) = p x /p y , let alone the more general case. It is still interesting to consider the case r ( x 0 ) = p x /p y , and we discuss it in the last section (Section 5).

In Section 4.2, we show a polynomial time algorithm to compute an optimal attack in the regime that the fraction of trading fee f = 0. Interestingly, it will also benefit the users if the miner follows such a strategy compared to truthfully following the greedy sequencing rule.

In contrast, Section 4.3 shows that when the fraction of trading fee f is any constant larger than 0 (say f = 0 . 3% as being used in most Uniswap pools), it is NP-hard to find an optimal strategy.

## 4.1 Upper Bounds of Optimal Profits

Our main results in this section (Theorem 1 and Theorem 3) will be crucially based on the following lemma, which provides an upper bound of miner's optimal profit (using arbitrary strategy) under the greedy sequencing rule.

Before presenting the lemma, we first define the arbitragable profit for one transaction, inspired by Lemma 1.

Definition 4 (Arbitragable Profit) . Given an initial state s 0 = ( x 0 , y 0 ) and a user's transaction TX , we define the arbitragable profit AP ( s 0 , TX ) as follows:

<!-- formula-not-decoded -->

for all x ′ .

Note that

So we have

Figure 1: Illustration of Arbitrage-Free Interval and the intuition behind Arbitragable Profit.

<!-- image -->

- If TX = Sell ( Y , q ) , let x ′ = min { F x ( y 0 +(1 -f ) q ) , L x } . Then AP ( s 0 , TX ) := ( F y ( x ′ ) -F y ( L x )) · p y -( L x -x ′ ) / (1 -f ) · p x .

Figure 1 illustrates the intuition behind Arbitragable Profit.

The lemma below shows that the miner's optimal profit is upper-bounded by the sum arbitragable profits of all users' transactions.

Lemma 2. Given an initial state s 0 = ( x 0 , y 0 ) with r ( x 0 ) = p x /p y , a set of users' transactions { TX i } i ∈ [ n ] , the miner's profit (using arbitrary strategy) under the greedy sequencing rule is upper bounded by M ( s 0 , { TX i } i ∈ [ n ] ) , where

<!-- formula-not-decoded -->

Proof. Fix arbitrary sequence of (users' and miner's) transactions ( TX τ (1) , · · · , TX τ ( k ) ), where TX τ ( i ) is a user's transaction if τ ( i ) ∈ [ n ] and it is the miner's transaction otherwise. Let s i = ( x i , y i ) be the state after executing TX τ ( i ) . Without loss of generality, we assume that TX τ ( i ) = Sell ( X , · ) if and only if x i -1 ≤ x 0 and TX τ ( i ) = Sell ( Y , · ) if and only if y i -1 ≤ y 0 for all i ∈ { 2 , · · · , k } . To see it, suppose that for k ′ &lt; k we have TX τ ( i ) = Sell ( X , · ) and x i -1 &gt; x 0 for all i ∈ { k ′ +1 , · · · , k } . Then by Lemma 1, we know that miner's profit obtained from TX τ ( k ′ +1) , · · · TX τ ( k ) is at most 0 (and possibly negative). It means the miner can always choose not to execute these transactions and the profit is as good as before.

We will inductively show that after executing the first i transactions, the miner's profit U i ≤ V i := ∑ j ∈ [ i ] ,τ ( j ) ∈ [ n ] AP ( s 0 , TX τ ( j ) ). This will imply that after executing all k transactions, miner's profit is upper bounded by ∑ i ∈ [ n ] AP ( s 0 , TX i ).

We define ϕ i as follows:

<!-- formula-not-decoded -->

We will show that ( U i + ϕ i ) -( U i -1 + ϕ i -1 ) ≤ V i -V i -1 = AP ( s 0 , TX τ ( i ) ) for all i ∈ [ k ], which will imply our desired statement U i ≤ V i as ϕ i ≥ 0 for all i ∈ [ k ]. (Here we define AP ( s 0 , TX τ ( i ) ) = 0 if it is a miner's transaction.)

The basis of the induction is trivial as U 0 + ϕ 0 = 0. For the induction step, let's consider arbitrary i ∈ [ k ].

Case 1: TX τ ( i ) is a user's transaction. Then we have U i = U i -1 . So it suffices for us to show ϕ i -ϕ i -1 ≤ AP ( s 0 , TX τ ( i ) ). Suppose that TX τ ( i ) = Sell ( X , q ). Then it must be the case x i -1 &lt; = x 0 due to the greedy sequencing rule. (The other case TX τ ( i ) = Sell ( Y , q ) will be symmetric.) If x i ≤ x 0 , then we have that ϕ in fact didn't increase, which means ϕ i -ϕ i -1 ≤ 0 ≤ AP ( s 0 , TX τ ( i ) ). If x i &gt; x 0 , then since x i -1 ≤ x 0 , we have x i ≤ max { x 0 +(1 -f ) q, R x } . So that ϕ i ≤ AP ( s 0 , TX τ ( i ) ), concluding the first case.

Case 2: TX τ ( i ) is a miner's transaction. Then we have V i = V i -1 . So it suffices for us to show U i -U i -1 + ϕ i -ϕ i -1 ≤ 0. Suppose that TX τ ( i ) = Sell ( X , q ), then it must be the case x i -1 &lt; = x 0 due to the greedy sequencing rule. (Again, the other case TX τ ( i ) = Sell ( Y , q ) will be symmetric.)

<!-- formula-not-decoded -->

Now, let's consider the case L x ≤ x i . To simplify the analysis, we consider an intermediate state s ′ with U ′ and ϕ ′ . If x i -1 ≥ L x , then we just set s ′ = s i -1 with U ′ = U i -1 and ϕ ′ = ϕ i -1 . If x i -1 &lt; L x , we split TX τ ( i ) into two transactions: TX ′ = Sell ( X , ( L x -x i -1 ) / (1 -f )) and TX ′′ = Sell ( X , ( x i -L x ) / (1 -f )), and we define s ′ , U ′ and ϕ ′ as that after executing TX ′ .

Note that we have U ′ -U i -1 = ϕ i -1 -ϕ ′ . So we only need to show U i -U ′ ≤ ϕ ′ -ϕ i . Note that in fact ϕ ′ = 0.

If x i ≤ R x , then ϕ i = ϕ ′ = 0. In addition, by Lemma 1, we know that U i -U ′ ≤ 0. So we conclude U i -U ′ ≤ ϕ ′ -ϕ i as desired.

The last possibility is that x i &gt; R x , where we have

<!-- formula-not-decoded -->

Moreover, by Lemma 1, we know that U i -U ′ ≤ ( R x -x i ) / (1 -f ) · p x +( F y ( R x ) -F y ( x i )) · p y &lt; -ϕ i . This finishes the proof.

## 4.2 Polynomial Time Algorithm When f = 0

In this subsection, we show a polynomial time algorithm to find an optimal strategy for the miner when f = 0. Interestingly, when adopting our algorithm, users will also benefit in the following sense: all users' transactions will be executed ( a.k.a they will be included in the block), and every user gets at least as good as if their transaction was the only one in the block. The latter is generally not true if the miner truthfully follows the greedy sequencing rule.

Theorem 1. When the fraction of trading fee f = 0 , Algorithm 1 finds an optimal strategy under the greedy sequencing rule in polynomial time, and the optimal profit is equal to the upper bound M ( s 0 , { TX i } i ∈ [ n ] ) .

Remark 1. Before going into details of the proof, we note that our algorithm can obtain the optimal profit M ( s 0 , { TX i } i ∈ [ n ] ) under arbitrary order of users' transactions { TX i } i ∈ [ n ] . So it still works even if there are some constraints on the execution order of certain transactions (e.g., a user may create two transactions { TX 1 , TX 2 } and specify that TX 1 must be executed before TX 2 ).

## Algorithm 1: Algorithm for optimal strategy when f = 0

```
Input: An initial state s 0 = ( x 0 , y 0 ), and a set of users' transactions { TX i } i ∈ [ n ] . Output: An optimal strategy for miner to obtain M ( s 0 , { TX i } i ∈ [ n ] ) profits, which is the best possible. 1 Sort these n transactions in any order τ : [ n ] → [ n ]. 2 for each i from 1 to n do 3 Execute user's transaction TX τ ( i ) . 4 if TX τ ( i ) = Sell ( X , q ) then 5 Execute a transaction Sell ( Y , y 0 -F y ( x 0 + q )). 6 if TX τ ( i ) = Sell ( Y , q ) then 7 Execute a transaction Sell ( X , x 0 -F x ( y 0 + q )).
```

Proof of Theorem 1. We first show that the sequence given by Algorithm 1 satisfies the greedy sequencing rule. Note that after executing each user's transaction TX τ ( i ) , we always execute a miner's transaction with the opposite direction, shown between line 4 and 7. Besides, at the end of i -th iteration, we have the state s 2 i = s 0 (we use 2 i because we execute two transactions in each iteration). So our sequence satisfies the greedy sequencing rule. Furthermore, during the i -th iteration, we obtain exactly AP ( s 0 , TX τ ( i ) ) profits by executing the transaction on line 5 or 7. Then the optimality follows from the same upper bound provided by Lemma 2.

Now we turn to the positive effects on users when a miner launches an optimal strategy given by Algorithm 1. We summarize them as the following two corollaries and omit the proofs as they are relatively straightforward from the proof of Theorem 1.

Corollary 1. When a miner launches an optimal strategy given by Algorithm 1, all users' transactions { TX i } i ∈ [ n ] will be executed.

Corollary 2. When a miner launches an optimal strategy given by Algorithm 1, each user's profit is as good as if their transaction was the only transaction in the block.

As shown in Theorem 1, Corollary 1, Corollary 2, both miner and users are satisfied when miner adopts our Algorithm 1.

## 4.3 NP-hardness When f &gt; 0

In this subsection, we show the computational hardness of finding an optimal strategy when the fraction of trading fees is any constant larger than 0 (say f = 0 . 3%).

We will mainly focus on the proof of the NP-completeness of the following decision problem, then Theorem 3 will follow directly.

Theorem 2. Let f ∈ (0 , 1) be any universal constant. It is NP-complete to decide if there is a strategy that can obtain profits M ( s 0 , { TX i } i ∈ [ n ] ) for any initial state s 0 = ( x 0 , y 0 ) and users' transactions { TX i } i ∈ [ n ] .

Proof. The NP-membership is easy. Given any strategy, we can efficiently simulate the execution of the sequence of transactions and check if the final profit is M ( s 0 , { TX i } i ∈ [ n ] ) or not.

For the NP-hardness, we reduce the Partition problem to our problem. Recall that the instance of the partition problem contains n positive integers and ask if it can be partitioned into two subsets S 1 and S 2 such that the sum of numbers in S 1 equals that in S 2 .

Suppose we are given arbitrary n positive integers { a 1 , · · · , a n } . Let t be half of the sum of these integers, i.e. , 1 2 ∑ n i =1 a i . Without loss of generality, we assume that a i ≤ t for all i ∈ [ n ] otherwise the answer to the decision problem will directly be 'no'.

We first construct a CFMM A and initial state s 0 . Concretely, we can consider the constant curve of A as F ( x, y ) : xy = k , and our goal is to choose parameters such that x 0 -L x = (1 -f ) t . Precisely, we know that L x = √ 1 -fx 0 , since r ( L x ) = 1 1 -f r ( x 0 ). This means x 0 -L x = (1 -√ 1 -f ) x 0 . So choosing x 0 = 1 -f 1 - √ 1 -f t would suffice.

Next, we construct users' transactions. For each integer a i , we construct TX i = Sell ( X , a i ). Clearly, we have AP ( s 0 , TX i ) = 0 as (1 -f ) a i ≤ (1 -f ) t = x 0 -L x ≤ R x -x 0 . Then we construct two Sell ( Y , · ) transactions. Precisely, we construct TX n +1 = TX n +2 = Sell ( Y , q ∗ ) where q ∗ is large enough such that F x ( y 0 + (1 -f ) q ∗ ) &lt; L x . Then we know AP ( s 0 , TX n +1 ) = AP ( s 0 , TX n +2 ) &gt; 0. This finishes the construction. And we know M ( s 0 , { TX i } i ∈ [ n +2] ) = 2 AP ( s 0 , TX n +1 ).

Finally, we argue that there exists a strategy obtaining profits M ( s 0 , { TX i } i ∈ [ n +2] ) if and only if there exists a subset S ⊆ [ n ] such that the sum of the numbers in S equal t . And this will conclude the theorem.

One direction is easy: if there exists S ⊆ [ n ] such that the sum of the numbers in S equal t , then we execute transactions as follows:

1. Execute user's transaction TX n +1 ; Execute miner's transaction Sell ( X , L x -F x ( y 0 +(1 -f ) q ∗ ) 1 -f );
2. Execute TX i for all i ∈ S ;
3. Repeat item (1) except replacing TX n +1 by TX n +2 .

It is easy to verify that this sequence satisfies the greedy sequencing rule, and the miner can obtain M ( s 0 , { TX i } i ∈ [ n +2] ).

For the other direction, we show that the sequence of transactions constructed above is essentially the only way to obtain M ( s 0 , { TX i } i ∈ [ n +2] ). So a miner can obtain M ( s 0 , { TX i } i ∈ [ n +2] ) only if the answer to the given Partition problem is 'yes'.

We adopt a proof scheme similar to that of Lemma 2. Fix a sequence of (users' and miner's) transactions ( TX τ (1) , · · · , TX τ ( k ) ) such that miner's profit U = 2 AP ( s 0 , TX n +1 ). Recall that in the proof of Lemma 2, we defined ϕ i and showed U i + ϕ i -( U i -1 + ϕ i -1 ) ≤ AP ( s 0 , TX i ) for all i ∈ [ k ]. Since U k = 2 AP ( s 0 , TX n +1 ) at the end, it must be the case U i + ϕ i = V i for all i ∈ [ k ] and ϕ k = 0. As a result, the sequence of transactions must satisfy that

- The miner does not lose profit for any transaction; otherwise the loss of the profit is strictly larger than the gain of the ϕ function, and this will result in U i + ϕ i &lt; V i for some i .

̸

- There are i 1 = i 2 ∈ [ k ] such that ϕ i 1 = ϕ i 2 = AP ( s 0 , TX n +1 ). This means when execute TX n +1 and TX n +2 , the corresponding state must be ( x 0 , y 0 ).

To achieve both items simultaneously, it must be ( x i 1 -1 , y i 1 -1 ) = ( x 0 , y 0 ) and TX n +1 is executed as TX τ ( i 1 ) . To get the first AP ( s 0 , TX n +1 ) profit, miner executes Sell ( X , L x -F x ( y 0 +(1 -f ) q ∗ ) 1 -f ) in the ( i 1 +1)-th iteration. To make sure that ( x i 2 -1 , y i 2 -1 ) = ( x 0 , y 0 ) (and TX n +2 is executed as TX τ ( i 2 ) ) while the miner does not loss any profit in this process, we must use users' transactions to change the state from x i 1 = L x to x i 2 -1 = x 0 , which means we need a subset S of users' transactions such that the sum of numbers in S is exactly t .

This finishes the proof.

Theorem 3 follows directly by simulating any algorithm that computes an optimal strategy and calculates the profits to solve the decision problem.

Theorem 3. Let f ∈ (0 , 1) be any universal constant. It is NP-hard to compute the strategy that can obtain the optimal profits.

## 5 Discussion and Open Problems

Refined Sequencing Rule. Our first question is related to mechanism design, motivated by a revisit of our polynomial time algorithm when f = 0. Recall that our algorithm can always obtain the upper bound profits, even if the miner is asked to follow the greedy sequencing rule such that the sequence is additionally under a descending order. Thus, we would like to ask if there is some sequencing rule (that is computationally efficient and verifiable) that can further mitigate the miner's incentive to manipulate. We propose the following way to build a theoretical foundation when considering real-world applications. We could consider the case where users' transactions are drawn from a certain distribution D (witnessed by real-world DeFi scenarios), and show that under the refined greedy sequencing rule, miners cannot obtain large profits with high probability. We leave it as a promising open question.

̸

Approximation Algorithm for Miners. It is also worth to study about approximation algorithm design for miners. Our NP-hardness rules out the possibility for a miner to have a polynomial time algorithm for an optimal strategy (assuming P =NP). However, it remains possible to design a polynomial time algorithm with a good approximation guarantee. This strategy exploration allows miners to develop efficient algorithms that can yield sufficient MEV close to the optimal strategy. As the optimal MEV problem shares a similar spirit with the Knapsack problem, one promising direction is to apply the classic approximation algorithms to our setting.

User's Strategies. The third question is about strategic analysis from the perspective of users. In this work, we systematically studied the optimal strategies of miners. We also note that there is fruitful space for a user to adopt strategies. For example, a user who wants to sell a large amount of X tokens may have an incentive to split it into several smaller transactions, and this may lead them to a higher profit under the greedy sequencing rule. Generally speaking, we wonder what is an optimal strategy for a user under certain sequencing rules. Different from the miner's incentive, multiple users are making decisions simultaneously, which forms a multi-agent system. One step further than one user's optimization, we ask what the equilibrium is when all users behave strategically. The game theory problem between users and miners under specific sequencing rules is also an intriguing question.

Other Scenarios where MEV Makes Everyone Happy. Finally, recall our exciting journey about the positive effects of MEV: when a miner attracts MEV (optimally), users are also benefited in a reasonable sense (Corollary 1 and Corollary 2). The intuition behind this phenomenon is that although the existence of MEV incentivizes miners to engage in attacking behaviors when a good sequencing rule can restrict miners' actions and prevent them from affecting users' profits, the presence of MEV itself can benefit users. In this case, MEV not only does not harm users but can expedite the execution of user transactions as miners have the motivation to execute more transactions (to obtain MEV). We expect and are eager to know a wider range of scenarios where the same conceptual result also holds. We leave this as the most important future work.

## References

- [1] DeFiLlama, 'Defi overview,' August 1st 2023. [Online]. Available: https://defillama.com/
- [2] DeFiprime, 'Decentralized exchanges trading volume,' August 1st 2023. [Online]. Available: https://defiprime.com/dex-volume
- [3] H. Adams, N. Zinsmeister, M. Salem, R. Keefer, and D. Robinson, 'Uniswap v3 core,' Tech. rep., Uniswap, Tech. Rep. , 2021. [Online]. Available: https://uniswap.org/whitepaper-v3.pdf
- [4] P. Daian, S. Goldfeder, T. Kell, Y. Li, X. Zhao, I. Bentov, L. Breidenbach, and A. Juels, 'Flash boys 2.0: Frontrunning in decentralized exchanges, miner extractable value, and consensus instability,' in 2020 IEEE Symposium on Security and Privacy, SP 2020, San Francisco, CA, USA, May 18-21, 2020 . IEEE, 2020, pp. 910-927. [Online]. Available: https://doi.org/10.1109/SP40000.2020.00040
- [5] L. Zhou, K. Qin, C. F. Torres, D. V. Le, and A. Gervais, 'High-frequency trading on decentralized on-chain exchanges,' in 42nd IEEE Symposium on Security and Privacy, SP 2021, San Francisco, CA, USA, 24-27 May 2021 . IEEE, 2021, pp. 428-445. [Online]. Available: https://doi.org/10.1109/SP40001.2021.00027
- [6] M. V. X. Ferreira and D. C. Parkes, 'Credible decentralized exchange design via verifiable sequencing rules,' in Proceedings of the 55th Annual ACM Symposium on Theory of Computing, STOC 2023, Orlando, FL, USA, June 20-23, 2023 , B. Saha and R. A. Servedio, Eds. ACM, 2023, pp. 723-736. [Online]. Available: https://doi.org/10.1145/3564246.3585233
- [7] M. Bartoletti, J. H. Chiang, and A. Lluch-Lafuente, 'Maximizing extractable value from automated market makers,' in Financial Cryptography and Data Security - 26th International Conference, FC 2022, Grenada, May 2-6, 2022, Revised Selected Papers , ser. Lecture Notes in Computer Science, I. Eyal and J. A. Garay, Eds., vol. 13411. Springer, 2022, pp. 3-19. [Online]. Available: https://doi.org/10.1007/978-3-031-18283-9 1
- [8] M. Kelkar, F. Zhang, S. Goldfeder, and A. Juels, 'Order-fairness for byzantine consensus,' in Advances in Cryptology -CRYPTO 2020 -40th Annual International Cryptology Conference, CRYPTO 2020, Santa Barbara, CA, USA, August 17-21, 2020, Proceedings, Part III , ser. Lecture Notes in Computer Science, D. Micciancio and T. Ristenpart, Eds., vol. 12172. Springer, 2020, pp. 451-480. [Online]. Available: https://doi.org/10.1007/978-3-030-56877-1 16
- [9] M. Kelkar, S. Deb, and S. Kannan, 'Order-fair consensus in the permissionless setting,' in APKC '22: Proceedings of the 9th ACM on ASIA Public-Key Cryptography Workshop, APKC@AsiaCCS 2022, Nagasaki, Japan, 30 May 2022 , J. P. Cruz and N. Yanai, Eds. ACM, 2022, pp. 3-14. [Online]. Available: https://doi.org/10.1145/3494105.3526239
- [10] C. Cachin, J. Micic, N. Steinhauer, and L. Zanolini, 'Quick order fairness,' in Financial Cryptography and Data Security - 26th International Conference, FC 2022, Grenada, May

2-6, 2022, Revised Selected Papers , ser. Lecture Notes in Computer Science, I. Eyal and J. A. Garay, Eds., vol. 13411. Springer, 2022, pp. 316-333. [Online]. Available: https://doi.org/10.1007/978-3-031-18283-9 15

- [11] M. A. Vafadar and M. Khabbazian, 'Condorcet attack against fair transaction ordering,' CoRR , vol. abs/2306.15743, 2023. [Online]. Available: https://doi.org/10.48550/arXiv.2306. 15743
- [12] D. Malkhi and P. Szalachowski, 'Maximal extractable value (MEV) protection on a DAG,' in 4th International Conference on Blockchain Economics, Security and Protocols, Tokenomics 2022, December 12-13, 2022, Paris, France , ser. OASIcs, Y. Amoussou-Guenou, A. Kiayias, and M. Verdier, Eds., vol. 110. Schloss Dagstuhl - Leibniz-Zentrum f¨ ur Informatik, 2022, pp. 6:1-6:17. [Online]. Available: https://doi.org/10.4230/OASIcs.Tokenomics.2022.6
- [13] Sikka, August 1st 2023. [Online]. Available: https://sikka.tech/projects/
- [14] S. Eskandari, S. Moosavi, and J. Clark, 'Sok: Transparent dishonesty: Front-running attacks on blockchain,' in Financial Cryptography and Data Security - FC 2019 International Workshops, VOTING and WTSC, St. Kitts, St. Kitts and Nevis, February 18-22, 2019, Revised Selected Papers , ser. Lecture Notes in Computer Science, A. Bracciali, J. Clark, F. Pintore, P. B. Rønne, and M. Sala, Eds., vol. 11599. Springer, 2019, pp. 170-189. [Online]. Available: https://doi.org/10.1007/978-3-030-43725-1 13
- [15] K. Babel, P. Daian, M. Kelkar, and A. Juels, 'Clockwork finance: Automated analysis of economic security in smart contracts,' in 44th IEEE Symposium on Security and Privacy, SP 2023, San Francisco, CA, USA, May 21-25, 2023 . IEEE, 2023, pp. 2499-2516. [Online]. Available: https://doi.org/10.1109/SP46215.2023.10179346
- [16] K. Kulkarni, T. Diamandis, and T. Chitra, 'Towards a theory of maximal extractable value I: constant function market makers,' CoRR , vol. abs/2207.11835, 2022. [Online]. Available: https://doi.org/10.48550/arXiv.2207.11835
- [17] P. Z¨ ust, T. Nadahalli, and Y. W. R. Wattenhofer, 'Analyzing and preventing sandwich attacks in ethereum,' ETH Z¨ urich , 2021. [Online]. Available: https: //pub.tik.ee.ethz.ch/students/2021-FS/BA-2021-07.pdf
- [18] L. Heimbach and R. Wattenhofer, 'Eliminating sandwich attacks with the help of game theory,' in ASIA CCS '22: ACM Asia Conference on Computer and Communications Security, Nagasaki, Japan, 30 May 2022 - 3 June 2022 , Y. Suga, K. Sakurai, X. Ding, and K. Sako, Eds. ACM, 2022, pp. 153-167. [Online]. Available: https://doi.org/10.1145/3488932.3517390
- [19] L. Zhou, K. Qin, and A. Gervais, 'A2MM: mitigating frontrunning, transaction reordering and consensus instability in decentralized exchanges,' CoRR , vol. abs/2106.07371, 2021. [Online]. Available: https://arxiv.org/abs/2106.07371
- [20] Flashbots, August 1st 2023. [Online]. Available: https://docs.flashbots.net/
- [21] Eden, August 1st 2023. [Online]. Available: https://www.edennetwork.io/
- [22] OpenMEV, August 1st 2023. [Online]. Available: https://openmev.xyz/