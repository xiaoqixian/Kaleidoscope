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

