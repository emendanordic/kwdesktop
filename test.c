
#include "test.h"

int foo() {
    int *ptr;
    *ptr = 0;

    return;
}

    void goo() {
        foo();
    }
