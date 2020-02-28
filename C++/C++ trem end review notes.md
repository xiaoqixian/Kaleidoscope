#### C++ trem end review notes

1. Function

* Two ways to change the actual arugments:reference arguements & pointer arguments.

```c++
//definet a function using reference arguments
void swap1(int &x,int &y);

//definet a function using pointer arguments
void swap2(int *x,int *y);

//invoke functions
int main() {
    int x = 1, y = 2;
    swap1(x, y);
    swap2(&x, &y);
    return 0;
}
```

* constant pointer:where constant pointer points at can be changed,but what it points at can not be changed.
* when the arguments are arrays,the actual arugments and the reference arguments share a same memory area.
* function scope:
  * anto variable:starts when it's defined,end at the end of the function.
  * static local variable:starts when it's defined,end at the end of the function.But it does not get recycled until the program is terminated.It only get initialized at compile time.
  * global variable

2. Struct

* Structure types themselves do not take up storage space; only structure variables allocate space.

* produce a linkedlist node variable:

  ```c
  struct node {
      int data;
      struct node *next;
  } *p;
  ```

  

  * by malloc in c

  ```c
  //notice the *
  p = (struct node *) malloc(sizeof(node));
  
  //to release the variable space
  free(p);
  ```

  * by new in c++

  ```c++
  p = new node;
  
  delete p;
  ```


3. Class

* Constructor

  1.Constructor is used to initialnize the member variables of the class.

  2.It can either implemented inside the class or outside the class.

  3.can be overloaded.

  4.The system will construct a default constructor when there is no constructor at all.

  5.All the members and variables of a static object will be initialnized as NULL or 0.

* Destrutor

  1.The destructor add a ~ in front of the destructor's name to differ from construtor.

  2.can **not** be overloaded.

  3.A destructor has no arguments.

  4.Destructor can both be called by program and by system.When the program does not call the destructor,system will do it.

* Copy initialization constructor

  1.It has only one argument which is the reference of another object.

  2.When there is no copy initialization constructor is implenmented,the complier will set a default one and pass all of the already known variables to it.

  For example:

  ```c++
  class Circle {
  	private:
  		int x,y;
  		
  	public:
  		Circle(int x,int y){
  			this->x = x;
  			this->y = y;
  		}
  		print(){
  			cout << x << ' ' << y << endl;
  		}
  }; 
  
  int main()
  {
  	Circle c1(1,2),c2(c1);
  	c2.print();
  	return 0;
  }
  ```

  In this code block, c2, the object, has same x and same y as c1 which means this two numbers are passed.

* Constant function

  1.only constant functions are allowed to operate constant objects.

* Constant member

  1.not allowed to be modified.

  2.Initialization list is where constant variables get initialized.

  ```c++
  class Decrement{
      private: 
      	int x;
      	const int y;
      public:
      	Decrement(int x,int y):this->y(y) {
              this->x = x;
          }
  }
  ```

* Static member

  1. static data
     * static data belongs to the class instead of objects.
     * static data is initialized outside of the class.
     * referred as <class name>::<static member name>.
  2. static function
     * static functions are able to directly refer static data.But non static data is not allowed.

* friend function

  * friend function is not a member function but is able to use private members.