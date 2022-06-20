Rust 迭代器中的函数式编程特性设计

众所周知，Rust 中加入了很多的函数式编程特性。其中很大一部分体现在 Rust 的迭代器设计上。

在 Rust 标准库中，所有可迭代的容器均可以通过 `into_iter()`、`iter()`、`iter_mut()` 三个函数得到该容器的迭代器，分别对应迭代 `T`, `&T` 和 `&mut T` 。用户自定义类型也可以通过实现 `Iterator` trait 来获得迭代器的所有特性，其中必须实现的函数只有 `next` 一个函数，可以说非常方便。

但是在由容器转换为迭代器的过程则比较复杂，由于数据结构的不同，不同容器的迭代逻辑也有所不同。Rust 的解决方案是不同迭代器分别实现 `IntoIterator` trait, 在调用 `into_iter` 之后可得到一个实现了 `Iterator` 的迭代器。

### filter

首先需要了解一下 iterator 的 `find` 函数：

```rust
    fn find<P>(&mut self, predicate: P) -> Option<Self::Item>
    where
        Self: Sized,
        P: FnMut(&Self::Item) -> bool,
    {
        #[inline]
        fn check<T>(mut predicate: impl FnMut(&T) -> bool) -> impl FnMut((), T) -> ControlFlow<T> {
            move |(), x| {
                if predicate(&x) { ControlFlow::Break(x) } else { ControlFlow::CONTINUE }
            }
        }

        self.try_fold((), check(predicate)).break_value()
    }
```

如上，`find` 将 `predicate` 函数包裹为一个返回 `ControlFlow` 的函数，然后再调用 `try_fold` 使得当遇到符合 `predicate` 值时返回退出并携带有退出的值。

filter 结构为：

```rust 
pub struct Filter<I, P> {
    // Used for `SplitWhitespace` and `SplitAsciiWhitespace` `as_str` methods
    iter: I,
    predicate: P,
}
```

Filter 本质是一种实现了 `Iterator` trait 的迭代器，其实现 `next` 函数的方法为：

```rust
	fn next(&mut self) -> Option<I::Item> {
        self.iter.find(&mut self.predicate)
    }
```

这就用到了之前提到的 `find` 函数，只有满足 `predicate` 函数条件的item才会被判断为next。

当调用一个迭代器的 `filter` 函数时，由于函数式编程的缓求值特性，并不会立刻筛选出所有符合的元素，而是直接返回一个 `Filter` 类型的实例。

此时的 `Filter` 实例实际可以看成一个缓求值列表 Lazylist, 所有满足 `predicate` 函数的元素都还没有被筛选出来，除非调用 `next` 函数才可以得到第一个满足的元素。而如果调用 `collect` 函数才会将所有元素遍历一遍并找到所有满足条件的元素（其实并不尽然，`collect` 还存在部分优化）。

所以实际上，不管是 `filter` 还是 `map` 调用之后都会得到一个具有迭代器特性的实例，只是该迭代器的 `next` 函数实现各有不同，当多个函数叠加时，比如：

```rust
let v = vec![5, 10, 11, 123];
let filter_map = v.iter().filter(|x| x > &10).map(|x| 2 * x);
```

由于我们看代码的习惯是从左往右，所以往往以为需要经历两遍循环才能得到最终的结果（一遍是filter进行过滤，一遍是遍历filter的结果得到map的结果）。然后实际上，该代码是从右往左“进行”的，当我们调用 filter_map 的 `next` 函数时，由于 filter_map 实际是一个 `Map`

```rust
pub struct Map<I, F> {
    iter: I,
    f: F,
}
```

的实例，其中的 `iter` 成员实际是 `Filter` 类型的实例。因此，`Map` 会首先调用 `iter` 的 `next` 函数，从而达到与下面的代码：

```rust
let v = vec![5, 10, 11, 123];
for num in v.iter() {
    if num > &10 {
        2 * num
    }
}
```

几乎一样的效果。而在结构上更加简洁，逻辑上更加清晰。

### collect 与 FromIterator / IntoIterator

`collect` 函数可将一个迭代器的数据（从迭代器的现有位置起）转换为容器，这要求该容器必须实现了 `FromIterator` trait

`FromIterator` 与 `IntoIterator` 是一对“镜像” trait

```rust
pub trait FromIterator<A>: Sized {
    fn from_iter<T: IntoIterator<Item = A>>(iter: T) -> Self;
}

pub trait IntoIterator {
    type Item;
    type IntoIter: Iterator<Item = Self::Item>;
    fn into_iter(self) -> Self::IntoIter;
}
```

对于可迭代容器，当调用 `into_iter` 之后将得到一个实现了 `Iterator` trait 的类型，该类型的具体实现涉及到容器的特性。比如，`Vec` 的 `IntoIter` 包含了该 `Vec` 的对应内存区域的起始指针、容量、迭代器所在元素的指针等，而 `LinkedList` 则包含了头、尾节点的指针、容量等。从原容器到迭代器，往往需要对内存重新进行解释，往往涉及到 unsafe 代码块。

```rust
	fn collect<B: FromIterator<Self::Item>>(self) -> B
    where
        Self: Sized,
    {
        FromIterator::from_iter(self)
    }
```

`Iterator` trait 内实现了 `collect` 函数，但实际是调用 `from_iter` 函数，该函数由所有实现了 `FromIterator` 的类型进行实现，同样对于不同的数据结构的实现不同，所以 `FromIterator` 内并不提供实现。

### 总结

Rust 实现迭代器的操作实际上是通过旧迭代器生成新的迭代器来延迟实现的，新迭代器的特性体现在其对于 `next` 函数的实现上。

