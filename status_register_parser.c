#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void print_flags(uint32_t hex_value) {
    printf("Flags ativas:\n");

    for (int i = 15; i >= 0; i--) {
        if (hex_value & (1 << i)) {
            switch (i) {
                case 0:
                    printf("- Carry\n");
                    break;
                case 1:
                    printf("- Overflow\n");
                    break;
                case 2:
                    printf("- Zero\n");
                    break;
                case 3:
                    printf("- Negative\n");
                    break;
                case 4:
                    printf("- Extend\n");
                    break;
                case 5:
                case 6:
                case 7:
                    printf("- Bit %d\n", i);
                    break;
                case 8:
                case 9:
                case 10:
                    printf("- Interrupt mask bit %d\n", i - 8);
                    break;
                case 11:
                case 12:
                    printf("- Bit %d\n", i);
                    break;
                case 13:
                    printf("- Supervisor state\n");
                    break;
                case 14:
                    printf("- Bit %d\n", i);
                    break;
                case 15:
                    printf("- Trace mode\n");
                    break;
                default:
                    break;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Error: missing arguments", argv[0]);
        return 1;
    }

    if (strlen(argv[1]) > 4){
        printf("Warning: Maximum size is 2 bytes");
        return 1;
    }

    uint32_t hex_value = strtol(argv[1], NULL, 16);

    print_flags(hex_value);

    return 0;
}