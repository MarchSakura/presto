#include <stdio.h>

int main() {
    #if __AVX512F__
    printf("avx512 yyds~\n");
    #else
    printf("no avx512 support =_=\n");
    #endif
    return 0;
}
