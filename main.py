import curses

class Computer:
    def __init__(self, screen):
        self.__screen = screen
        self.__memory = [0] * 32
        self.__disassembly = [''] * 32
        self.__a = 0
        self.__z = False
        self.__neg = False
        self.__sp = 0
        self.__overflow = False
        self.__underflow = False
        self.__instructions = [
            'LDAM', 'LDAI', 'STA',  'INC', 
            'DEC',  'SUM',  'SUB',  'JMP',
            'JZ',   'JN',   'AND',  'OR',
            'XOR',  'NOT',  'OUT',  'IN',
            'END'
        ]

    def set_program(self, program):
        self.compile(program)

    def compile(self, program):
        idx_memory = 0
        lines = program.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            tokens = line.split(' ')
            instruction = tokens[0]
            data_low = None
            data_high = None
            data = None
            instruction_code = self.__instructions.index(instruction)
            if instruction in ['LDAM', 'LDAI', 'STA', 'SUM', 'SUB', 'JMP', 'JZ', 'JN', 'AND', 'OR', 'XOR']:
                data = int(tokens[1])
                if instruction in ['LDAM', 'STA', 'SUM', 'SUB', 'JMP', 'JZ', 'JN', 'AND', 'OR', 'XOR']:
                    data_low = data % 256
                    data_high = data // 256
                else:
                    data_low = data
            self.__memory[idx_memory] = instruction_code
            disassembly = instruction
            if data is not None:
                disassembly = disassembly + ' ' + str(data)
            self.__disassembly[idx_memory] = disassembly
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
        self.print_status()
        while not self.exec_step():
            self.print_status()
            pass

    # def print_mem(self):
    #     for i in range(32):
    #         print('MEM [%2d]: %5d' % (i, self.__memory[i]))

    def print_status(self):
        self.__screen.refresh(self.__memory, self.__disassembly, self.__a, self.__sp)
        # print('SP: %d' % self.__sp)
        # print('A: %d' % self.__a)
        # self.print_mem()

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
        elif instruction == 'IN':
            value = self.__screen.input()
            self.__a = value
            self.__sp += 1
        elif instruction == 'OUT':
            self.__screen.show_output(self.__a)
            self.__sp += 1
        elif instruction == 'END':
            self.__screen.show_finished()
            return True
        self.update_flags()
        return False

class Screen:
    def __init__(self):
        self.__stdscr = curses.initscr()
        self.__memory = []
        self.__registers = {}
        curses.echo()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    def __del__(self):
        self.__stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def show_memory(self, mem, disassembly, sp):
        l = 1
        c = 1
        positions = 32
        self.__stdscr.addstr(l, c, 'MEMORY', curses.A_BOLD)
        l += 1
        self.__stdscr.addstr(l, c, '      +----------+ +------+ +----------------+')
        l += 1
        for i in range(positions):
            sp_indicator = ''
            if i == sp:
                sp_indicator = '>>'
            s = f'{sp_indicator:2s} {i:>2} | {mem[i]:>08b} | | {mem[i]:>4d} | | {disassembly[i]:14s} |'
            if i == sp:
                self.__stdscr.addstr(l, c, s, curses.color_pair(1))
            else:
                self.__stdscr.addstr(l, c, s)
            l += 1
        self.__stdscr.addstr(l, c, '      +----------+ +------+ +----------------+')

    def show_a(self, a):
        l = 3
        c = 55
        self.__stdscr.addstr(l, c, 'ACCUMULATOR: ', curses.A_BOLD)
        self.__stdscr.addstr(l, c + 15, f'{a:08b}b {a:4d}')

    def show_output(self, output):
        l = 5
        c = 55
        if output is None:
            out = ''
        else:
            out = str(output)
        self.__stdscr.addstr(l, c, 'OUTPUT: ', curses.A_BOLD)
        self.__stdscr.addstr(l, c + 15, f'{out:15s}')

    def show_finished(self):
        self.__stdscr.addstr(36, 0, 'Execution terminated. Press any key to exit..........', curses.color_pair(2))
        c = self.__stdscr.getch()

    def input(self):
        l = 1
        c = 30
        self.__stdscr.addstr(l, c, 'INPUT: ', curses.A_STANDOUT)
        s = self.__stdscr.getstr(l, c + 10, 6)
        self.__stdscr.addstr(l, c, ' ' * 30)
        return int(s)

    def refresh(self, mem, disassembly, a, sp):
        self.show_a(a)
        self.show_memory(mem, disassembly, sp)
        self.__stdscr.refresh()
        self.__stdscr.addstr(36, 0, 'Press Q to finish or any other key to continue: ')
        c = self.__stdscr.getch()
        if c == 'q' or c == 'Q':
            exit()

def main(stdscr):
    print('main')
    s = Screen()
    c = Computer(s)
    c.set_program(
            """
            IN
            STA 30
            IN
            STA 28
            LDAM 30
            SUM 28
            OUT
            END
            """)
    c.exec()

print('mmain')
curses.wrapper(main)

