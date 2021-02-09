# The Relational Model of Data

### What is a Data Model?

A *data model* is a notation for describing data or information. The description generally consists of three parts:

1.  *Structure of the data*.
2.  *Operations on the data*.
3.  *Constraints on the data.*

#### Important Data Models

Two data model of preeminent importance:

-   The relational model.
-   The semistructured-data model.

The relational model is based on tables. 

The semistructured data resembles trees or graphs, rather than tables or arrays. The principal manifestation of this viewpoint is XML, a way to represent data by hierarchically nested tagged elements.

#### Other Data Models

A modern trend is to add object-oriented features to the relational model.

1.  Values can have structure.
2.  Relations can have associated methods.

### Basics of the Relational Model

A two-dimensional table called a *relation*.

A few terms of a relation:

-   Attribute: The columns of a relation are named by *attributes*.
-   Schema: The name of a relation and the set of attributes for a relation is called the *schema* for that relation.
-   Tuples: The rows of a relation, other than the header row containing the attribute names, are called *tuples*. A tuple has one component of an attribute.
-   Domains: A *domain* is associated with each attribute of a relation and it's required to be of some elementary types.

>   We shall generally follow the convention that relation names begin with a uppercase letter, and attributes names begin with a lowercase letter.

