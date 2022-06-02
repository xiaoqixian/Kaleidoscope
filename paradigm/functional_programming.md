Functional Programming in Rust

### Shift

命令式编程(Imperative Programming) 与函数式编程(Functional Programming) 一个比较大的区别就是在循环处理上的区别。

编程里最常见的一个场景就是对于一个可迭代的容器（container），我们需要对这些变量进行一次遍历，选择性地对于部分变量进行一些处理。在命令式编程中，会直接使用一个for循环迭代所有变量，然后通过if语句来判断是否需要对当前迭代变量进行处理。

在函数式编程中则完全不是这样，在函数式编程中，则是通过一些非常标准化、流程化的操作来完成这些工作，具有非常高度的抽象性。

#### filter

filter 从字面意义上理解则是从容器中筛选一些变量作为接下来数据处理的候选，其接受一个实现了 `FnMut(&Self::Item) -> bool` trait 的类型，作为变量是否满足的判断依据。

比如，如果需要在一个 `Vec<int>` 变量中筛选出所有大于10的变量，根据函数式编程的思想可以这样：

```rust
    let v = vec![5, 10, 11, 123, 20, 4];
    let mut d = v.iter().filter(|x| **x > 10);
    while let Some(p) = d.next() {
        println!("{}", p);
    }
```

#### map

map 则是一种完成映射的操作，其可以根据迭代器中的元素进行某种处理后生成另一个其它类型元素的迭代器，map 函数接受一个实现了 `FnMut(&Self::Item) -> B` trait 的类型变量，`B` 为泛型，可以是任何其它类型变量。

比如，如果需要将一个 `Vec<int>` 类型变量的所有元素转换为 String 类型，则可以直接：

```rust
    let v = vec![5, 10, 11, 123, 20, 4];
	let string_v = v.iter().map(|x| format!("{}", x)).collect::<Vec<String>>();
    println!("{:?}", string_v);
```

通常我们往往需要在 filter 函数后面紧接着调用 map 来实现需求，但是这样往往需要进行两轮迭代，所以函数式编程往往被人诟病低效，因为其为了简洁将命令式编程中一轮迭代就可以完成的任务分成多轮完成从而降低了效率。

在 rust 中还有另一个结合了 filter 和 map 的函数：filter_map, 其接受一个实现了 `FnMut(&Self::Item) -> Option<B>` trait 的类型的参数，该参数需要对传入变量进行判断，如果满足筛选条件，则进行处理后返回 Some，不满足条件则返回 None，而迭代器只返回 Some 值的变量。

比如如果需要将一个 `Vec<int>` 类型的变量的所有大于10 的元素转换为 String 类型，则可以直接：

```rust
    let v = vec![5, 10, 11, 123, 20, 4];
    let mut new_iter = v.iter().filter_map(|x| if *x > 10 {Some(format!("{}", x))} else {None});
    println!("{:?}", string_v);
```

#### fold

fold 表现的抽象为：初始化一个变量（初始值由调用者给定），将该变量与迭代器中的每个变量进行某种操作（操作由调用者给定, 且必须返回一个同类型变量）之后，返回这个变量。

最典型的，对列表进行求和：

```rust
    let v = vec![5, 10, 11, 123, 20, 4];
	let sum = v.iter().fold(0, |acc, x| acc + x);
```

#### reduce

reduce 的操作其实与 fold 的操作部分重合，其表现的抽象为：内部初始化一个变量为迭代器的第一个值，如果迭代器为空则返回 None，之后将该变量与迭代器的所有变量进行一次操作（操作必须返回一个同类型变量）之后返回。其与 fold 操作最大的区别就是不用提供一个初始值，适用于只可能是返回迭代器中的某一个变量的情景。

最典型的，求列表最值：

```rust
    let v = vec![5, 10, 11, 123, 20, 4];
	let sum = v.iter().reduce(|max, x| if max < x {x} else {max});
```

### Cede

#### Currying and Partial Application

当我调用一个函数时，我们可能并不希望一次传入全部参数，可能当前只能获得部分参数的值，这时我们希望能够分阶段传入参数。一般在面向对象编程中，可能需要将该函数封装为一个类，然后将所有参数设为类成员，分阶段赋值最后调用函数。但是在函数式编程中，存在两种不同的方式来完成。

Currying：柯里化，当一个函数被柯里化之后，每次可只传入一个参数，调用之后将返回一个新的函数，新的函数同样只接受一个参数，直到最后函数的所有参数填补完全返回结果。相当于将原本一次性调用的函数拆解成一条链式调用。

Partial Application: 偏应用，当函数被偏应用时，可传入部分参数，返回一个新的函数，当新函数调用时，传入剩余的参数，从而获得结果。

#### 缓求值 Lazy Evaluation

缓求值非常好理解，就是尽可能地延缓表达式的值的求解，直到需要真正使用时才进行求值从而节省计算资源。缓求值其实在命令式编程和函数式编程中都有应用。

这里给出维基中的一个c++的例子：

```c++
struct matrix{
    double values[100][100]  ;
    double* operator[](int i){return values[i];}
};

struct matrix_add {
   mutable struct rowEntry{ 
       double operator [](int k){
           matrix_add* pthis = (matrix_add*)this;
           return (pthis->a)[_currentRow][k] + (pthis->b)[_currentRow][k];
       }
       
       void setRow(int v) {
           _currentRow = v;
       }
   private:
       int _currentRow;
   } _rowEntry;

   matrix_add(matrix & a, matrix & b) : a(a), b(b) { }
   
   rowEntry& operator[](int i) const {
       _rowEntry.setRow(i); 
       return _rowEntry;
   }
private:
    matrix & a;
    matrix  & b;
};

matrix_add operator + (matrix & a, matrix & b) {
    return matrix_add(a, b);
}

int main () {
    matrix A,B;
    A[3][4]=101; B[3][4]=102;
    matrix_add R = A + B;
    int result = R[3][4];
    return 0;
}
```

当两个矩阵相加时，需要将矩阵的每个值都分别相加，但是我们可能并不需要所有的结果，如果在加法部分就将所有的结果计算出来，则浪费了计算资源。因此我们将程序改为只在通过索引读取结果矩阵的值时才计算该值的结果，从而做到了缓求值。

