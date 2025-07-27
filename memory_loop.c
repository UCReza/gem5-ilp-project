#include <stdio.h>
#include <stdlib.h>
#define ITERS 1000000
#define NLOG2 18
int main(void){
    const long N = 1L<<NLOG2;
    int *arr = (int*)malloc(sizeof(int)*N);
    if(!arr) return 1;
    for(long i=0;i<N;i++) arr[i]=i;
    volatile long idx=0,sum=0;
    for(long i=0;i<ITERS;i++){
        idx = (idx + arr[idx & (N-1)]) & (N-1);
        sum += arr[idx];
    }
    printf("%ld\n", sum);
    free((void*)arr);
    return 0;
}
