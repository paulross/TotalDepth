//
//  LisRepCode.cpp
//  TotalDepth
//
//  Created by Paul Ross on 14/01/2019.
//  Copyright © 2019 Engineering UN. All rights reserved.
//

#include "LISRepCode.h"

#include <math.h>

/* C/C++ function that returns a double from a Rep code 68 word (a 32 bit integer). */
double _from68(int32_t word) {
    signed int mantissa;
    if (word & 0x80000000) {
        // This is: -0x800000
        // i.e.: -2147483648 >> 8
        // i.e.: (-1 << 31) >> 8
        // i.e.: -1 << (31-8)
        // i.e.: -1 << 23
        mantissa = -8388608;
    } else {
        mantissa = 0;
    }
    mantissa |= word & 0x007FFFFF;
    int exponent = word & 0x7F800000;
    exponent >>= 23;
    // NOTE: At this stage the mantissa is an integer
    // and needs to be divided by 2^23 to get the fractional value.
    // For efficiency we do not do this but instead adjust the exponent.
    // If the mantissa was the correct fractional value the next line
    // should be exp = (mant & 0x80000000) ? (127 - exp) : (exp - 128);
    // instead we use the numbers 104 and 151 i.e. subtracting 23
    if (word & 0x80000000) {
        exponent = 104 - exponent;
    } else {
        exponent -= 151;
    }
    return ldexp(mantissa, exponent);
}

/* C/C++ function that returns a 32 bit representation code word from a double. */
int32_t _to68(double value) {
    int32_t word = 0;
    int exponent = 0;
    double mantissa = frexp(value, &exponent);
    // Overflow and underflow control
    if (exponent <= -(128 + 23)) {
        // Set zero
        return 0x40000000;
    } else if (exponent > 127) {
        // Set minumum or maximum
        if (value < 0.0) {
            // Negative, return minimum
            return 0xFFC00000;
        }
        // Positive, return maximum
        return 0x7FFFFFFF;
    }
    // If exponent is <128 then reduce mantissa by excess 128
    if (exponent < -128) {
        mantissa /= pow(2, -128 - exponent);
        exponent = -128;
    }
    // Set exponent as excess 128
    if (value < 0.0) {
        exponent = 127 - exponent;
        // Set sign bit and shift for exponent
        word = 1 << 8;
    } else {
        exponent -= 128;
        word = 0;
    }
    word |= exponent & 0xFF;
    // Shift for mantissa
    word <<= 23;
    word |= static_cast<int32_t>(mantissa * (1 << 23)) & 0x007FFFFF;
    return word;
}
