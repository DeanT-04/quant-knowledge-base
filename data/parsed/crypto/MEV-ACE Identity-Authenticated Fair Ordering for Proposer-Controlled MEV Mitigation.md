## MEV-ACE: Identity-Authenticated Fair Ordering for Proposer-Controlled MEV Mitigation

Jian Sheng Wang ACE Labs jason@acechain.io

April 8, 2026

## Abstract

Maximal Extractable Value (MEV) remains a structural threat to blockchain fairness because the block producer can often observe pending transactions and unilaterally decide their ordering or inclusion. Existing mitigations hide transaction contents or outsource ordering, but they typically leave two gaps unresolved: commitments are not authenticated by slashable identities, and inclusion obligations are not backed by transferable evidence that other validators can verify.

This paper presents MEV-ACE , a fair-ordering protocol for proposer-controlled ordering MEV . MEV-ACE combines three mechanisms: (1) registered economic identities , whose authentication keys are deterministically derived from the ACEGF framework and bonded on-chain; (2) authenticated commit/open messages with validator receipt thresholds , which make admissibility and inclusion obligations independently auditable; and (3) verifiable-delay randomness , which determines transaction order only after the admissible commitment set is fixed.

We formalize the protocol in a 3 f +1 validator model with threshold receipts and show three properties under standard assumptions: order-unpredictability once the admissible set is locked, commitment authenticity under EUF-CMA security of the authentication signature scheme, and accountable inclusion for transactions that obtain threshold commit and open receipts. Under these conditions, and when producer/user bonds exceed the one-slot gain from invalid execution or selective non-opening, MEV-ACE removes unilateral proposer discretion over front-running, sandwiching, and censorship against admitted transactions. The protocol remains single-slot in structure, requires no threshold decryption committee, and is compatible with post-quantum signatures such as ML-DSA-44.

Keywords: MEV, fair ordering, front-running resistance, blockchain, ACE-GF, VDF, identity-bound commitment

## 1 Introduction

Maximal Extractable Value (MEV) refers to the profit a block producer can extract by manipulating the ordering, inclusion, or censorship of transactions within a block [2]. Large-scale empirical studies and measurement efforts have documented substantial extracted value on Ethereum and related DeFi ecosystems [3, 4], imposing a regressive tax on ordinary users while concentrating profit among sophisticated searchers and cooperating validators.

The MEV problem is structural: in conventional blockchains, the block producer observes pending transactions in cleartext and has unilateral discretion over their ordering. This asymmetry enables three canonical attack classes:

- Front-running : The producer inserts a transaction before a target transaction to capture a price movement.
- Sandwich attacks : The producer brackets a target transaction with a buy-before and sell-after pair, extracting the slippage.
- Censorship : The producer selectively excludes transactions to disadvantage specific users or benefit competing transactions.

We collectively term these ordering-based MEV , distinguished from information-based MEV (e.g., cross-domain arbitrage from public oracle updates) which does not depend on the producer's ordering power.

## 1.1 Limitations of Existing Approaches

Prior work has pursued four main strategies, each with fundamental limitations:

Commit-reveal schemes [5]. Users hide transaction contents during an initial commitment phase and reveal later. This reduces early information leakage, but by itself does not authenticate who is allowed to create admissible commitments, nor does it provide a portable proof that an omitted commitment had to be included.

Threshold encryption [6]. Transactions are encrypted under a threshold key and decrypted only after ordering is fixed. This requires a trusted decryption committee, introduces at least one full round-trip of latency for threshold decryption, and remains vulnerable to producer-committee collusion.

Fair-ordering services [7]. Decentralized oracles provide ordering attestations. These introduce an external trust assumption and oracle-layer latency, and they shift, rather than remove, the requirement that some outside party honestly witness and enforce ordering.

Proposer-builder separation (PBS) [8]. Separates block building from block proposing. This redistributes MEV rather than eliminating it: the builder still extracts orderingbased MEV, and the proposer receives a share via auction.

## 1.2 The Authenticated-Admissibility Gap

We identify a structural weakness shared by these approaches: the protocol does not natively authenticate admissible commitments by registered, slashable identities, nor does it require inclusion evidence that can be verified by any validator . This enables the following attacks:

1. Commitment stuffing : The producer generates many low-cost commitments to dilute the ordering pool and improve the expected placement of its own trades.
2. Selective non-opening : The producer admits many candidate transactions and reveals only the subset whose realized positions are profitable.
3. Unprovable omission : Honest users may have broadcast valid commitments or openings, but other validators lack a transferable proof that the producer was obligated to include them.

These attacks are especially problematic in systems where identity creation is cheap, commitment admission is not authenticated, and omission can only be detected by local observation rather than by globally verifiable receipts.

## 1.3 Our Contributions

This paper makes the following contributions:

1. Formal model of admissible fair ordering. We define proposer-controlled ordering MEV in a model where commitments and openings become mandatory only after they collect threshold validator receipts, and formalize three security properties: order-unpredictability, commitment authenticity, and accountable inclusion (Section 3).
2. The MEV-ACE protocol. We present a single-slot protocol that combines ACEGF-derived authentication keys, bonded identity registration, threshold receipt certificates for commit/open phases, and VDF-based delayed randomness (Section 4).
3. Security analysis. We prove that MEV-ACE satisfies all three properties under the sequentiality of the VDF, EUF-CMA security of the authentication signature scheme, collision resistance of SHA-256, and standard BFT delivery assumptions for omission proofs. We further derive explicit economic conditions under which honest execution is the producer's best response (Section 5).
4. Deployment guidance. We provide a parameterized latency and communication analysis that makes the timing assumptions explicit, instead of conflating VDF security parameters with wall-clock runtime (Section 6).
5. Identity-authenticated ordering architecture. We show how ACE-GF can be used as an identity-native key-derivation layer for MEV protection without requiring seed storage or threshold decryption, while keeping the actual security boundary at the protocol layer: registered keys, bonded participation, and independently verifiable receipts.

## 1.4 Scope and Non-Goals

MEV-ACE targets proposer-controlled ordering MEV on a single chain. Informationbased MEV-such as back-running public oracle price updates or cross-domain statistical arbitrage-is not in scope. These forms of MEV exploit publicly available information and do not disappear merely because proposer ordering discretion is reduced; they require orthogonal mitigations such as batch auctions, delayed disclosure, or private execution.

## 2 Preliminaries

## 2.1 ACE-GF Identity Framework

ACE-GF (Atomic Cryptographic Entity Generative Framework) [1] is a deterministic key-derivation framework that derives application-specific cryptographic material from an identity root called the Root Entropy Value ( REV ). For MEV-ACE, the relevant properties are:

- Deterministic derivation. Application keys are derived under explicit context strings, allowing the protocol to dedicate a distinct authentication key to MEV ordering without reusing keys from unrelated applications.
- Context isolation. Keys derived under distinct contexts are computationally independent under the pseudorandomness of the underlying KDF.
- Operational simplicity. Honest users manage one identity root while still obtaining application-specific signing keys, which lowers operational overhead without weakening protocol-level accountability.
- Post-quantum compatibility. ACE-GF can instantiate its authentication context with ML-DSA-44 (NIST FIPS 204), allowing the ordering protocol to inherit post-quantum signature support.

Definition 1 (MEV Authentication Key) . For a user with identity root REV , let

<!-- formula-not-decoded -->

denote the signature key pair derived for MEV-ACE authentication.

Definition 2 (Registered Identity Commitment) . For a user with authentication verification key vk auth , the public identity commitment used by MEV-ACE is

<!-- formula-not-decoded -->

where H is SHA-256. A registered economic identity is the on-chain tuple ( idcom , vk auth , D stake ) , where D stake is a slashable bond locked for protocol participation.

Remark 1. In MEV-ACE, protocol-level Sybil resistance does not rely on local wallet setup cost. The enforceable cost comes from the registered bond D stake , the per-slot commitment quota ℓ , and slashing for invalid behavior or selective non-opening. ACE-GF is used to make authenticated key derivation convenient and context-isolated, not to serve as the sole anti-Sybil mechanism.

## 2.2 Verifiable Delay Functions

AVerifiable Delay Function (VDF) [10] is a function f : X → Y that requires T sequential computation steps to evaluate but whose output can be verified in O (log T ) time.

Definition 3 (VDF) . A VDF scheme consists of three algorithms:

- Setup (1 λ , T ) → pp : generates public parameters for security parameter λ and delay parameter T .

- Eval ( pp , x ) → ( y, π ) : computes output y with proof π in exactly T sequential steps.
- Verify ( pp , x, y, π ) →{ 0 , 1 } : verifies the output in O (log T ) time.

We require the sequential computation assumption : no adversary with poly ( λ ) parallel processors can evaluate the VDF significantly faster than T sequential steps.

## 2.3 Notation

Throughout this paper: H ( · ) denotes SHA-256; ∥ denotes concatenation; [ n ] denotes the set { 1 , . . . , n } ; λ is the security parameter; negl ( λ ) denotes a negligible function in λ ; π σ denotes a permutation derived from seed σ ; R C i and R O i denote threshold receipt bundles for the commit and open phases, respectively.

## 3 Formal Model

## 3.1 System Model

We consider a blockchain with the following participants:

- Users U = { u 1 , . . . , u n } : each user u i controls a registered identity ( idcom i , vk auth i , D stake ) and submits transactions.
- Block producer P : the entity responsible for assembling the current block. P may be strategic, rational, or Byzantine, and may also control a subset of registered user identities.
- Validators V = { v 1 , . . . , v 3 f +1 } : validators verify signatures, issue commit/open receipts, and reject blocks that omit transactions proven to be mandatory.

Time is divided into discrete slots . Each slot has a designated block producer selected by the consensus protocol. The block producer for slot s is denoted P s .

Acommitment or opening becomes mandatory only after it gathers a threshold receipt bundle from validators. We use q c and q o for the commit and open thresholds, respectively, and assume q c , q o ≥ 2 f +1 .

Definition 4 (Admissible Commitment) . A commitment for slot s is a tuple ( idcom i , c i , s, σ C i ) . It is admissible if:

1. ( idcom i , vk auth i , D stake ) is registered and active;
2. σ C i is a valid signature under vk auth i on message ( "commit" , idcom i , c i , s ) ;
3. the identity has not exceeded the per-slot quota ℓ ; and
4. the commitment carries a validator receipt bundle R C i containing at least q c valid validator signatures on the same message before the slot's commit cutoff.

Definition 5 (Executable Opening) . Let ( idcom i , c i , s, σ C i ) be an admissible commitment. An opening ( tx i , r i , idcom i , s ) is executable if:

1. c i = H ( tx i ∥ r i ∥ idcom i ∥ s ) ;

2. it carries an opening receipt bundle R O i with at least q o valid validator signatures on message ( "open" , idcom i , c i , s ) before the opening cutoff; and
3. the corresponding identity remains active and slashable.

## 3.2 Ordering-Based MEV: Formal Definition

Definition 6 (Transaction Ordering Function) . An ordering function Order maps a set of transactions T = { tx 1 , . . . , tx m } to a permutation σ ∈ S m determining their execution sequence within a block.

Definition 7 (Ordering-Based MEV) . Let σ ∗ denote the execution order chosen by a strategic producer P over the executable opening set of a slot, and let σ 0 denote the protocol-prescribed order. The ordering-based MEV extracted by P is:

<!-- formula-not-decoded -->

where Profit ( P , σ ) is the net economic gain to P from executing T in order σ , including any producer-controlled identities and side transactions.

## 3.3 Security Properties

We define three properties that collectively eliminate unilateral proposer discretion over admitted transactions:

Definition 8 (Order-Unpredictability) . A fair-ordering protocol satisfies order-unpredictability if, for any PPT adversary A controlling the block producer, the probability that A can predict the position of any target executable transaction tx i in the final ordering, given all information available before the admissible commitment set is locked, satisfies:

<!-- formula-not-decoded -->

where m is the number of executable openings in the slot.

Definition 9 (Commitment Authenticity) . A fair-ordering protocol satisfies commitment authenticity if, for any PPT adversary A , the probability that A produces an admissible commitment for a registered identity idcom ∗ without possessing the corresponding authentication signing key is:

<!-- formula-not-decoded -->

Definition 10 (Accountable Inclusion) . A fair-ordering protocol satisfies accountable inclusion if any transaction that has both an admissible commitment and an executable opening must appear in every valid finalized block for that slot, and any omission can be proven by a publicly verifiable omission proof derived from ( R C i , R O i ) .

Definition 11 (Elimination of Proposer-Controlled Ordering MEV) . A protocol eliminates proposer-controlled ordering MEV on admitted transactions if it simultaneously satisfies order-unpredictability, commitment authenticity, and accountable inclusion.

## 4 The MEV-ACE Protocol

MEV-ACE operates in four logical steps: Register , Commit , Order , and Open . Registration occurs off the slot critical path; the latter three phases execute within one slot.

## 4.1 Protocol Overview

The protocol combines three ideas:

1. Authenticated admissibility : a commitment is not merely a hash; it must be signed by a registered identity and acknowledged by a threshold of validators before it enters the admissible set.
2. Delayed randomness : the execution permutation is derived only after the admissible set is locked, removing the producer's ability to pick positions after learning transaction contents.
3. Receipt-backed inclusion : both commitments and openings carry portable receipt bundles, so omission can be proven to any validator rather than inferred only by local observation.

Together, these mechanisms constrain the producer in two dimensions: it cannot cheaply fabricate additional admissible demand, and it cannot silently omit a transaction that has already crossed the protocol's admission thresholds.

## 4.2 Registration

Before participating, user u i derives an authentication key pair

<!-- formula-not-decoded -->

computes idcom i = H ( vk auth i ) , and registers ( idcom i , vk auth i , D stake ) on-chain. Registration activates the identity only after the bond is locked, and the bond remains slashable for non-opening and invalid protocol behavior.

Each active identity may submit at most ℓ commitments per slot. This quota is protocol-enforced and is central to the anti-stuffing analysis in Section 5.3.

## 4.3 Phase 1: Commit

Each user u i wishing to include a transaction tx i in slot s performs:

1. Sample a fresh opening nonce r i .
2. Compute the commitment:

<!-- formula-not-decoded -->

3. Authenticate the commitment:

<!-- formula-not-decoded -->

4. Broadcast ( idcom i , c i , s, σ C i ) to validators.

A validator v j receiving the commitment verifies:

1. idcom i is registered and active;
2. σ C i verifies under the registered vk auth i ;
3. the identity has not exceeded the per-slot quota ℓ .

If all checks succeed, the validator signs a receipt

<!-- formula-not-decoded -->

Once the user or network aggregates q c such receipts, the commitment becomes admissible and carries certificate R C i .

## Algorithm 1 Commit Phase (User u i )

Require: Transaction tx i , slot number s , auth key sk auth i

Sample fresh nonce r i

c

i

C

H

(

tx

i

r

i

idcom

auth

i

s

)

σ i ← Sign ( sk i , ( "commit" Broadcast ( idcom i , c i , s, σ C i ) and collect R C i

,

idcom

i

, c

i

, s

))

The commit phase ends at cutoff ∆ c . Only commitments with valid receipt bundles R C i collected before this cutoff belong to the slot's admissible set.

## 4.4 Phase 2: Order

After the commitment cutoff, the producer constructs the admissible commitment set

<!-- formula-not-decoded -->

containing every commitment certificate valid for slot s . The set is canonicalized by sorting on ( idcom i , c i ) .

The ordering then proceeds as follows:

1. Compute the admissible-set root

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

to obtain ( seed s , π VDF ,s ) = VDF . Eval ( pp , x s ) .

3. Derive the execution permutation

<!-- formula-not-decoded -->

via a seeded Fisher-Yates shuffle over the m = |C ∗ s | admissible commitments.

4. Publish ( C s, root , seed s , π VDF ,s , σ s ) in the block proposal together with the certified admissible set.

←

∥

∥

∥

2. Evaluate the VDF on

## Algorithm 2 Order Phase (Block Producer)

```
Require: Certified admissible set C ∗ s , previous block hash h prev C s, root ← MerkleRoot ( Sort ( C ∗ s )) x s ← H ( h prev ∥C s, root ∥ s ) ( seed s , π VDF ,s ) ← VDF . Eval ( pp , x s ) σ s ← FisherYates ( seed s , |C ∗ s | ) Publish ( C s, root , seed s , π VDF ,s , σ s )
```

Why VDF, not a simple hash? If the seed were a plain hash of the admissible-set root, the producer could learn the final permutation immediately once the set is locked and then decide which of its own committed transactions to open. The VDF inserts a mandatory sequential delay between admissible-set lock and permutation availability, forcing commitment decisions to be made before the order is known.

## 4.5 Phase 3: Open

After the producer publishes the ordering material, users reveal transaction openings:

1. Broadcast ( tx i , r i , idcom i , s ) for each admissible commitment they wish to open.
2. Validators verify c i ? = H ( tx i ∥ r i ∥ idcom i ∥ s ) against the certified admissible commitment.
3. If valid, validators issue opening receipts

<!-- formula-not-decoded -->

and any opening with at least q o such receipts obtains certificate R O i .

4. The producer executes every transaction with a valid opening certificate in the order induced by σ s , skipping unopened commitments and applying the user-side non-opening penalty.

## Algorithm 3 Open Phase (User u i and Validators)

Require:

Opening ( tx i , r i , idcom i , s ) , certified commitment ( idcom i , c i , R C i )

User:

Broadcast ( tx i , r i , idcom i , s )

Validator:

Verify c i = H ( tx i ∥ r i ∥ idcom i ∥ s )

Validator:

Issue opening receipt and aggregate R O i

Producer:

Execute every certified opening in order σ s

Non-opening penalties. If an admissible commitment does not receive a valid opening certificate R O i before the opening cutoff, the corresponding identity is slashed by a fraction δ user of its bond for that unopened commitment. This makes selective non-opening an explicitly priced deviation rather than a free option.

Omission proofs. If a block omits an admissible commitment or an executable opening, any participant may present an omission proof consisting of the relevant certificate bundle(s): for commit omission, ( idcom i , c i , s, R C i ) ; for execution omission, ( idcom i , c i , s, R C i , tx i , r i , R O i ) . Validators verify these objects directly and reject the block if the omission proof is valid.

## 4.6 Timing and Slot Structure

Within a single slot of duration ∆ , the protocol allocates time to commitment admission, delayed randomness, and opening:

| Phase           | Duration          | Action                                         |
|-----------------|-------------------|------------------------------------------------|
| Commit          | [0 , ∆ c )        | Users broadcast commitments and collect R C i  |
| VDF computation | [∆ c , ∆ c +∆ v ) | Producer evaluates delayed randomness on C ∗ s |
| Open            | [∆ c +∆ v , ∆)    | Users reveal and collect R O i                 |

The timing constraint is

<!-- formula-not-decoded -->

where ∆ o denotes the minimum opening/verification budget and ∆ v must exceed the maximum lead by which a producer can know the final admissible-set root before commit cutoff. This separates the security requirement on delayed randomness from any one implementation's raw CPU benchmark.

Single-slot execution. Unlike multi-block commit-reveal constructions, MEV-ACE can complete all critical steps in one slot when the chain's slot budget is sized to accommodate ∆ c , ∆ v , and ∆ o . On faster chains, the same logic can be preserved by moving delayed randomness or receipt aggregation to a pipelined implementation.

## 5 Security Analysis

We analyze the three properties from Section 3 and then derive the producer's incentive constraints.

## 5.1 Order-Unpredictability

Theorem 1 (Order-Unpredictability) . Assume that: (i) the admissible commitment set C ∗ s is fixed before the VDF output seed s becomes available; (ii) the VDF satisfies the sequential computation assumption; and (iii) H is modeled as a random oracle. Then MEV-ACE satisfies order-unpredictability (Definition 8).

Proof. Let tx i be any executable transaction in slot s . The final execution permutation is

<!-- formula-not-decoded -->

By assumption, C s, root is not fixed until the admissible commitment set is locked, and seed s is unavailable before that lock. Hence any strategy that conditions commitment decisions on the realized position of tx i cannot use the actual final seed.

Once C ∗ s is fixed, the seed is derived from a random-oracle hash and a sequentially evaluated VDF output. Therefore, before seed s is released, A gains no non-negligible advantage over guessing the position of tx i in the Fisher-Yates permutation. The position is uniformly distributed over the m executable openings, so

<!-- formula-not-decoded -->

## 5.2 Commitment Authenticity

Theorem 2 (Commitment Authenticity) . Under EUF-CMA security of the authentication signature scheme and collision resistance of H , MEV-ACE satisfies commitment authenticity (Definition 9).

Proof. For a commitment to be admissible, validators must verify a valid signature

<!-- formula-not-decoded -->

under the registered verification key vk auth i whose hash equals idcom i . Therefore an adversary that produces an admissible commitment for identity idcom i without controlling sk auth i directly yields an EUF-CMA forgery against the signature scheme.

Collision resistance of H ensures that, after admission, the user cannot later open the same commitment to two distinct tuples ( tx i , r i ) and ( tx ′ i , r ′ i ) with the same idcom i and slot number. Thus the commitment is both authenticated at admission time and binding at opening time. The combined failure probability is negligible.

## 5.3 Sybil Resistance via Identity Cost

Lemma 1 (Bounded Stuffing Cost) . Let ℓ be the maximum number of commitments allowed per identity per slot. To inject k additional admissible commitments in a slot beyond its currently registered capacity, an adversary must control at least ⌈ k/ℓ ⌉ additional active identities and therefore lock at least ⌈ k/ℓ ⌉ · D stake of slashable capital.

Proof. By protocol rule, each active identity can contribute at most ℓ admissible commitments to a slot. Therefore k extra admissible commitments require at least ⌈ k/ℓ ⌉ extra identities. Each such identity must be registered with an active bond D stake , so the minimum additional slashable capital is ⌈ k/ℓ ⌉ · D stake .

Corollary 1. If u of those extra commitments are later left unopened, the adversary incurs additional slashing of at least u · δ user · D stake .

The key point is not that identity creation is impossible; it is that the protocol converts commitment stuffing from a nearly free deviation into a deviation that consumes additional bonded capacity and, under selective non-opening, incurs explicit slashing.

## 5.4 Accountable Inclusion

Theorem 3 (Accountable Inclusion) . Assume that: (i) q c , q o ≥ 2 f + 1 ; (ii) omission proofs based on ( R C i , R O i ) are delivered to honest validators before they finalize the slot; and (iii) the underlying BFT protocol has more than 2 / 3 honest stake. Then MEV-ACE satisfies accountable inclusion (Definition 10).

Proof. Let transaction tx i have an admissible commitment certificate R C i and an executable opening certificate R O i . Because both thresholds are at least 2 f +1 in a 3 f +1 validator set, each certificate includes signatures from at least f +1 honest validators.

Suppose the producer omits the commitment entirely. Then any observer can present ( idcom i , c i , s, R C i ) ; all validators can verify the certificate independently and conclude that the commitment belonged to the admissible set. A block whose admissible-set root excludes that commitment is invalid.

Suppose the producer includes the commitment but omits execution after a valid opening. Then any observer can present ( idcom i , c i , s, R C i , tx i , r i , R O i ) . Validators verify the commitment hash, the opening certificate, and the canonical position of the transaction under σ s . A block that does not execute this transaction is invalid.

Under the assumed BFT quorum and timely delivery of omission proofs, honest validators reject any invalid block. Therefore every transaction with both valid certificates appears in every finalized block for the slot.

## 5.5 Producer Incentives

Theorem 4 (Honest Execution as Producer Best Response) . Let B prod denote the producer bond. Suppose the following inequalities hold for every slot:

## 1. Invalid-block deviation bound:

<!-- formula-not-decoded -->

where G invalid is the maximum one-slot gain from reordering or omitting mandatory transactions.

## 2. Selective non-opening bound:

<!-- formula-not-decoded -->

where G open is the maximum gain from withholding one admissible producer-controlled opening after observing the realized order.

3. Stuffing-cost bound: for every k ≥ 1 ,

where G stuff ( k ) is the incremental expected gain from injecting k additional admissible commitments.

<!-- formula-not-decoded -->

Then, after the admissible commitment set is fixed, honest execution of the certified permutation is a best response for the producer.

Proof. Consider the producer's possible deviations.

Deviation 1: Reorder or omit mandatory transactions. By Theorem 3, omission proofs and deterministic recomputation of σ s make the block invalid. The producer loses at least δ prod B prod , which exceeds the gain cap G invalid by assumption.

Deviation 2: Publish a fake VDF output. VDF soundness makes successful forgery negligible, and an invalid VDF proof again triggers the invalid-block penalty. Expected gain is negative by the first inequality.

Deviation 3: Inject additional admissible commitments. By Lemma 1, k extra commitments require at least ⌈ k/ℓ ⌉ additional bonded identities. By the stuffingcost inequality, this capital requirement exceeds the incremental expected gain G stuff ( k ) .

Deviation 4: Selectively withhold producer-controlled openings. Each unopened admitted commitment loses at least δ user D stake , which by assumption exceeds the maximum gain G open from suppressing that opening.

Since every profitable deviation channel is closed either cryptographically or economically, honest execution is a best response for the producer once the admissible set is fixed.

## 5.6 Security Boundaries and Limitations

We explicitly acknowledge the following limitations:

- The guarantees apply only after receipt thresholds are met. If a user fails to collect R C i or R O i before the relevant cutoff, the transaction never becomes mandatory for that slot.
- Information-based and cross-domain MEV remain out of scope. Backrunning on public state changes and arbitrage across chains still require orthogonal mechanisms such as batch auctions or delayed disclosure [13].
- The protocol depends on timely dissemination of omission proofs. If valid omission proofs do not reach honest validators before they vote, accountable inclusion becomes weaker in practice even though the proof objects are sound.
- VDF hardware asymmetry remains a deployment risk. If one party can compute the VDF materially faster than the calibrated bound, delayed randomness may no longer provide the intended uncertainty window.
- Economic guarantees are parameter-sensitive. If D stake , δ user , or δ prod are set below realistic one-slot profit opportunities, selective non-opening or stuffing can become rational again.

## 6 Performance Analysis

The original version of this paper conflated cryptographic delay parameters, wall-clock runtime, and end-to-end slot overhead. We separate them here.

## 6.1 Computation and Communication Costs

Let m be the number of admissible commitments in a slot and n = 3 f +1 the validator count. MEV-ACE adds four main cost components:

- User-side work: each transaction adds one commitment hash, one opening nonce, and one authentication signature.
- Validator-side work: commit and open admission require O ( m ) signature/hash checks over the slot.
- Canonicalization: constructing the admissible-set root requires an O ( m log m ) sort and O ( m ) hashes.
- Delayed randomness: VDF evaluation is deployment-specific, while verification remains O (log T ) or better depending on the construction.

Communication overhead arises from two additional user messages per transaction (commit and open) plus validator receipt certificates. In practice, this means MEV-ACE is bandwidth-sensitive unless receipt signatures are batched, aggregated, or compressed in the execution layer.

## 6.2 Latency Budget

The slot budget should be reasoned about as

<!-- formula-not-decoded -->

where:

- ∆ c is the time for users to obtain commit certificates R C i ;
- ∆ v is the wall-clock delay introduced by the randomness mechanism;
- ∆ o is the time for users to obtain opening certificates R O i ;
- ∆ margin absorbs network jitter and consensus scheduling slack.

The key design rule is that ∆ v must exceed the producer's maximum timing advantage in learning the final admissible-set root. This is a security calibration , not a CPU microbenchmark. A deployment can therefore be single-slot only if its chain-level slot duration is large enough to hold all three phases with margin.

## 6.3 Throughput Implications

MEV-ACE does not impose a fixed percentage throughput penalty independent of deployment. Its throughput impact depends on three variables:

1. the validator count and signature scheme used for receipts;
2. whether receipt evidence is carried as individual signatures, aggregates, or committee certificates;

3. the chain's networking budget for doubling user-plane messages from one to two phases.

Consequently, a credible throughput claim requires an implementation benchmark with a concrete validator topology, signature scheme, aggregation strategy, and slot scheduler. This paper does not claim a universal 3-7 ms overhead or a fixed TPS number.

## 6.4 Qualitative Comparison

Relative to plain commit-reveal, MEV-ACE adds two capabilities that materially change the security boundary: authenticated admissibility and omission proofs. Relative to threshold-encryption systems, it avoids a decryption committee but still requires a carefully calibrated delay budget. Relative to PBS, it targets the source of ordering discretion rather than merely reallocating extracted value between builders and proposers.

## 7 Discussion

## 7.1 Why Identity Binding Is the Missing Piece

The core observation of this work is more precise than 'identity solves MEV.' What matters is authenticated admissibility backed by slashable economic identities . Fair ordering without authenticated admission still lets the producer manufacture demand; authenticated admission without delayed randomness still lets the producer condition reveals on realized order. MEV-ACE pairs these two controls and adds receipt-backed inclusion so omission becomes globally auditable.

## 7.2 Generalization Beyond ACE-GF

While MEV-ACE is presented in the context of ACE-GF, the design generalizes to any system that provides:

1. A registered verification key or equivalent public credential for protocol authentication.
2. A slashable participation bond or other enforceable cost for expanding identity capacity.
3. A way to dedicate protocol-specific signing material so that ordering authentication is isolated from other applications.

ACE-GF is attractive because it supplies item (3) cleanly and can instantiate the authentication key with post-quantum signatures. The security proofs in this paper, however, ultimately rely on registered keys, receipt thresholds, and bonded participation rather than on any ACE-GF-specific local wallet workflow.

## 7.3 Parameter Selection Guidelines

- Receipt thresholds q c , q o : Set to at least 2 f +1 so that every certificate contains signatures from at least f +1 honest validators and can therefore support omission proofs.

- Delay budget ∆ v : Choose ∆ v to exceed the producer's maximum timing advantage in learning the final admissible-set root, with additional margin for hardware asymmetry and network jitter.
- Stake deposit D stake : Size the user bond so that δ user D stake exceeds the maximum gain from withholding one admitted opening, and ⌈ k/ℓ ⌉ D stake exceeds the gain from stuffing k extra commitments.
- Producer bond B prod : Size the producer-side slash so that δ prod B prod exceeds the maximum one-slot benefit from invalid ordering or omission.
- Rate limit ℓ : Choose ℓ based on expected user activity. A larger ℓ improves UX for high-frequency users but weakens the capital cost of commitment stuffing.

## 8 Related Work

MEVtaxonomy and measurement. Daian et al. [2] introduced the concept of miner extractable value and documented front-running on Ethereum. Flashbots later published MEV-Explore as a practical measurement resource for extracted MEV [3]. Qin et al. [4] quantified extractable value across major DeFi activity classes. Together, this line of work shows that ordering-based MEV is a structural problem in blockchain systems where transaction ordering affects economic outcomes.

Commit-reveal and encryption-based approaches. Canidio and Danos [5] analyze commit-reveal schemes against front-running. Shutter Network [6] uses threshold encryption to hide transaction contents from sequencers. These approaches reduce early information leakage, but by themselves they do not authenticate admissible commitments via bonded identities or provide portable omission proofs.

Fair ordering services. Kelkar et al. [9] formalized order-fairness and proposed Aequitas. Chainlink Fair Sequencing Services (FSS) [7] decentralizes ordering via oracle networks. These require external trust assumptions that MEV-ACE avoids.

Proposer-builder separation. Flashbots MEV-Boost [8] separates block building from proposing in Ethereum. This is a redistribution mechanism (the builder still extracts MEV; the proposer receives a share), not an elimination mechanism.

VDF-based protocols. Boneh et al. [10] formalized VDFs. Wesolowski [11] provided efficient VDF constructions. MEV-ACE uses delayed randomness not as a standalone fairness primitive, but as one component in a larger admissibility-and-inclusion framework.

Identity and Sybil resistance. Proof-of-personhood protocols [12] address Sybil resistance through identity verification. ACE-GF [1] provides a cryptographic identity framework with context-isolated key derivation. MEV-ACE differs from both strands by using registered, slashable protocol identities to authenticate commitments and openings in the block-building path.

## 9 Conclusion

Wehave presented MEV-ACE, an identity-authenticated fair-ordering protocol for proposercontrolled MEV mitigation. The central claim is narrower and stronger than the original draft: once commitments and openings cross threshold receipt gates, the producer no longer retains unilateral discretion to reorder or omit them without either violating verifiable protocol rules or paying explicitly modeled economic penalties. This result follows from the combination of registered authentication keys, receipt-backed admissibility, delayed randomness, and slashable participation bonds.

The paper's security conclusion is therefore conditional rather than rhetorical. MEVACE provides order-unpredictability, commitment authenticity, and accountable inclusion under standard cryptographic assumptions, timely dissemination of omission proofs, and correctly sized economic parameters. ACE-GF remains useful as the deterministic identity/key-derivation substrate and preserves compatibility with post-quantum signatures such as ML-DSA-44, but the enforceable security boundary is the protocol itself.

Future work. The next three priorities are: (1) benchmarking concrete receipt and VDF implementations under realistic validator topologies; (2) formalizing omission-proof handling inside a full BFT state machine; and (3) studying how this framework composes with batch auctions or encrypted execution for information-based MEV.

## References

- [1] J. S. Wang, 'ACE-GF: A Generative Framework for Atomic Cryptographic Entities,' arXiv preprint arXiv:2511.20505v2 , 2026.
- [2] P. Daian, S. Goldfeder, T. Kell, et al., 'Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability,' in Proc. IEEE S&amp;P , 2020.
- [3] A. Obadia, 'Quantifying MEV-Introducing MEV-Explore v0,' The Flashbots Collective , Feb. 21, 2021. [Online]. Available: https://collective.flashbots.net/t/ quantifying-mev-introducing-mev-explore-v0/862
- [4] K. Qin, L. Zhou, and A. Gervais, 'Quantifying Blockchain Extractable Value: How dark is the forest?,' in Proc. IEEE S&amp;P , 2022.
- [5] A. Canidio and V. Danos, 'Commit-Reveal Schemes Against Front-Running Attacks (Extended Abstract),' in Proc. 4th Int. Conf. Blockchain Economics, Security and Protocols (Tokenomics 2022) , vol. 110 of OASIcs , 2022.
- [6] Shutter Network, 'Shutterized Beacon Chain,' Ethereum Research , Mar. 24, 2022. [Online]. Available: https://ethresear.ch/t/shutterized-beacon-chain/ 12249
- [7] A. Juels, L. Breidenbach, and F. Tramèr, 'Fair Sequencing Services: Enabling a Provably Fair DeFi Ecosystem,' Chainlink Blog , Sep. 11, 2020. [Online]. Available: https://blog.chain.link/ chainlink-fair-sequencing-services-enabling-a-provably-fair-defi-ecosystem/

- [8] Flashbots, 'MEV-Boost: Merge ready Flashbots Architecture,' Ethereum Research , Nov. 4, 2021. [Online]. Available: https://ethresear.ch/t/ mev-boost-merge-ready-flashbots-architecture/11177
- [9] M. Kelkar, F. Zhang, S. Goldfeder, and A. Juels, 'Order-Fairness for Byzantine Consensus,' in Proc. CRYPTO , 2020.
- [10] D. Boneh, J. Bonneau, B. Fisch, and B. Bünz, 'Verifiable Delay Functions,' in Proc. CRYPTO , 2018.
- [11] B. Wesolowski, 'Efficient Verifiable Delay Functions,' in Proc. EUROCRYPT , 2019.
- [12] M. Borge, E. Kokoris-Kogias, P. Jovanovic, et al., 'Proof-of-Personhood: Redemocratizing Permissionless Cryptocurrencies,' in Proc. IEEE EuroS&amp;PW , 2017.
- [13] E. Budish, P. Cramton, and J. Shim, 'The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response,' Quarterly Journal of Economics , vol. 130, no. 4, 2015.