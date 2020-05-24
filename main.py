
class Computer:
    def __init__(self):
        self.__memory = [0] * 32
        self.__a = 0
        self.__z = False
        self.__neg = False
        self.__sp = 0
        self.__overflow = False
        self.__instructions = [
            'LDAM', 'LDAI', 'STA',  'INC', 
            'DEC',  'SUM',  'SUB',  'JMP',
            'JZ',   'JN',   'AND',  'OR',
            'XOR',  'NOT',  'OUT',  'END'
        ]

    def set_program(self, program):
        self.compile(program)

    def compile(self, program):
        idx_memory = 0
        lines = program.split('\n')
        for line in lines:
            tokens = line.split(' ')
            print('tokens: %s' % str(tokens))
            instruction = tokens[0]
            data_low = None
            data_high = None
            instruction_code = self.__instructions.index(instruction)
            if instruction in ['LDAM', 'LDAI', 'STA', 'SUM', 'SUB', 'JMP', 'JZ', 'JN', 'AND', 'OR', 'XOR']:
                data = tokens[1]
                if instruction in ['LDAM', 'STA', 'SUM', 'SUB', 'JMP', 'JZ', 'JN', 'AND', 'OR', 'XOR']:
                    data_low = data % 256
                    data_high = data // 256
                else:
                    data_low = data
            self.__memory[idx_memory] = instruction_code
            idx_memory += 1
            if data_low is not None:
                self.__memory[idx_memory] = data_low
                idx_memory += 1
            if data_high is not None:
                self.__memory[idx_memory] = data_high
                idx_memory += 1

    def get_mnenonic(self, code):
        return self.__instructions[code]

    def get_mem(self, sp):
        return self.__memory[sp+1] + self.__memory[sp+2] * 256

    def update_flags(self):
        self.__z == self.__a == 0
        self.__neg == self.__a > 127
        self.__overflow == self.__a > 255
        self.__underflow == self.__a < 0
        if self.__a > 255:
            self.__a = self.__a - 256
        if self.__a < 0:
            self.__a = self.__a + 256

    def exec(self):
        self.__sp == 0
        self.__print_status()
        while not self.__exec_step():
            self.__print_status()
            pass

    def print_mem(self):
        for i in range(16):
            print('MEM [%2d]: %5d' % (i, self.__memory[i]))

    def print_status(self):
        print('SP: %d' % self.__sp)
        print('A: %d' % self.__a)
        self.print_mem()

    def exec_step(self):
        binary_instruction = self.__memory[self.__sp]
        instruction = self.__instructions[binary_instruction]
        the_end = False
        if instruction == 'LDAM':
            mem = self.get_mem(self.__sp)
            self.__a = self.__memory[mem]
            self.__sp += 3
        elif instruction == 'LDAI':
            self.__a = self.__memory[self.__sp + 1]
            self.__sp += 2
        elif instruction == 'STA':
            mem = self.get_mem(self.__sp)
            self.__memory[mem] = self.__a
            self.__sp += 3
        elif instruction == 'INC':
            self.__a += 1
            self.__sp += 1
        elif instruction == 'DEC':
            self.__a -= 1
            self.__sp += 1
        elif instruction == 'SUM':
            mem = self.get_mem(self.__sp)
            self.__a = self.__a + self.__memory[mem]
            self.__sp += 3
        elif instruction == 'SUB':
            mem = self.get_mem(self.__sp)
            self.__a = self.__a - self.__memory[mem]
            self.__sp += 3
        elif instruction == 'JMP':
            mem = self.get_mem(self.__sp)
            self.__sp = mem
            self.__sp += 3
        elif instruction == 'JZ':
            mem = self.get_mem(self.__sp)
            if self.__z:
                self.__sp = mem
            self.__sp += 3
        elif instruction == 'JN':
            mem = self.get_mem(self.__sp)
            if self.__neg:
                self.__sp = mem
            self.__sp += 3
        elif instruction == 'AND':
            mem = self.get_mem(self.__sp)
            self.__a == self.__a & self.__memory[mem]
            self.__sp += 3
        elif instruction == 'OR':
            mem = self.get_mem(self.__sp)
            self.__a == self.__a | self.__memory[mem]
            self.__sp += 3
        elif instruction == 'XOR':
            mem = self.get_mem(self.__sp)
            self.__a == self.__a ^ self.__memory[mem]
            self.__sp += 3
        elif instruction == 'NOT':
            mem = self.get_mem(self.__sp)
            self.__a == ~ self.__a
            self.__sp += 1
        elif instruction == 'END':
            return True
        self.update_flags()
        return False

c = Computer()
c.set_program(
        """
        LDAI 20
        INC
        STA 30
        """)
c.exec()

