class NaiveMisc(object):

    def __init__(self, word_size):
        assert word_size >= 2
        self.word_size = word_size
        self.memory = [0] * 2**word_size
        self.ip = 0

    def set_ip(self, ip):
        assert 0 <= ip < len(self.memory)
        assert ip % 4 == 0
        self.ip = ip

    def set_word(self, address, value):
        assert 0 <= value < 2**self.word_size
        assert 0 <= address
        self.memory[address] = value

    def get_ip(self):
        return self.ip

    def get_word(self, address):
        assert 0 <= address
        return self.memory[address]

    def step(self):
        n = len(self.memory)

        assert self.ip % 4 == 0

        dst = self.memory[self.ip]
        src1 = self.memory[self.ip + 1]
        src2 = self.memory[self.ip + 2]
        jump = self.memory[self.ip + 3]

        dst = (dst + self.ip) % n

        higher_bits = jump // (n // 4)
        jump %= n
        assert 0 <= higher_bits < 4

        if higher_bits & 2 == 0:
            src1 = self.memory[(src1 + self.ip) % n]
        if higher_bits & 1 == 0:
            src2 = self.memory[(src2 + self.ip) % n]

        self.memory[dst] = (src1 - src2) % n

        self.ip += jump * 4
        self.ip %= n

    def simulate(self, num_steps):
        for _ in range(num_steps):
            self.step()

    def __str__(self):
        return 'NaiveMisc(ip={}, memory={})'.format(self.ip, self.memory)


def main():  # pragma: no cover
    nm = NaiveMisc(word_size=4)
    for i in range(2**nm.word_size):
        nm.set_word(i, i)

    for _ in range(20):
        print(nm)
        nm.step()


if __name__ == '__main__':  # pragma: no cover
    main()
