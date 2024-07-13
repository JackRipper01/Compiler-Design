CODE = r"""function tan(x: Number): Number => sin(x) / cos(x);
function cot(x:Number):Number => 1 / tan(x);
function operate(x:Number, y:Number) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
}
function fib(n:Number):Number => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);
function fact(x:Number):Number => let f = 1 in for (i in range(1, x+1)) f := f * i;
function gcd(a:Number, b:Number) => while (a > 0)
        let m = a % b in {
            b := a;
            a := m;
        };
protocol Hashable {
    hash(): Number;
}
protocol Equatable extends Hashable {
    equals(other: Object): Boolean;
}

type Point(x: Number,y:Number) {
    x = x;
    y = y;

    getX() : Number => self.x;
    getY():Number => self.y;

    setX(x:Number) :Number => self.x := x;
    setY(y:Number):Number => self.y := y;
}
type PolarPoint(phi:Number, rho:Number) inherits Point(rho * sin(phi), rho * cos(phi)) {
    rho() :Number => sqrt(self.getX() ^ 2 + self.getY() ^ 2);
}
type Knight inherits Person {
    name():String => "Sir"; //candela
}
type Person(firstname:String, lastname:String) {
    firstname = firstname;
    lastname = lastname;

    name():String => self.firstname @@ self.lastname;
    hash() : Number {
        5;
    }
}
type Superman {
}
type Bird {
}
type Plane {
}
type A {
    hello() => print("A");
}

type B inherits A {
    hello() => print("B");
}

type C inherits A {
    hello() => print("C");
}

{
    42;
    print(42);
    print((((1 + 2) ^ 3) * 4) / 5);
    print("Hello World");
    print("The message is \"Hello World\"");
    print("The meaning of life is " @ 42);
    print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));
    {
        print(42);
        print(sin(PI/2));
        print("Hello World");
    }


    print(tan(PI) ** 2 + cot(PI) ** 2);

    let msg = "Hello World" in print(msg);
    let number = 42, text = "The meaning of life is" in
        print(text @ number);
    let number = 42 in
        let text = "The meaning of life is" in
            print(text @ number);
    let number = 42 in (
        let text = "The meaning of life is" in (
                print(text @ number)
            )
        );
    let a = 6, b = a * 7 in print(b);
    let a = 6 in
        let b = a * 7 in
            print(b);
    let a = 5, b = 10, c = 20 in {
        print(a+b);
        print(b*c);
        print(c/a);
    };
    let a = (let b = 6 in b * 7) in print(a);
    print(let b = 6 in b * 7);
    let a = 20 in {
        let a = 42 in print(a);
        print(a);
    };
    let a = 7, a = 7 * 6 in print(a);
    let a = 7 in
        let a = 7 * 6 in
            print(a);
    let a = 0 in {
        print(a);
        a := 1;
        print(a);
    };
    let a = 0 in
        let b = a := 1 in {
            print(a);
            print(b);
        };
    let a = 42 in if (a % 2 == 0) print("Even") else print("odd");
    let a = 42 in print(if (a % 2 == 0) "even" else "odd");
    let a = 42 in
        if (a % 2 == 0) {
            print(a);
            print("Even");
        }
        else print("Odd");
    let a = 42, mod = a % 3 in // error
        print(
            if (mod == 0) "Magic"
            elif (mod % 3 == 1) "Woke"
            else "Dumb"
        );
    let a = 10 in while (a >= 0) {
        print(a);
        a := a - 1;
    }
    
    for (x in range(0, 10)) print(x);
    let iterable = range(0, 10) in
        while (iterable.next())
            let x = iterable.current() in
                print(x);

    let pt = new Point(3,4) in
        print("x: " @ pt.getX() @ "; y: " @ pt.getY());
    let pt = new PolarPoint(3,4) in
        print("rho: " @ pt.rho());

    let p = new Knight("Phil", "Collins") in
        print(p.name());
    let p: Person = new Knight("Phil", "Collins") in print(p.name());
    let x: Number = 42 in print(x);

    let x = new Superman() in
        print(
            if (x is Bird) "It's bird!"
            elif (x is Plane) "It's a plane!"
            else "No, it's Superman!"
        );
    let x = 42 in print(x);
    let total = { print("Total"); 5; } + 6 in print(total);
    let x : A = if (rand() < 0.5) new B() else new C() in
        if (x is B)
            let y : B = x as B in {
                y.hello();
            }
        else {
            print("x cannot be downcasted to B");
        };

}
"""