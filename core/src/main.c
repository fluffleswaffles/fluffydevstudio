#include "fluffy.h"

void setup() {
    fluffy_init();
    // do once
}

void loop() {
    // do forever
}

int main(void) {
    setup();
    while(1) {
        loop();
    }
    return 0;
}