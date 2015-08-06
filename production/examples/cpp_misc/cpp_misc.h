#pragma once

#include <assert.h>
#include <sstream>
#include <vector>

class CppMisc {
public:
    int word_size;
    std::vector<int> memory;
    int ip;

    CppMisc(int word_size) : word_size(word_size), memory(1 << word_size), ip(0) {
    }

    int get_ip() const {
        return ip;
    }

    void set_ip(int ip) {
        assert(ip >= 0);
        assert(ip < memory.size());
        assert(ip % 4 == 0);
        this->ip = ip;
    }

    int get_word(int addr) {
        return memory.at(addr);
    }

    void set_word(int addr, int value) {
        assert(value >= 0);
        assert(value < memory.size());
        memory.at(addr) = value;
    }

    void step() {
        assert(ip % 4 == 0);
        int dst = memory.at(ip);
        int src1 = memory.at(ip + 1);
        int src2 = memory.at(ip + 2);
        int jumps = memory.at(ip + 3);

        const int n = memory.size();

        dst = (dst + ip) % n;

        int high_bits = jumps / (n / 4);
        jumps %= n / 4;
        if ((high_bits & 2) == 0)
            src1 = memory.at((ip + src1) % n);
        if ((high_bits & 1) == 0)
            src2 = memory.at((ip + src2) % n);

        memory.at(dst) = (src1 - src2 + n) % n;

        ip = ip + 4 * jumps;
        ip %= n;
    }

    void simulate(int num_steps) {
        assert(num_steps >= 0);
        for (int i = 0; i < num_steps; ++i)
            step();
    }

    std::string __str__() {
        std::ostringstream out;
        out << "CppMisc(ip=" << ip << ", memory=[";
        bool first = true;
        for (auto cell : memory) {
            if (!first)
                out << ", ";
            out << cell;
            first = false;
        }
        out << "])";
        return out.str();
    }
};
