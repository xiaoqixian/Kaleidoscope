# Index Structures 3

### Linear Hash Tables

Extensive hash tables have some obvious defects:

1.  When the bucket array need to double its size, it's a substantial work. So when you insert some certain records, it may take a long time to get it done.
2.  As the size of the bucket array grows, the memory may be not able to hold it anymore. So part of the extensive hash table may get transported to disk. This causes a sudden increment of disk I/O operation and drags the DB operation speed down.
3.  If the number of records per block is small. There is a chance that two records have a very similar hash value, for example, the first 20 bits of the hash value are the same. In this case, we have to split millions of blocks in this bucket. Even though maybe there are only like 3 records in our hash table.

Another strategy, called *linear hashing*, grows the number of buckets more slowly. The principal new elements we find in linear hashing are:

-   The number of buckets $n$ is always chosen so the average of records per bucket is a fixed fraction, say 80%, of the number of records that fill one block.
-   Since blocks cannot always be split, overflow blocks are permitted, although  the average number of overflow blocks per bucket will much less than 1.
-   The number of bits used to number the entries of the bucket array is $\lceil \log_2n\rceil$, where $n$ is the current number of buckets. These bits are always taken from the *right* (low-order) end of the bit sequence that is produced by the hash function.
-   Suppose $i$ bits of the hash function are being used to number array entries, and a record with key $K$ is intended for bucket $a_1a_2\cdots a_i$, which is the last $i$ bits of $h(K)$. Then let $a_1a_2\cdots a_i$ be $m$. treated as an $i-$bit binary integer. If $m<n$, then the bucket numbered $m$ exists, and we place the record in that bucket. If $n\le m<2^i$, then the bucket $m$ does not yet exist, so we place the record in bucket $m-2^{i-1}$, that is, the bucket we would get if we changed $a_1$ (which must be 1) to 0.

We use $i$ to represent the number of bits of the hash function that currently are used; use $n$ to represent the number of blocks; use $r$ to represent the number of records stored in the hash table.

#### Insertion Into Linear Hash Tables

Each time we insert, we compute $h(K)$ and use the last $i$ bits of bit sequence $h(K)$ as the bucket number $m$. 

If $m<n$, we put the record in bucket $m$. If $m\ge n$, we put the record in bucket $m-2^{i-1}$.

If there is no room in the designated bucket, then we create an *overflow block*, add it to the chain for that bucket, and put the record there.

![image-20210208201149018](https://i.loli.net/2021/02/08/ipLKGY2IEgWPwql.png)

In the above case, the block that the record with key 1111 stays in is an overflow block.

So, in conclusion, we don't create a new bucket because there is no room in the bucket, we create a new bucket because the ratio $r/n$ exceeds the threshold. 

### Multidimensional Indexes

All the index structures discussed so far are *one dimensional*; that is, they assume a single search key, and they retrieve records that match a given search-key value.

#### Applications of Multidimensional Indexes

One important application of multidimensional indexes involves geographic data. A *geographic information system* stores objects in a (typically) 2-dimensional space. The objects may be shapes or points. 

The quires asked of geographic information systems are not typical of SQL queries, although many can be expressed in SQL with some effort. Examples of these types of queries are:

1.  *Partial Match Queries*. We specify values for one or more dimensions and look for all points matching those values in those dimensions. 
2.  *Range Queries*. We give ranges for one or more of the dimensions, and we ask for the set of points within those ranges.
3.  *Nearest-neighbor queries*. We ask for the closest point to a given point.
4.  *Where-am-I queries*. We are given a point and we want to know in which shape, if any, the point is located.

Most data structures for supporting queries on multidimensional data fall into one of two categories:

1.  Hash-table-like approaches.
2.  Tree-like approaches.

### Hash Structures for Multidimensional Data

We'll consider two data structures that generalize hash tables built using a single key. In each case, the bucket for a point is a function of all the attributes or dimensions. 

One scheme, is called the "grid file", usually doesn't hash values along the dimensions, but rather partitions the dimensions by sorting the values along that dimension. The other, called "partitioned hashing", does hash the various dimensions, with each dimension contributing to the bucket number.

#### Grid Files

Think of indexes for queries involving multidimensional data is the *grid file*. Think of the space of points partitioned in a grid. In each dimension, *grid lines* partition the space into *stripes*. Points that fall on a grid line will be considered to belong to the stripe for which that grid line is the lower boundary. 

#### Lookup in a Grid File

Each of the regions into which a space is partitioned can be though of as a bucket of a hash table, and each of the points in that region has its record placed in a block belonging to that bucket. If needed, overflow blocks can be used to increase the size of a bucket.

The grid file uses an array whose number of dimensions is the same as for the data file. To locate the proper bucket for a point, we need to know for each dimension, the list of values at which the grid lines occur. To hash a point, we look at each component of the point and determine the position of the point in the grid for that dimension. The position of the point in each of the dimensions together determine the bucket.

#### Insertion Into Grid Files

Usually when we need to insert a record into a grid file, we first lookup for the record. If there is room in the bucket, then there is nothing more to do. 

If there is no room, there are two general approaches:

1.  Add overflow blocks to the bucket.
2.  Reorganize the structure by adding or moving the grid line.

Obviously, the second approach is more advanced. It saves more space, but once it need to reorganize, it takes a lot of CPU time to do it.



