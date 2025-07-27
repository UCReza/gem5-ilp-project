#include <stdio.h>
#define ITERS 1000000
int main(void){
    volatile long sum=0;
    for (long i=0;i<ITERS;i++){ if((i&255)==0) sum+=i; else sum-=1; }
    printf("%ld\n", sum);
    return 0;
}
