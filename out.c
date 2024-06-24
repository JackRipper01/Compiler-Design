#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

int main() {
    //let a = 5,b=a+4 in print(a + b);
    //let a=5 in let b=a+4 in print(a+b);
    float let(float a)
    {
        float let(float b)
        {
        printf("%f\n", a+b);
        }
        let(a+4);
    }
    let(5);
    return 0;
}

