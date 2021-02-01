# Index Structures

An index is any data structure that takes the value of one or more fields and finds the records with that value quickly.

### Basics

Indexes can be *"dense"*, meaning there is an entry in the index file for every record; indexes can be *"sparse"*, meaning that only some of the data records are represented in the index, often one index entry per block of the data file.

Indexes can be *"primary"* and *"secondary"*, a primary index determines the location of the records of the data file, while a secondary index does not.

#### Dense Indexes

If records are sorted, we can build on them a *dense index*. With a key *K*, we can use binary search to find *K* the index, if there are *n* blocks of index, we only look at $\log_2n$ of them.

![image-20210131225241373](https://i.loli.net/2021/01/31/JwbFjxcrl7dBCuz.png)

#### Sparse Indexes

A Sparse Index has only one key-pointer pair per block of the data file. It saves more space, but takes more time for finding a certain record.

![image-20210131225317011](https://i.loli.net/2021/01/31/gzSp4NHvLcDXb62.png)

#### Multiple Levels of Index

An index may cover multiple blocks, so we may still need to do may disk I/O to find the correct record. So it's a good idea to build another level of index on the index, we can make the use of the first level of index more efficient.

![image-20210131225811122](https://i.loli.net/2021/01/31/ev41SkXEDNgFuY6.png)

The first level indexes can be dense or sparse (sparse in the figure), however, the second level and higher must be sparse. Otherwise it would have an exact number of indexes as the first-level indexes. 

When I say first-level index, I mean the level that directly points to the records, so don't get it wrong.

#### Secondary Indexes

A secondary index is a data structure that facilitates finding records given a value for one or more fields. However, the secondary index is distinguished from the primary index in that a secondary index does not determine the placement of records, which may have been decided by a primary index on some other field. 

![image-20210131230927697](https://i.loli.net/2021/01/31/k4Cwnmyrz5cxRVK.png)

 As you can see in the figure, even though all the search keys are sorted, the pointers are not sorted at all. 

However, the keys in the index file are sorted, otherwise when we search with a secondary index, the DB engine has to run through all of the index-records pairs. 

And most of the time, a secondary index is not unique. The result is that the pointer in one block can go to many different data blocks, instead of one or a few consecutive blocks, because normally a secondary index can match multiple records. 

Thus, using a secondary index may result in many more disk I/O's than if we get the same number of records via a primary index.

#### Indirection in Secondary Indexes

If a search-key value appears *n* times in the data file, then the value is written *n* times in the index file. 

A convenient way to avoid repeating values is to use a level of indirection, called *buckets*.

![image-20210131233003372](https://i.loli.net/2021/01/31/fmnrPqld47ABvCY.png)

A bucket block is used to store pointers, in which pointers associated with a search value are stored consecutively. 

The scheme of the figure saves space as long as search-key values are larger than pointers, and the average key appears at least twice. 

However, this bucket conception has a huge defect. When we want to insert a record into the DB, as all the pointers are stored consecutively, it would cost a lot for the insert. 

### B-Trees

In essence:

-   B-trees automatically maintain as many levels of index as is appropriate for the size of the file being indexed.
-   B-trees manage the space on the blocks they use so that every block is between half used and completely full.

The *B+ tree* is the mostly used tree in the B-Trees family.

#### The Structure of B-Trees

There are three layers in a B-Tree: the root, an intermediate layer, and leaves, but any number of layers is possible.

There is a parameter $n$ associated with each B-Tree index, and this parameter determines the layout of all blocks of the B-Tree. Each block will have space for $n$ search-key and $n+1$ pointers.

![image-20210201102026277](https://i.loli.net/2021/02/01/oMqgeW8rlR7nBpc.png)

Several rules in a B-Tree:

-   Keys are distributed among the leaves in sorted order, from left to right.

-   At the root, there are at least two used pointers. All pointers point to B-tree blocks at the level below.

-   At a leaf, the last pointer points to the next leaf block to the right, i.e., to the block with next higher keys. Among the other $n$ pointers in a leaf block, at least $\lfloor(n+1)/2\rfloor$ of these pointers are used and point to **data records**; unused pointers are null and do not point anywhere. The $i$th pointer, if it is used, points to a record with the $i$th key.

-   At an interior node, all $n+1$ pointers can be used to point to B-tree blocks at the next lower level. At least $\lceil(n+1)/2\rceil$ of them are actually used.

    If $j$ pointers are used, then there will be $j-1$ keys, say $K_1,K_2,\cdots, K_{j-1}$. The first pointer points to a part of the B-tree where some of the records with keys less than $K_1$ will be found. The second pointer goes to that part of the tree where all records with keys that are at least $K_1$, but less than $K_2$ will be found, and so on. 

    Note that some records with keys fat below $K_1$ or fat above $K_{j-1}$ may not be reachable from this block at all, but will be reached via another block at the same level.

-   All used pointers and their keys appear at the beginning of the block with the exception of the $(n+1) $st pointer in a leaf, which points to the next leaf.

![image-20210201115115327](https://i.loli.net/2021/02/01/VDPuHUsxEjNObCM.png)

For an interior node, at least the first key and the first two pointer are presented. 

#### Applications of B-trees

The sequence of pointers at the leaves of a B-tree can play the role of any of the pointer sequences coming out of an index file that we learned before.

Here are some examples:

1.  The search key of the B-tree is the primary key for the data file, and the index is dense. That is, there is one key-pointer pair in a leaf for every record of the data file. The data file may or may not be sorted by primary file.
2.  The data file is sorted by the primary key, and the B-tree is a sparse index with one key-pointer pair at a leaf for each block of the data file.
3.  The data file is sorted by an attribute that is not a key, and this attribute is the search key for the B-tree. For each key value $K$ that appears in the data file there is one key-pointer pair at a leaf. That pointer goes to the first of the records that have $K$ as their sort-key value.

If we do allow duplicate occurrences of a search key, then we need to change slightly the definition of what the keys at interior nodes mean. 

Now, suppose there are keys $K_1,K_2,\cdots,K_n$ at an interior node. Then $K_i$ will be the smallest new key that appears in the part of the subtree accessible from the $(i+1)$st pointer. By "new", we mean that there are no occurrences of $K_i$ in the portion of the tree to the left of the $(i+1)$st subtree, but at least one occurrence of $K_i$ in that subtree. Not that in some situations, there will be no such key, in which case $K_i$ can be taken to be null.

![image-20210201124819943](https://i.loli.net/2021/02/01/4As3I2YWQJpKiMr.png)

In the above case, the search key 23 occurred four times. For the second interior node, as the second pointer of it cannot find such a key that satisfies the condition. So the first search key of it is null. 

#### Range Queries

B-trees are useful not only for queries in which a single value of the search key in sought. 

SQL examples of range queries using a search key attribute $k$ are:

```sql
SELECT * FROM R WHERE R.k >= 10 AND R.k <= 25;
```

If we want to find all keys in the range $[a,b]$ at the leaves of a B-tree, we do a lookup to find the key $a$. Whether or not it exists, we are led to a leaf where $a$ could be, and we search for the leaf for keys that are $a$ or greater. As long as we do not find a key greater than $b$ in the current block, we follow the pointer to the next leaf and repeat our search for keys in the range $[a,b]$.

If a is $-\infty$, we can design a special search key that will always take us to the first leaf in the DB engine.

#### Insertion Into B-Trees

Steps:

1.  Find a place for the new key in the appropriate leaf, and we put it there if there is room.
2.  If there is no room in the proper leaf, we split the leaf into two and divide the keys between the two new nodes, so each is half full or just over half full.
3.  The splitting of nodes at one level appears to the level above as if a new key-pointer pair needs to be inserted at that higher level. We may thus recursively apply this strategy to insert at the next level: if there is room, insert it; if not, split the parent node and continue up the tree.
4.  As an exception, if we try to insert into the root, and there is no room, then we split the root into two nodes and create a new root at the next higher level; the new root has the two nodes resulting from the split as its children. Recall that no matter how large $n$ is, it is always permissible for the root to have only one key and two children.

Example:

![image-20210201115115327](https://i.loli.net/2021/02/01/VDPuHUsxEjNObCM.png)

We're going to insert a search key-value 40 into the above B-tree.

1.  First we find a place for the search key 40, and it will be the fifth leaf, but there is no room.

2.  According to the steps, we need to split the fifth leaf, and the result   will be like:

    ![image-20210201173758018](https://i.loli.net/2021/02/01/u6FtTywWxBl9K7J.png)

    We find out that the new sixth leaf is not pointed to, so we need to add a pointer in its parent node. And we soon find out that there is no room in its parent node.

3.  So we need to split the parent node, and we get this:

    ![image-20210201193427291](https://i.loli.net/2021/02/01/LRxDiPMIhsHbWFk.png)

    If we want to describe the process in code, we have to do it recursively.

#### Deletion From B-Tree

First we must locate the key-pointer pair of the record in a leaf of the B-tree. We then delete the record itself from the data file, and we delete the key-pointer pair from the B-tree.

If the B-tree node from which a deletion occurred **still has at least the minimum number of keys and pointers,** then there is nothing more to be done. 

If not, we then need to do one of two things for a node $N$ whose contents are sub-minimum; one case requires a recursive deletion up to three:

1.  If one of the adjacent siblings of node $N$ has more that the minimum number of keys and pointers, then one key-pointer pair can be moved to $N$, keeping the order of keys intact. Usually the moved key will be the smallest key if it's a right sibling or the biggest key if it's a left sibling. 

    Possibly, the keys at the parent of $N$ must be adjusted to reflect the new situation. For instance, if we move a key from a right adjacent sibling, say $M$, then the key moved must be its smallest key. So we need to update its parent node at least. 

2.  The hard case is when neither adjacent sibling can be used to provide an extra key for $N$.  In this case, we have two adjacent nodes, $N$ and a sibling $M$; the latter has the minimum number of keys and the former has fewer than the minimum. Therefore, together they have no more keys and pointers than are allowed in a single node. We merge these two nodes, effectively deleting one of them. We need to adjust the keys at the parent, and then delete a key and pointer at the parent. If the parent is still full enough, then we are done. If not, then we recursively apply the deletion algorithm at the parent.

Example:

![image-20210201115115327](https://i.loli.net/2021/02/01/wslarx3KOMyCe5i.png)

Suppose we need to delete key 7, it is the minimum key of the second leaf, if we delete it from the second leaf, then the second leaf only has one key, and we need at least two in every leaf. So we need to "borrow" an extra key from its siblings. We choose the left sibling. 

![image-20210201221022288](https://i.loli.net/2021/02/01/piWomRT4MscehIl.png)

Next, suppose we delete key 11. This time, we cannot just take an extra key from its sibling, cause its sibling is down to the minimum number of keys. 

According to the case 2, we need to merge this two nodes. 

So after we merge this two nodes, the B-tree is like this:

![image-20210201221533726](https://i.loli.net/2021/02/01/wnrVUvsDJNWFdQX.png)

Then we find out the first child of the root has no keys and one pointer, thus we try obtain an extra key from its sibling, which is 23. 

And after that, we need to update the root. The final result is like:

![image-20210201222102857](https://i.loli.net/2021/02/01/nEKgMAS3vFLQOCk.png)

