## C++11 new features

### 语法糖

#### auto 自动类型推导

可用于推导函数返回值或迭代类型，需要注意的是除了类型信息，其它信息可能会丢失，比如：

1. 指向类型为引用时，推导类型会丢失引用。如果要避免，可手动添加 & 符号避免丢失
2. const/volatile 符会丢失，如果要避免，可手动添加对应 cv 符。但是，在auto 与引用或指针符号结合时，对应的 cv 属性会得到保留。

#### decltype 关键字

decltype 用于推导一个表达式的类型，并且不会像 auto 一样丢失引用和 cv 限定符。

推导规则：

1. exp 是标识符、类访问表达式，decltype(exp) 和 exp 的类型一致
2. exp 是函数调用，decltype(exp) 和返回值的类型一致
3. 带括号的表达式和加法运算表达式（其他情况）

#### auto 结合 decltype

对于返回值类型与参数类型相关的模板函数，返回类型通常需要使用 decltype 进行类型推导。一般则需要写成：

```c++
template <typename T, typename U>
decltype((*(T*)0) + (*(U*)0)) add(T t, U u) {
    return t + u;
}
```

这样显得非常晦涩，因此 C++ 加入了后置类型推导。

```c++
template <typename T, typename U>
auto add(T t, U u) -> decltype(t + u) {
    return t + u;
}
```

甚至，可以直接使用函数返回值类型作为后置类型推导。

```c++
int& foo(int& i);
float& foo(float& f);

template <typename T>
auto func(T& val) -> decltype(foo(val)) {
    return foo(val);
}
```

#### 通过 using 重定义模板

对于接受多个模板的类型而言，如果想要将其中某个类型具化，通过 typedef 无法做到，则可以通过 using 定义一个新的类型。

```c++
template <typename T>
using str_map_t = std::map<std::string, T>;
```

#### 函数模板的默认模板参数

C++11 取消了对于函数模板的默认模板参数的限制，当所有模板都有默认参数时，函数调用与普通函数一致，这点与类模板不一样。

#### 列表初始化

C++11中定义了可通过列表初始化的方式来初始化一些结构体，这种方式适用于聚合体类型，聚合体类型定义：

1. 类型是一个普通数组
2. 类型是一个类(class, struct, union)，且
   - 无自定义构造函数
   - 无私有或保护的非静态数据成员
   - 无基类
   - 无虚函数
   - 不能有 {} 和 = 直接初始化的非静态数据成员

C++ 的stl 容器支持通过 {1,2,3,..} 的方式进行初始化，但是对于自定义容器却不行。现在可以通过 std::initializer_list 来进行初始化，只需要提供一个接受 std::initializer_list 类型参数的构造函数即可。比如：

```c++
class FooVector {
    std::vector<int> _v;
    
public:
    FooVector(std::initializer_list<int> list) {
        for (auto it = list.begin(); it != list.end(); list++)
            _v.push_back(*it);
    }
}
```

总之，std::initializer_list 可用于一次性传递同类型的多个数据，其内部保存的是所持有对象的引用。

#### std::function 和 bind 绑定器

std::function 接受一个函数签名作为模板参数可代表一个可调用对象类型。比如

```c++
int func(int) {
    return -1;
}

#include <functional>
int main() {
    std::function<int(int)> f = func;
}
```

std::bind 可接受一个可调用对象与占位符生成一个新的可调用对象。比如如果要生成一个将函数的两个参数调换的可调用对象，或者只暂时传入一个参数以达到函数式编程中偏特化的效果：

```c++
void func(int a, int b) {
    std::cout << "a = " << a << ", b = " << b << std::endl;
}

int main() {
    auto switch_param = std::bind(func, std::placeholders::_2, std::placeholders::_1);
    switch_param(1, 2);

    auto partial_spec = std::bind(func, 1, std::placeholders::_1);
    partial_spec(2);
}
```

注意，占位符 std::placeholders 对应的是生成的可调用对象调用时的参数位置。

#### lambda 表达式

C++11中lambda 表达式的语法形式为：

[ capture ] (parames) opt -> ret {body;}

capture 为捕获列表，params 为参数列表，opt 为函数选项，ret 为返回值。

当返回值非常明显时，可以省略写返回值，但是初始化列表不在此列。当无参数时，参数列表可以省略。

捕获变量：

- [] 不捕获任何变量
- [&] 捕获外部作用域所有变量，并作为引用在函数中使用
- [=] 捕获外部作用域所有变量，并作为值在函数中使用
- [=, &foo] 按值捕获所有变量，按引用捕获 foo 变量
- [bar] 按值捕获 bar 变量，同时不捕获其他变量
- [this] 捕获当前类的 this 指针，让 lambda 表达式拥有和当前类成员函数同样的访问权限。

需要注意的是按值捕获时，在lambda表达式的瞬间，值就已经复制到了表达式中，之后值改变，但是表达式依然不受影响。

如果需要对外界变量进行修改，则需要使用 mutable 为函数选项，此时即使没有参数，也需要写出参数列表。

lambda 表达式同样是可调用对象，可以作为 std::function 类型变量的值。

#### tuple 元组

tuple 元组是一个固定大小的**不同类型**值的集合，可通过 std::make_tuple 创建，元组值可以通过 get\<index\>() 函数获取，或者通过 std::tie 进行解包，不需要解包的变量通过 std::ignore 忽略。

可以通过 std::tie 创建左值引用的元组，std::forward_as_tuple 创建右值引用的元组。

### 内存优化

#### 右值引用

1. 左值和右值是独立于它们的类型的，右值引用类型可能是左值也可能是右值。
2. auto&& 或函数参数类型自动推导的 T&& 是一个未定的引用类型，被称为 universal references, 它可能是左值引用也可能是右值引用类型，取决于初始化值的类型。
3. 所有的右值引用叠加到右值引用上仍然是一个右值引用，其他引用折叠都为左值引用。当 T&& 为模板参数时，输入左值，它会变成左值引用，而输入右值引用时会变为具名的右值引用。
4. 编译器会将已经命名的右值引用视为作为左值。

#### move 语义

move 语义可以将一个左值强制转换为右值，以避免一些不必要的拷贝。move 语义通过 std::move 函数实现。

#### forward 和 完美转发

当右值引用作为函数的形参传入函数时，由于其已经被命名，因此被看作一个左值。如果需要保留原来的类型以转发到另一个函数，这种转发称为完美转发（Perfect Forwarding）。

完美转发通过函数 std::forward\<T\> 函数实现，其接受一个模板参数。如果模板参数类型并非引用类型，则其等同于 std::move 函数。

#### emplace_back 减少内存拷贝和移动

emplace_back 能就地通过参数构造对象，不需要拷贝或移动内存，应该尽量考虑用 emplace_back 来代替 push_back，除非对应的类型并没有提供相应的构造函数。

### 泛型编程

#### type_traits——类型萃取

1. 生成编译期常量—— std::integral_constant 类型，可通过常量成员变量 value 获取对应的值。

2. 通过 std::is_const 类型判断是否是某个类型，一般配合模板使用。在不知道模板类型的情况下，可通过一些结构体判断是否是某个类型，对应的结果可通过常量成员变量 value 获取。

   比如，判断是否是 int 类型

   ```c++
   std::cout << "int: " << std::is_const<int>::value << std::endl;
   ```

3. 判断两个类型之间的关系。

   |                      traits 类型                      |          说明           |
   | :---------------------------------------------------: | :---------------------: |
   |      template<class T, class U> struct is_same;       |  判断两个类型是否相同   |
   |     template<class T, class U> struct is_base_of;     | 判断 T 是否为 U 的基类  |
   | template<class From, class To> struct is_convertible; | 判断 From 能否转换为 To |

4. 类型转换的 traits

   常用的类型转换的 trait 包括对于 const 的添加和删除、引用的添加和删除、数组的修改和指针的修改。

5. 根据条件选择的 traits

   std::conditional 可根据一个判断式选择两个类型中的一个，显然该判断式必须是编译期已知的常量。选择出的类型可通过类型成员变量 type 获取，注意前面要加 typedef 表明这是类型。

6. 获取可调用对象返回类型的 traits

   std::result_of 可在编译期获取一个可调用对象的返回类型

   ```c++
   int fn(int) {return int();}
   
   typedef int(&fn_ref)(int);
   typedef int(*fn_ptr)(int);
   
   struct fn_class {
       int operator()(int i) {
           return i;
       }
   };
   
   int main() {
       typedef std::result_of<decltype(fn)&(int)>::type A;
       typedef std::result_of<fn_ref(int)>::type B;
       typedef std::result_of<fn_ptr(int)>::type C;
       typedef std::result_of<fn_class(int)>::type D;
   
       std::cout << "A: " << std::is_same<int, A>::value << std::endl;
       std::cout << "B: " << std::is_same<int, B>::value << std::endl;
       std::cout << "C: " << std::is_same<int, C>::value << std::endl;
       std::cout << "D: " << std::is_same<int, D>::value << std::endl;
   
       return 0;
   }
   ```

7. 根据条件禁用或启用某种或某些类型的 traits

   SFINAE(substitution-failure-is-not-an-error) 原则：当进行模板匹配时，如果匹配到不合适的模板并不会报错，而是匹配其他的重载函数。

   std::enable_if 利用 SFINAE 实现根据条件选择重载函数，其原型如下：

   ```c++
   template <bool B, class T = void>
   struct enable_if;
   ```

   基本用法如下：

   ```c++
   template <typename T>
   typename std::enable_if<std::is_arithmetic<T>::value, T>::type foo(T t) {
       return t;
   }
   ```

   上述表明只有在 T 为整数或浮点数时才会被重载。

   其还可以用于对于模板的入参类型进行限定

   ```c++
   template <typename T>
   T foo(T t, typename std::enable_if<std::is_integral<T>::value, int>::type = 0) {
       return t;
   }
   ```

   还可以用于对不同返回值类型的函数进行重载

   ```c++
   template <typename T>
   typename std::enable_if<std::is_arithmetic<T>::value>::type foo(T t) {
       cout << typeid(T).name() << endl;
   }
   
   template <typename T>
   typename std::enable_if<std::is_same<T, std::string>::value>::type foo(T t) {
       cout << typeid(T).name() << endl;
   }
   ```

#### 可变参数模板

定义如下：

```c++
template <typename... T>
void f(T... args) {
    cout << sizeof...(args) << endl;
}
```

可以通过递归的方式展开参数包，传入一个固定参数和可变参数，递归调用时只传入可变参数包，由于固定参数被优先填充，因此可变参数相当于减少一个，从而达到展开参数包的目的。最后会没有一个参数，因此需要再写一个无参的重载。

```c++
template <typename T, typename... Args>
void print(T head, Args... rest) {
    cout << "Parameter " << head << endl;
    print(rest...);
}

void print() {
    cout << "no parameter" << endl;
}
```

也可以通过逗号表达式来展开参数包

```c++
template <typename T>
void printArg(T t) {
    cout << t << endl;
}

template <typename... Args>
void expand(Args... args) {
    std::initlializer_list<int>{(printArg(args), 0)...};
}
```

可变参数模板类的参数包展开的方式和可变参数模板函数的展开方式不同，需要通过模板特化或继承方式去展开。

```c++
template<int...>
struct IndexSeq {};

template<int N, int... Indexes>
struct MakeIndexes: MakeIndexes<N-1, N-1, Indexes...> {};

//当N-1=0时的偏特化情况
template<int... Indexes>
struct MakeIndexes<0, Indexes...> {
    typedef IndexSeq<Indexes...> type;
};
```

也可以不通过继承方式实现

```c++
template<int...>
struct IndexSeq {};

template<int N, int... Indexes>
struct MakeIndexes {
    using type = MakeIndexes<N-1, N-1, Indexes...>::type;
};

template<int... Indexes>
struct MakeIndexes<0, Indexes...> {
    using type = IndexSeq<Indexes...>;
};
```

#### 可变参数模板和 type_traits 的综合应用

实现函数式编程中的链式调用

```c++
template<typename T>
class Task;

template<typename Ret, typename... Args>
class Task<Ret(Args...)> {
private:
    std::function<Ret(Args...)> fn;
public:
    Task(std::function<Ret(Args...)>&& f): fn(std::move(f)) {}
    Task(std::function<Ret(Args...)>& f): fn(f) {}

    Ret invoke(Args&&... args) {
        return this->fn(std::forward<Args>(args)...);
    }

    template<typename Fn>
    auto then(Fn&& f) -> Task<typename std::result_of<Fn(Ret)>::type(Args...)> {
        using return_type = typename std::result_of<Fn(Ret)>::type;
        auto func = std::move(this->fn);

        return Task<return_type(Args...)>([func, &f](Args&&... args) {
            return f(func(std::forward<Args>(args)...));
        });
    }
};
```

调用 then 函数时，将执行本 task 的函数并将结果作为参数传入下一个函数中，并返回一个新的 task

##### 实现 any 类

主要在于通过一对基类和子类分别擦除和保存值的类型，基类为非泛型类，其类型的指针保存在 Any 类中，相当于 Any 不保存值的类型。但是其子类为模板类，在创建时需要指定保存的值的类型。在需要取出值时，传入取出的类型，通过 dynamic_cast 将基类的指针转换为子类，并取出对应的值。从而实现了值类型的擦除和恢复。

```c++
struct Any {
    Any(void): m_tpIndex(std::type_index(typeid(void))) {std::cout << "call default constructor" << std::endl;}
    Any(Any& that): m_ptr(that.clone()), m_tpIndex(that.m_tpIndex) {}
    Any(Any&& that): m_ptr(std::move(that.m_ptr)), m_tpIndex(that.m_tpIndex) {}

    // use std::decay to remove reference and cv modifier and get the original type
    // `typename =` equals to `typename T =`, as T is not used, so it can be omitted.
    template <typename U, typename = typename std::enable_if<!std::is_same<typename std::decay<U>::type, Any>::value, U>::type> 
    Any(U&& value): m_ptr(new Derived<typename std::decay<U>::type>(std::forward<U>(value))), m_tpIndex(std::type_index(typeid(typename std::decay<U>::type))) {
        std::cout << "call rvalue constructor" << std::endl;
    }

    bool isNull() const {
        return !bool(m_ptr);
    }

    template <class U> bool Is() const {
        return m_tpIndex == std::type_index(typeid(U));
    }

    // transform U into the actual type
    template <class U>
    U& AnyCast() {
        if (!Is<U>()) {
            std::cout << "can not cast " << typeid(U).name() << " to " << m_tpIndex.name() << std::endl;
        }

        auto derived = dynamic_cast<Derived<U>*> (m_ptr.get());
        return derived->m_value;
    }

    Any& operator=(const Any& a) {
        std::cout << "call operator = " << std::endl;
        if (m_ptr == a.m_ptr) {
            return *this;
        }
        m_ptr = a.clone();
        m_tpIndex = a.m_tpIndex;
        return *this;
    }

private:
    struct Base;
    typedef std::unique_ptr<Base> BasePtr;

    struct Base {
        virtual ~Base() {}
        virtual BasePtr clone() const = 0;
    };

    template <typename T>
    struct Derived: Base {
        template <typename U>
        Derived(U&& value): m_value(std::forward<U>(value)) {}

        BasePtr clone() const {
            return BasePtr(new Derived<T>(this->m_value));
        }

        T m_value;
    };

    BasePtr clone() const {
        if (m_ptr != nullptr) {
            return m_ptr->clone();
        }
        return nullptr;
    }

    BasePtr m_ptr;
    std::type_index m_tpIndex;
};

int main() {
    Any n;
    auto r = n.isNull();
    std::cout << "auto r" << std::endl;
    double d = 1.3;
    n = d;
    std::cout << n.Is<double>() << std::endl;
    return 0;
}
```

#### 实现 function_traits

通过 function_traits 可以获取函数的一些基本信息，包括函数类型、返回类型、参数个数和参数类型。

```c++
template<typename T>
class function_traits;

template<typename Ret, typename... Args>
class function_traits<Ret(Args...)> {
public:
    enum { arity = sizeof...(Args) };
    typedef Ret function_type(Args...);
    typedef Ret return_type;

    using stl_function_type = std::function<function_type>;
    typedef Ret(*pointer)(Args...);

    template<size_t I>
    struct args {
        static_assert(I < arity, "index is out of range");
        // Provides compile-time indexed access to the types of the elements of the tuple
        using type = typename std::tuple_element<I, std::tuple<Args...>>::type;
    };
};

#include <iostream>
int main() {
    int func(int a, float b);

    std::cout << std::is_same<function_traits<decltype(func)>::return_type, int>::value << std::endl;

    std::cout << (function_traits<decltype(func)>::arity == 2) << std::endl;
}
```

#### 实现 variant

variant 类似于 Any，能够代表定义的多种类型，允许赋不同类型的值给它，类型会被擦除，在取出时再重新确定。

```c++
typedef variant<int, char, double> vt;
vt v = 1;
v = '2';
v = 12.32;
```

主要实现方法是通过内存对齐的缓冲区 std::aligned_storage 记录数据，通过 type_index 确定类型。

要设立缓冲区首先显然需要确定所有类型中最大的一个，某个类型内存对齐后的大小可以由 std::alignment_of\<T\>::value 确定，因此需要创建一个结构体可以从多个编译期常量中选出最大的一个，这需要前面提到的继承方式来展开可变模板参数包的方式来完成。

```c++
template <std::size_t arg, std::size_t... rest>
struct IntegerMax;

template <std::size_t arg>
struct IntegerMax<arg>: std::integral_constant<std::size_t, arg> {};

template <std::size_t arg1, std::size_t arg2, std::size_t... rest>
struct IntegerMax<arg1, arg2, rest...>: std::integral_constant<std::size_t, arg1 <= arg2 ? 
    IntegerMax<arg2, rest...>::value : IntegerMax<arg1, rest...>::value> {};

template <typename... TypeList>
struct MaxAlign: std::integral_constant<std::size_t, IntegerMax<std::alignment_of<TypeList>::value...>::value> {};
```

其次，variant 可以赋值的类型应当是变量在创建时就已经确定的，在进行二次赋值时需要判断是否在候选范围内，如果不再则抛出异常。因此，需要创建一个结构体用于判断某个类型是否在一个类型列表中。

```c++
// if List contains type T
template <typename T, typename... List>
struct Contains;

template <typename T, typename Head, typename... Rest>
struct Contains<T, Head, Rest...>: std::conditional<std::is_same<T, Head>::value, std::true_type, Contains<T, Rest...>>::type {};

//end recursion
template <typename T>
struct Contains<T>: std::false_type {};
```

完整程序如下：

```c++
// select max aligned type size
template <std::size_t arg, std::size_t... rest>
struct IntegerMax;

template <std::size_t arg>
struct IntegerMax<arg>: std::integral_constant<std::size_t, arg> {};

template <std::size_t arg1, std::size_t arg2, std::size_t... rest>
struct IntegerMax<arg1, arg2, rest...>: std::integral_constant<std::size_t, arg1 <= arg2 ? 
    IntegerMax<arg2, rest...>::value : IntegerMax<arg1, rest...>::value> {};

template <typename... TypeList>
struct MaxAlign: std::integral_constant<std::size_t, IntegerMax<std::alignment_of<TypeList>::value...>::value> {};

// if List contains type T
template <typename T, typename... List>
struct Contains;

template <typename T, typename Head, typename... Rest>
struct Contains<T, Head, Rest...>: std::conditional<std::is_same<T, Head>::value, std::true_type, Contains<T, Rest...>>::type {};

//end recursion
template <typename T>
struct Contains<T>: std::false_type {};

template <typename... Types>
struct Variant {
    enum {
        data_size = IntegerMax<sizeof(Types)...>::value,
        align_size = MaxAlign<Types...>::value
    };

    using data_t = typename std::aligned_storage<data_size, align_size>::type;
private:
    data_t _data;
    std::type_index _type_index;

    template <typename T>
    void destory_as(const std::type_index& id, void* data) {
        if (id == std::type_index(typeid(T))) {
            reinterpret_cast<T*>(data)->~T();
        }
    }

    void destory(const std::type_index& id, void* buffer) {
        [](Types&&...){}((destory_as<Types>(id, buffer), 0)...);
    }

    template <typename T>
    void move_as(const std::type_index& id, void* old_v, void* new_v) {
        if (id == std::type_index(typeid(T))) {
            new (new_v)T(std::move(*reinterpret_cast<T*>(old_v)));
        }
    }

    void move(const std::type_index& id, void* old_v, void* new_v) {
        [](Types&&...){}((move_as<Types>(id, old_v, new_v), 0)...);
    }

    template <typename T>
    void copy_as(const std::type_index& id, const void* old_v, void* new_v) {
        if (id == std::type_index(typeid(T))) {
            new (new_v)T(reinterpret_cast<T*>(old_v));
        }
    }

    void copy(const std::type_index& id, const void* old_v, void* new_v) {
        [](Types...){}((copy_as<Types>(id, old_v, new_v), 0)...);
    }

public:
    Variant(void): _type_index(std::type_index(typeid(void))) {}

    ~Variant() {
        this->destory(this->_type_index, &this->_data);
    }

    Variant(Variant<Types...>&& old): _type_index(old._type_index) {
        this->move(old._type_index, &old._data, &this->_data);
    }

    Variant(Variant<Types...>& old): _type_index(old._type_index) {
        this->copy(old._type_index, &old._data, &this->_data);
    }

    Variant& operator=(const Variant& old) {
        this->copy(old._type_index, &old._data, &this->_data);
        this->_type_index = old._type_index;
        return *this;
    }

    Variant& operator=(Variant&& old) {
        this->move(old._type_index, &old._data, &this->_data);
        this->_type_index = old._type_index;
        return *this;
    }

    template <typename T, typename = typename std::enable_if<Contains<typename std::decay<T>::type, Types...>::value>::type>
    Variant(T&& value): _type_index(typeid(void)) {
        std::cout << "reassignd to type " << typeid(T).name()  << std::endl;
        this->destory(this->_type_index, &this->_data);
        typedef typename std::decay<T>::type U;
        new (&this->_data)U(std::forward<T>(value));
        this->_type_index = std::type_index(typeid(U));
    }

    template <typename T>
    bool is() const {
        return this->_type_index == std::type_index(typeid(T));
    }

    bool empty() const {
        return this->_type_index == std::type_index(typeid(void));
    }

    std::type_index type() const {
        return this->_type_index;
    }

    template <typename T>
    typename std::decay<T>::type get() {
        using U = typename std::decay<T>::type;
        if (!this->is<U>()) {
            std::cout << typeid(U).name() << " is not defined. current type is"
                << this->_type_index.name() << std::endl;
            throw std::bad_cast{};
        }

        return *(U*)(&this->_data);
    }
};
```



