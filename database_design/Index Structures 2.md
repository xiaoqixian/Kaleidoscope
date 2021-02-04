# Index Structures 2

### Hash Tables

The hash table is a main-memory data structure, in such a structure there is a *hash function* that takes a search key as an argument and computes from it an integer in the range 0 to $B-1$, $B$ is the number buckets. A bucket is a linked list, we store records by linking them to buckets.

If we have a record with a search key of $K$, we first use the hash function to compute from it an integer, then we find the bucket of the target range. 

#### Secondary-Storage Hash Tables

A hash table has to store so many records that they must be kept mainly in secondary storage. 

A bucket consists of blocks, rather than pointers to the records. If a bucket has too many records, a chain of overflow blocks can be added to the bucket to hold more records.

We shall assume that the location of the first block for many bucket $i$ can be found given $i$.

Here's an illustration of a hash table:

![image-20210204134009696](https://i.loli.net/2021/02/04/7rZQsoqfRkaz36g.png)

And, the number of buckets, which is $B$, is not constant. The ones with constant number of buckets are called *static hash tables*. 

In fact, as the number of records grows, to optimize the efficiency of the hash table, we can try to add more buckets. Cause if a bucket contains too many blocks, it will take a lot of time searching the target block. 

#### Extensible Hash Tables

For an extensible hash table, the major additions to the simpler static hash table structure are:

1.  There is a level of indirection for the buckets, which is an array of pointers to blocks represents the buckets, instead of the array holding the data blocks themselves.
2.  The array of pointers can grow, its length is always the power of 2. 
3.  Certain buckets can share a block if the total number of records in those buckets can fit in the block.
4.  The hash function $h$ computes for each key a sequence of $k$ bits for some large $k$, say 32. However, the bucket numbers will at all times use some smaller number of bits, say $i$ bits, from the beginning or end of this sequence. The bucket array will have $2^i$ entries when $i$ is the number of bits used.

![image-20210204165925366](https://i.loli.net/2021/02/04/pTarPYvGbSt3Muq.png)

In the above case, we use hash function to compute a 4 bits sequence from a search key, and we only take 1 bit of them. So there are only 2 entries in bucket array. 

#### Insertion Into Extensible Hash Tables

To insert a record with a search key $K$, we first compute a sequence from $K$, take the first $i$ bits of the sequence. Then we find the target pointer by the bits, and finally get the target block following the pointer. 

See if there is any available room in the block, if is, insert the record and we're done. 

If no room, there are two possibilities, depending on the number $j$, which indicates how many bits of the hash value are used to determine membership in the block (the value of $j$ can be found in the "nub" of each block in the figure.).

If $j==i$, then we need to increase $i$ by 1, which means doubling the length of the bucket entries. Now we need new indexes for the bucket. Suppose originally we use an index $w$, after the length increment, we use $w0$ and $w1$ to index two different entries. 

If $j<i$:

1.  If $j<i$, means there are overfull records in the current block. So we need to add one more block to the bucket. 

2.  For now, we split the block into two. Distribute records in $B$ to the two blocks, based on the value of their $(j+1)$st bit —— records whose key has 0 in that bit stay in $B$ and those with 1 there go to the new block.

3.  Put $j+1$ into the block "nub" to indicate the number of bits used to determine membership.

4.  Adjust the pointers in the bucket array so entries that formerly pointed to $B$ now point either to $B$ or the new block, depending on their $(j+1)$st bit.

    The "adjust" may be a little hard to understand. For example:

    ![image-20210204210347201](https://i.loli.net/2021/02/04/n2iaIMgtfbWme6Q.png)

    In the above case, when we need to insert a record with a hash value of "1001". And as we see, $j$ already equals to $i$, so we first need to expand the bucket array by increasing $i$ by 1. 

    Next, we need to adjust three records: 1001, 1010, 1001. Cause their  first 2 bits are the same, so we need to split the current block, one of which is pointed by 100 index and another of which is pointed by 101 index.

    ![image-20210204210252808](https://i.loli.net/2021/02/04/dS5q8FGfCnjWwpt.png)

Since there is a chance that all the records may go into one of the blocks, if so, we need to repeat the process on the overfull block.