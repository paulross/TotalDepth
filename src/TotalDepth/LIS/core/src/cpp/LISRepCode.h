//
//  LisRepCode.hpp
//  TotalDepth
//
//  Created by Paul Ross on 14/01/2019.
//

#ifndef LisRepCode_h
#define LisRepCode_h

/* #include <stdio.h> */
#include <cstddef>
#include <cstdint>

/* Allow access from C/C++ code. */
extern const size_t RC_49_SIZE;
double _from49(uint16_t word);
uint16_t _to49(double value);

extern const size_t RC_68_SIZE;
double _from68(uint32_t word);
uint32_t _to68(double value);

#endif /* LisRepCode_h */
