//
//  LisRepCode.cpp
//  TotalDepth
//
//  Created by Paul Ross on 14/01/2019.
//

#include "LISRepCode.h"

#include <math.h>
const size_t RC_49_SIZE = 2;

double _from49(uint16_t word) {
    /* Returns a double from Rep code 49 0x31, 16bit floating point representation.
     * Value +153 is 0100 1100 1000 1000 or 0x4C88.
     * Value -153 is 1011 0011 1000 1000 or 0xB388.
     */
    int m = word & 0xFFF0;
    if (word & 0x8000) {
        //   Negative
        m -= 0x10000;
    }
    // Divisor is 2^15 as right 4 bits are zero i.e. 2^11 * 2^4
    double mantissa = static_cast<double>(m) / (1<<15);
    int exponent = word & 0xF;
    return ldexp(mantissa, exponent);
}

uint16_t _to49(double value) {
    /* Converts a double to Rep code 49 0x31, 16bit floating point representation.
     * Value +153 is 0100 1100 1000 1000 or 0x4C88.
     * Value -153 is 1011 0011 1000 1000 or 0xB388.
     */
    uint16_t word = 0;
    int exponent = 0;
    double mantissa = frexp(value, &exponent);
    /* TODO: Overflow, underflow */
    if (exponent <= 0 - 11) {
        // Set zero
        return 0x0000;
    } else if (exponent > 15) {
        // Set minumum or maximum
        if (value < 0.0) {
            // Negative, return minimum
            // TODO: Is this really the minimum?
            return 0xFFFF;
        }
        // Positive, return maximum
        // TODO: Is this really the maximum?
        return 0x7FFF;
    }
    // Denormalisation, if exponent is <128 then reduce mantissa by excess 128
    if (exponent < 0) {
        mantissa /= pow(2, 0 - exponent);
        exponent = 0;
    }
    if (value < 0.0) {
        exponent = 127 - exponent;
        // Set sign bit and shift for mantissa
        word = 1 << 8;
    } else {
        exponent -= 128;
        word = 0;
    }
    word |= static_cast<int16_t>(mantissa * (1 << 12)) & 0x07FF;
    word <<= 4;
    word |= exponent & 0xF;
    return word;
}

/* C/C++ function that returns a double from a Rep code 68 word (a 32 bit integer). */
const size_t RC_68_SIZE = 4;

double _from68(uint32_t word) {
    signed int mantissa;
    if (word & 0x80000000) {
        // This is: -0x800000 or -2147483648 >> 8 or (-1 << 31) >> 8 or  -1 << (31-8)
        // so -1 << 23
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
    // should be exp = (word & 0x80000000) ? (127 - exp) : (exp - 128);
    // instead we use the numbers 104 and 151 i.e. subtracting 23
    if (word & 0x80000000) {
        exponent = 104 - exponent;
    } else {
        exponent -= 151;
    }
    return ldexp(mantissa, exponent);
}

/* C/C++ function that returns a 32 bit representation code word from a double. */
uint32_t _to68(double value) {
    uint32_t word = 0;
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
            // TODO: Is this really the minimum?
            return 0xFFC00000;
        }
        // Positive, return maximum
        // TODO: Is this really the maximum?
        return 0x7FFFFFFF;
    }
    // Denormalisation, if exponent is <128 then reduce mantissa by excess 128
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
    word |= static_cast<uint32_t>(mantissa * (1 << 23)) & 0x007FFFFF;
    return word;
}
