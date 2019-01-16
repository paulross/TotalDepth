//
//  main.cpp
//  TotalDepth
//
//  Created by Paul Ross on 14/01/2019.
//  Copyright © 2019 Engineering UN. All rights reserved.
//

#include <iostream>
#include <iomanip>
#include <vector>

#include "LISRepCode.h"

void test_repcode_68(void) {
    std::cout << __FUNCTION__ << "()" << std::endl;
    std::vector<std::pair<int32_t, double>> test_data {
        { 0x444C8000, 153 },
        { 0xBBB38000, -153 },
        { 0x40000000, 0.0 }
    };
    for (auto pair : test_data) {
        std::cout << "Word: 0x" << std::hex << pair.first;
        std::cout << " value: " << std::dec << _from68(pair.first);
        std::cout << " expected: " << std::dec << pair.second;
        std::cout << std::endl;
    }
    for (auto pair : test_data) {
        std::cout << "Value: " << std::dec << pair.second;
        std::cout << " word: 0x" << std::hex << _to68(pair.second);
        std::cout << " word: 0x" << std::hex << (long) _to68(pair.second);
        std::cout << " expected: 0x" << std::hex << pair.first;
        std::cout << std::dec;
        std::cout << std::endl;
    }
    std::cout << __FUNCTION__ << "() - DONE" << std::endl;
}

int main(int argc, char **argv) {
    std::cout << "Hello world" << std::endl;
    // 0x444C8000 -> 153
    // 0xBBB38000 -> -153
    // 0x40000000 -> 0.0
    int32_t word;
    double value;
    
    value = 153.0;
    word = _to68(value);
    std::cout << "Word: 0x" << std::hex << word << " Value: " << std::dec << value << std::endl;
    word = 0x444C8000;
    value = _from68(word);
    std::cout << "Word: 0x" << std::hex << word << " Value: " << std::dec << value << std::endl;
//    word = 0x807FFFFF;
    // -2.12676e+37
    word = 0x80700000;
//    // Word: 0x807fffff Value: -2.02824e+31
//    word = 0x807FFFFF;
    value = _from68(word);
    std::cout << "Word: 0x" << std::hex << word << " Value: " << std::dec << value << std::endl;
//    test_repcode_68();
    return 0;
}
