![[Pasted image 20250119204702.png]]
```
Definition 0.3.2: A set 𝐴A is a subset of a set 𝐵B if 𝑥∈𝐴x∈A implies 𝑥∈𝐵x∈B, and we write 𝐴⊆𝐵A⊆B. That is, all members of 𝐴A are also members of 𝐵B. At times, we write 𝐵⊇𝐴B⊇A to mean the same thing.Two sets 𝐴A and 𝐵B are equal if 𝐴⊆𝐵A⊆B and 𝐵⊆𝐴B⊆A. We write 𝐴=𝐵A=B. That is, 𝐴A and 𝐵B contain exactly the same elements. If it is not true that 𝐴A and 𝐵B are equal, then we write 𝐴≠𝐵A=B.A set 𝐴A is a proper subset of 𝐵B if 𝐴⊆𝐵A⊆B and 𝐴≠𝐵A=B. We write 𝐴⊂𝐵A⊂B.For the example sets 𝑆S and 𝑇T defined above, 𝑇⊂𝑆T⊂S, but 𝑇≠𝑆T=S. So 𝑇T is a proper subset of 𝑆S. If 𝐴=𝐵A=B, then 𝐴A and 𝐵B are simply two names for the same exact set.To define new sets, one often uses the set building notation:{𝑥∈𝐴:𝑃(𝑥)}{x∈A:P(x)}.This notation refers to a subset of the set 𝐴A containing all elements of 𝐴A that satisfy the property 𝑃(𝑥)P(x). Using 𝑆={0,1,2}S={0,1,2} as above, {𝑥∈𝑆:𝑥≠2}{x∈S:x=2} is the set {0,1}{0,1}. The notation is sometimes abbreviated as {𝑥:𝑃(𝑥)}{x:P(x)}, meaning 𝐴A is not mentioned when understood from context. Furthermore, 𝑥∈𝐴x∈A is sometimes replaced with a formula to make the notation easier to read.
```

![[Pasted image 20250119204355.png]]
```
**Definition 0.3.4.**

(i) A **union** of two sets A and B is defined as:  
A ∪ B := {x : x ∈ A or x ∈ B}.

(ii) An **intersection** of two sets A and B is defined as:  
A ∩ B := {x : x ∈ A and x ∈ B}.

(iii) A **complement of B relative to A** (or **set-theoretic difference of A and B**) is defined as:  
A \ B := {x : x ∈ A and x ∉ B}.

(iv) We say **complement of B** and write Bᶜ instead of A \ B if the set A is either the entire universe or if it is the obvious set containing B, and is understood from context.

(v) We say sets A and B are **disjoint** if:  
A ∩ B = ∅.

The notation Bᶜ may be a little vague at this point. If the set B is a subset of the real numbers ℝ, then Bᶜ means ℝ \ B. If B is naturally a subset of the natural numbers, then Bᶜ is ℕ \ B. If ambiguity can arise, we use the set difference notation A \ B.

```

```
Definition 0.3.10. Let 𝐴 and 𝐵 be sets. The Cartesian product is the set of tuples defined as
𝐴 × 𝐵  := {(𝑥, 𝑦) : 𝑥 ∈ 𝐴, 𝑦 ∈ 𝐵}
```

```
Definition 0.3.11. A function 𝑓 : 𝐴 → 𝐵 is a subset 𝑓 of 𝐴 × 𝐵 such that for each 𝑥 ∈ 𝐴,
there exists a unique 𝑦 ∈ 𝐵 for which (𝑥, 𝑦) ∈ 𝑓 . We write 𝑓 (𝑥) = 𝑦. Sometimes the set 𝑓 is
called the graph of the function rather than the function itself.
```

```
Definition 0.3.13. Consider a function 𝑓 : 𝐴 → 𝐵. Define the image (or direct image) of a
subset 𝐶 ⊂ 𝐴 as
 
𝑓 (𝐶) B 𝑓 (𝑥) ∈ 𝐵 : 𝑥 ∈ 𝐶 .
Define the inverse image of a subset 𝐷 ⊂ 𝐵 as
𝑓 −1 (𝐷) B 
 𝑥 ∈ 𝐴 : 𝑓 (𝑥) ∈ 𝐷 .
In particular, 𝑅( 𝑓 ) = 𝑓 (𝐴), the range is the direct image of the domain 𝐴.
```

```
Definition 0.3.17. Let 𝑓 : 𝐴 → 𝐵 be a function. The function 𝑓 is said to be injective or
one-to-one if 𝑓 (𝑥1 ) = 𝑓 (𝑥 2 ) implies 𝑥1 = 𝑥2. In other words, 𝑓 is injective if for all 𝑦 ∈ 𝐵, the
set 𝑓 −1({𝑦}) is empty or consists of a single element. We call such an 𝑓 an injection.
f 𝑓= 𝐵, then we say 𝑓 is  or  In other words, 𝑓 is surjective if the
```

```
Definition 0.3.18. Consider 𝑓 : 𝐴 → 𝐵 and 𝑔 : 𝐵 → 𝐶. The composition of the functions 𝑓
and 𝑔 is the function 𝑔 ◦ 𝑓 : 𝐴 → 𝐶 defined as
(𝑔 ◦ 𝑓 )(𝑥) B 𝑔 𝑓 (𝑥))
```


```
Definition 0.3.19. Given a set 𝐴, a binary relation on 𝐴 is a subset R ⊂ 𝐴 × 𝐴, which consists
of those pairs where the relation is said to hold. Instead of (𝑎, 𝑏) ∈ R, we write 𝑎 R 𝑏.
```

```
When 𝑓 : 𝐴 → 𝐵 is a bĳection, then the inverse image of a single element, 𝑓 −1({𝑦}), is
always a unique element of 𝐴. We then consider 𝑓 −1 as a function 𝑓 −1 : 𝐵 → 𝐴 and we
write bĳection simply 𝑓 : ℝ 𝑓 −1 (𝑦). ℝ defined In this case, by 𝑓 we B call 𝑥 3, 𝑓 −1 we the have inverse 𝑓 −1 function = √
 3 𝑥.
 of 𝑓 . For instance, for the
→ (𝑥) (𝑥)Definition 0.3.18. Consider 𝑓 : 𝐴 → 𝐵 and 𝑔 : 𝐵 → 𝐶. The composition of the functions 𝑓
and 𝑔 is the function 𝑔 ◦ 𝑓 : 𝐴 → 𝐶 defined as
(𝑔 ◦ 𝑓 )(𝑥) B 𝑔 𝑓 (𝑥)
 .
For example, 3 if 𝑓 : ℝ → ℝ is 𝑓 (𝑥) B 𝑥 3 and 𝑔 : ℝ → ℝ is 𝑔(𝑦) = sin(𝑦), then
(𝑔 ◦ 𝑓 )(𝑥) = sin(𝑥 ). It is left to the reader as an easy exercise to show that composition
of one-to-one maps is one-to-one and composition of onto maps is onto. Therefore, the
composition of bĳections is a bĳection.
```

```
Definition 0.3.21. A relation R on a set 𝐴 is said to be
(i) Reflexive if 𝑎 R 𝑎 for all 𝑎 ∈ 𝐴.
(ii) Symmetric if 𝑎 R 𝑏 implies 𝑏 R 𝑎.
(iii) Transitive if 𝑎 R 𝑏 and 𝑏 R 𝑐 implies 𝑎 R 𝑐.
If R is reflexive, symmetric, and transitive, then it is said to be an equivalence relation.
```

```
Definition 0.3.23. Let 𝐴 be a set and R an equivalence relation. An equivalence class of
𝑎 ∈ 𝐴, often denoted by [𝑎], is the set {𝑥 ∈ 𝐴 : 𝑎 R 𝑥}.
```