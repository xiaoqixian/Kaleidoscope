### **Mathematical Formula**

1. Taylor expansion
   $$
   g(x) = g(x_0) + \sum_{k = 1}^{n}\frac{f^k(x-x_0)^k}{k!}(x-x_0)^k + R_n(x)
   $$
   $R_n(x)$ refers to the Lagrange remainder, which is
   $$
   R_n(x) = \frac{f^{n+1}(\xi)}{(n+1)!}(x-x_0)^{n+1}
   $$
   
   Lagrange remainder is derived from Cauchy mean value theorem.
   
2. Cauchy mean value theorem

   Between a and b always exits a $\xi\in(a,b)$ to make
   $$
   \frac{f(b) - f(a)}{g(b) - g(b)} = \frac{f^{'}(\xi)}{g^{'}(\xi)}
   $$
   true.
   
3. Why all the functions represent to the sum of the odd and even functions?

   For a regular function $f(x)$
   $$
   f(x) = \frac{f(x) + f(-x)}{2} + \frac{f(x)-f(-x)}{2}
   $$
   even function on the left and odd function on the right.
   
4. **A method for solving first-order nonlinear differential equations.**

   For a regular first-order nonlinear differential equation
   $$
   \frac{dy}{dx} + P(x)y = Q(x)\tag{1}
   $$
   Let $y = u\cdot v$, $u$ and $v$ are both functions about $x$, so we get
   $$
   \frac{dy}{dx} = v\frac{du}{dx} + u\frac{dv}{dx}
   $$
   Then the differential equation become
   $$
   \frac{du}{dx}\cdot v + u\cdot\left(\frac{dv}{dx} + P(x)\cdot v \right) = Q(x)\tag{2}
   $$
   We want solve the $v$ to make the formula inside the parenthesis to be zero, that is
   $$
   \frac{dv}{dx} + P(x)\cdot v = 0
   $$
   This is a first order linear differential equation, it's general solution is
   $$
   v = C_1e^{-\int P(x)dx}\tag{3}
   $$
   Let's substitute v into the formula (2), we get
   $$
   \frac{du}{dx}\cdot C_1e^{-\int P(x)dx} = Q(x)\tag{4}
   $$
   This is a linear differential equation, we can easily solve it, the general solution of $u$ is
   $$
   u = \frac1{C_1}\int Q(x)\cdot e^{\int P(x)dx}dx + C_2
   $$
   So our target $y$ is
   $$
   y = u\cdot v = \left[\int e^{(\int P(x)dx)}\cdot Q(x)\cdot dx + C \right]\cdot e^{(-\int P(x)dx)}
   $$
   



---

#### **Common Antiderivative Formula**

1. $$
   \int \frac x{x^2+a^2}dx = \frac12\ln(x^2+a^2) + C
   $$

2. 