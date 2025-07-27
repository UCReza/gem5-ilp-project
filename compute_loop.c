#include <stdio.h>
#define ITERS 1000000
int main(void){
    volatile long a=1,b=2,c=3,d=4,e=5,f=6;
    for (long i=0;i<ITERS;i++){ a+=b; c+=d; e+=f; b+=3; d+=5; f+=7; }
    printf("%ld\n", a+c+e+b+d+f);
    return 0;
}
