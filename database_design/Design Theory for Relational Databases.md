# Design Theory for Relational Databases

### Functional Dependencies

There is a design theory for relations that lets use examine a design carefully and make improvements based on a few simple principles.

The so called "functional dependencies" is a statement of a type that generalizes the idea of a key for a relation. 

#### Definition of Functional Dependency

A *functional dependency* on a relation $R$  is a statement of the form "If two tuples of $R$ agree on all of the attributes $A_1,A_2,\cdots,A_n$", then they must agree on all of another list of attributes $B_1,B_2,\cdots,B_m$. 

We write this functional dependency as $A_1A_2\cdots A_n\rightarrow B_1B_2\cdots B_m$ and say that "$A_1A_2\cdots A_n$ functionally determines  $B_1B_2\cdots B_m$".

If we can make sure that every record of the relation $R$ will be one in which a given functional dependency is true, then we say the relation $R$ *satisfies* an functional dependency $f$.

#### Keys of Relations 

We say a set of one or more attributes $\{A_1,A_2,\cdots,A_n\}$ is a *key* for a relation $R$ if:

1.  Those attributes functionally determine all other attributes of the relation.
2.  No proper subset of $\{A_1,A_2,\cdots,A_n\}$ functionally determine all other attributes of $R$.

#### Superkeys

A set of attributes that contains a key is called a *superkey*, short for "superset of a key". Every superkey satisfies the first condition of a key, however, the second condition is not satisfied for a superkey that contains more than just a key.

### Rules About Functional Dependencies

Suppose we are told of a set of functional dependencies that a relation satisfies. Often, we can deduce that the relation must satisfy certain other functional dependencies. This ability of discovering additional functional dependencies is essential when we talk about the design of good relation schemas later.

#### Reasoning About Functional Dependencies

Functional dependencies often can be presented in several different ways, without changing the set of legal instances of the relation. We say:

-   Two sets of functional dependencies of $S$ and $T$ are *equivalent* if the set of relation instances satisfying $S$ is exactly the same as the set of relation instances satisfying $T$.
-   More generally, a set of functional dependencies $S$ follows from a set of functional dependencies $T$ if every relation instance that satisfies all the functional dependencies in $T$ also satisfies all the functional dependencies in $S$.

#### The Splitting/Combining Rule

Splitting rule: If $A_1A_2\cdots A_n\rightarrow B_1B_2\cdots B_m$, then $A_1A_2\cdots A_n\rightarrow B_i$ for $i=1,2,\cdots,m$.

Combining Rule: If $A_1A_2\cdots A_n\rightarrow B_i$ for $i=1,2,\cdots,m$, then $A_1A_2\cdots A_n\rightarrow B_1B_2\cdots B_m$.

#### Trivial Functional Dependencies

A constraint of any kind on a relation is said to be *trivial* if it holds for every instance of the relation, regardless of what other constraints are assumed.

Say $X\rightarrow Y$, if $Y$ is not a subset of $X$, then the functional dependency $X\rightarrow Y$ is not trivial. If $Y$ is a subset of $X$, the functional dependency is trivial.

#### Computing the Closure of Attributes 

Starting with the given set of attributes, we repeatedly expand the set by adding the right sides of functional dependencies as soon as we have included their left sides. Eventually, we cannot expand the set any further, and the resulting set is the **closure**. 

We denote the closure of a set of attributes $A_1A_2\cdots A_n$ by $\{A_1,A_2,\cdots,A_n\}^+$. 

By computing the closure of any set of attributes, we can test whether any given functional dependency $A_1A_2\cdots A_n\rightarrow B$ follows from a set of functional dependencies $S$. If $B$ is in $\{A_1,A_2,\cdots,A_n\}^+$, then the functional dependency does follow from $S$. Else, it does not follow from $S$. 

#### Armstrong Principles System

In 1974, W. W. Armstrong concluded a set of functional dependencies deduction rules, which is called the *Armstrong Principles System*. 

Say a relation $R(U,F)$, $U$ is a set of attributes and $F$ is a set of functional dependencies. For the relation $R$, we have such deduction rules:

1.  *Reflexivity*: If $Y\subseteq X\subseteq U$, then $X\rightarrow Y$.
2.  *Augmentation*: If $X\rightarrow Y$, then $XZ\rightarrow YZ$.
3.  *Transitivity*: If $X\rightarrow Y, Y\rightarrow Z$, then $X\rightarrow Z$.
4.  *The Combining Rule*: If $X\rightarrow Y,X\rightarrow Z$, then $X\rightarrow YZ$.
5.  *The Pseudo Transitivity Rule*: If $X\rightarrow Y, WY\rightarrow Z$, then $XW\rightarrow Z$.
6.  *The Decomposition Rule*: If $X\rightarrow Y$ and $Z\subseteq Y$, then $X\rightarrow Z$.

#### Closing Sets of Functional Dependencies

Sometimes we have a choice of which functional dependencies we use to represent the full set of functional dependencies for a relation. If we were given a set of functional dependencies $S$, then any set of functional dependencies equivalent to $S$ is said to be a *basis* for S.

A *minimal basis* for a relation is a basis $B$ that satisfies three conditions:

1.  All the functional dependencies in $B$ have singleton right sides.
2.  If any functional dependency is removed from $B$, the result is no longer a basis.
3.  If for any functional dependency in $B$ we remove one or more attributes from the left side of $F$, the result is no longer a basis.

#### Projecting Functional Dependencies

Suppose we have a relation $R$ with set of functional dependencies $S$, and we project $R$ by computing $R_1=\pi_L(R)$, for some list of attributes $R$. When functional dependencies hold in $R_1$? 

This algorithm is very useful when we need to decompose a relation. 

Algorithm:

1.  Let $T$ be the eventual output set of functional dependencies. Initially, $T$ is empty.
2.  For each set of attributes $X$ that is a subset of the attributes of $R_1$, compute $X^+$. This computation is performed with respect to the set of functional dependencies $S$, and may involve attributes that are in the schema of $R$ but not $R_1$. Add to all nontrivial functional dependencies $X\rightarrow A$ such that $A$ is both in $X^+$ and an attribute of $R_1$.
3.  Now, $T$ is a basis for the functional dependencies that hold in $R_1$, but may not be the minimal basis. We can construct a minimal basis by modifying $T$ as follows:
    1.  If there is an functional dependency $F$ in $T$ that follows from the other functional dependencies in $T$, remove $F$ from $T$.
    2.  Let $Y\rightarrow B$ be an functional dependency in $T$, with at least two attributes in $Y$, and let $Z$ be $Y$ with one of its attributes removed. If $Z\rightarrow B$ follows from the functional dependencies in $T$, then replace $Y\rightarrow B$ by $Z\rightarrow B$.
    3.  Repeat the above steps in all possible ways until no more changes to $T$ can be made.

By definition, it may be a little hard to understand. Let's take a example: Suppose $R(A,B,C,D)$ has functional dependencies $A\rightarrow B,B\rightarrow C,$ and $C\rightarrow D$. Suppose also that we wish to project out the attribute $B$, leaving a relation $R_1(A,C,D)$. In principle, to find the functional dependencies for $R_1$, we need to take the closure of all eight subsets of $\{A,B,C \}$, using the full set of functional dependencies, including those involving $B$. However, there are some obvious simplifications we can make.

-   Closing the empty set and the set of all attributes cannot yield a nontrivial functional dependency.
-   If we already know that the closure of some set $X$ is all attributes, then we cannot discover any new functional dependencies by closing supersets of $X$.

Thus, we may start with the closures of the singleton sets, and then move on to the doubleton sets if necessary. For each closure of a set $X$, we add the functional dependency $X\rightarrow E$ for each attribute $E$ that is in $X^+$ and in the schema of $R_1$, but not in $X$.

First, $\{A\}^+ = \{A,B,C,D\}$. Thus, $A\rightarrow C$ and $A\rightarrow D$ hold in $R_1$. Note that $A\rightarrow B$ is true in $R$, but makes no sense in $R_1$ because $B$ is not an attribute of $R_1$.

Next, we consider $\{C\}^+ = \{C,D\}$, from which we get the additional functional dependency $C\rightarrow D$ for $R_1$. 

Since $\{D\}^+ = \{D\}$, we can add no more functional dependencies, and are done with the singletons.

Since $\{A\}^+$ already includes all attributes in $R_1$, there is no point in considering any superset of $\{A\}$. Thus, the only doubleton whose closure we need to take is $\{C,D\}^+ = \{C,D\}$. This observation allows us to add nothing. We are done with the closures, and functional dependencies we have discovered are $A\rightarrow C,A\rightarrow D$ and $C\rightarrow D$. A simpler, equivalent set of functional dependencies for $R_1$ is $A\rightarrow C, C\rightarrow D$. 

### Design of Relational Database Schemas

Careless selection of a relational database schema can lead to redundancy and related anomalies. 

#### Anomalies

Problems such as redundancy occur when we try to cram too much into a single relation are called *anomalies*.

The principal kinds of anomalies that we encounter are:

1.  Redundancy
2.  Update Anomalies. We mat change information in one tuple but leave the same information unchanged in another.
3.  Deletion Anomalies. If a set of values becomes empty, we may lose other information as a side effect.

#### Decomposing Relations

The accepted way to eliminate these anomalies is to *decompose relations.* Decomposition of $R$ involves splitting the attributes of $R$ to make the schemas of two new relations.

Given a relation $R(A_1,A_2,\cdots, A_n)$, we may decompose $R$ into two relations  $S(B_1,B_2,\cdots, B_m)$ and $T(C_1,C_2,\cdots,C_k)$ such that:

1.  $\{A_1,A_2,\cdots, A_n\} = \{B_1,B_2,\cdots, B_m\}\cup \{C_1,C_2,\cdots,C_k\}$.
2.  $S= \pi_{B_1,B_2,\cdots,B_m}(R)$
3.  $T=\pi_{C_1,C_2,\cdots,C_k}(R)$

#### Boyce-Codd Normal Form

The goal of decomposition is to replace a relation by several that do not exhibit anomalies. There is a condition called *Boyce-Codd normal form*, or *BCNF*, under which the anomalies discussed can be guaranteed not to exist.

-   A relation $R$ is in BCNF if and only if: whenever there is a nontrivial functional dependency $A_1A_2\cdots A_n\rightarrow B_1B_2\cdots B_m$ for $R$ , it is the case that $\{A_1,A_2,\cdots, A_n\}$ is a superkey for $R$.

That is, the **left side of every nontrivial functional dependency must be a superkey.** Recall that a superkey need not be minimal. Thus, an equivalent statement of the BCNF condition is that **the left side of every nontrivial functional dependency must contain a key.**

The purpose of arising BCNF is to eliminate redundancies produced by functional dependencies. In BCNF, no attribute can be deduced from other non key attributes by using only functional dependencies. 

#### Decomposition into BCNF

By repeatedly choosing suitable decompositions, we can break any relation schema into a collection of subsets of its attributes with the following important properties:

1.  These subsets are the schemas of relation in BCNF.
2.  The data in the original relation is represented faithfully by the data in the relations that are the result of the decomposition. Roughly, we need to be able to reconstruct the original relation instance exactly from the decomposed relation instances.

Example: Consider a relation with schema (the schema is about movies)
$$
\{title, year, studioName, president, presidentAddress \}
$$
$\{title,year\}$ is the only key of the schema, by this two attributes, we can deduce all other attributes. However, the relation is not in BCNF. Cause  once we know the $president$, we are able to know the $presidentAddress$, which violates the rule that *no attribute can be deduced from other non key attributes by using only functional dependencies.* And the $studioName$ can also determines the $president$.

So we need to decompose the relation into three. 
$$
\{title, year, studioName\}\\
\{studioName, president\}\\
\{president, presidentAddress\}
$$
In general, we must keep applying the decomposition rule as many times as needed, until our relations are in BCNF. 

#### BCNF Decomposition Algorithm

INPUT: A relation $R$ with a set of functional dependencies $S$.

OUTPUT: A decomposition of $R$ into a collection of relations, all of which are in BCNF.

METHOD: The following steps can be applied recursively to any relation $R$ and set of functional dependencies $S$.

1.  Check whether $R$ is in BCNF. If so, nothing more need to be done.
2.  If there are BCNF violations, let one be $X\rightarrow Y$. Use the algorithm we've talked above to compute the closure $X^+$. Choose $R_1 = X^+$ as  one relation and let $R_2$ have attributes $X$ and those attributes of $R$ that are not in $X^+$.
3.  By projecting functional dependencies, we can compute the sets of $R_1$ and $R_2$; let them be $S_1$ and $S_2$ respectively.
4.  Recursively decompose $R_1$ and $R_2$ using this algorithm. Return the union of the results of these decompositions.

**Let's do some exercises.**

For all the exercises, do the following:

-   Indicate all the BCNF violations. Do not forget to consider functional dependencies that are not in the given set, but follow from them. However, it is not necessary to give violations that have more than one attribute on the right side.
-   Decompose the relations, as necessary, into collections of relations that are in BCNF.

Exercises:

1.  $R(A,B,C,D)$ with functional dependencies $AB\rightarrow C, C\rightarrow D$ and $D\rightarrow A$.

    Obviously, $D\rightarrow A$ violates the BCNF rules. We can decompose it as:
    $$
    \{A,B,C,D\}\\
    \{D,A\}
    $$

2.  $R(A,B,C,D)$ with functional dependencies $B\rightarrow C$ and $B\rightarrow D$.

    The problem is that $A$ can not be determined, but that's OK, the rest of attributes don't violate BCNF.

    