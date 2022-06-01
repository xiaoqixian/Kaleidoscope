# Cpp Template

### Define a template

A template definition starts with the keyword `template` followed by a <font color = red>template parameter list</font>, which is a comma-separated list of one or more template parameters.

For example:

```cpp
template <typename T>
template <typename T, U>
```

Sometimes we can use `class` keyword to replace `typename`, there's no distinction between them.

#### Nontype Template Parameters

A nontype parameter represents a value rather than a type. Nontype parameters are specified by using a specific type name instead of the `typename` keyword.

For example: 

```cpp
template <unsigned N, unsigned M>
int compare(const char (&p1)[N], const char (&p2)[N]) {
    return strcmp(p1, p2);
}
```

#### Template Compilation

When the compiler sees the definition of a template, it does not generate code. It generates code only when we instantiate a specific instance of the template.

#### Class Templates

Defining templates in classes has no much differences to defining templates in functions. Exception when we define member functions with templates outside of a class, the `template <typename T>` declaration is needed as well. So are constructors.

When we define a class without body, the actual typename is no need to be provided cause we don't need to use it. 

For example:

```c++
template <typename>
class Blob; //we just declare a class with template.
```

##### Class Templates and Friends

When a class contains a friend declaration, the class and the friend can independently be templates or not. A class template that has a nontemplate friend grants that friend access to all the instantiations of the template.

##### **Befriending the Template's Own Type Parameter**

Under C++11 standard, we can make a template type parameter a friend;

```c++
template <typename Type>
class Bar {
    friend Type;
}
```

Here we stay that whatever type is used to instantiate Bar is a friend.

##### Template Type Aliases

C++11 lets us define a type alias for a class template:

```c++
template <typename T>
using twin = pair<T, T>;

twin<string> authors;
```

Also we can fix one or more of the template parameters:

```c++
template <typename T>
using partNo = pair<T, unsigned>;

partNo<string> books;
```

##### Using Class Members That Are Types

Recall that we use scope operator (::) to access both static members and type members. In ordinary code, the compiler has access to the class definition. As as result, it knows whether a name accessed through the scope operator is a type or a static member. 

Assuming T is a template type parameter, when the compiler sees code such as T::mem it won't know until instantiation time whether mem is a type or a static member. By default, the compiler assumes that a name accessed through the scope operator is not a type. Therefore, if we need to access a type, we need to explicitly tell the compiler that it's a type. We do so by using the keyword `typename`.

For example:

```c++
template <typename T>
typename T::value_type func(const T& c) {
    ...
}
```

#### Default Template Parameters

Just as we can supply default arguments to function parameters, we can also supply **default template parameters**.

For example:

```c++
template <typename T, typename F = Less<T>>
int compare(const T& v1, const T& v2, F f = F()) {
    if (f(v1, v2)) return -1;
    if (f(v2, v1)) return 1;
    return 0;
}
```

There's also default template parameters for classes, if a class template provides default arguments for all of its template parameters, and we want to use those parameters, we must put an empty bracket pair following the template's name:

```c++
template <typename T = int>
class Numbers;

Numbers<> num;
```

#### Controlling Instantiations 

The fact that instantiations are generated when a template is used means that the same instantiation may appear in multiple object files. In large systems, the overhead of instantiating the same template in multiple files can become significant.

When the compiler sees an extern template declaration, it will not generate code for that instantiation in the file. Declaring an instantiation as extern is a promise that there will be a nonextern use of that instantiation elsewhere in that program.

```c++
extern template class Blob<string>;
```

When the compiler sees an instantiation definition, it generates code.

```cpp
template class Blob<string>;
```

### Template Argument Deduction

