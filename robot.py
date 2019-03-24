import textwrap


class Robot:
    def __init__(self, debug_mode=False):
        self.memory = []
        self.input = []
        self.output = []
        self.hand = None
        self.subroutine = None
        self.exit_subroutine = False
        self.program = None
        self.exit_flag = False
        self.debug_mode = debug_mode

        self.commands = {
            'INPUT': self.cmd_input,
            'OUTPUT': self.cmd_output,
            'ADD': self.cmd_add,
            'SUB': self.cmd_sub,
            'COPYTO': self.cmd_copyto,
            'COPYFROM': self.cmd_copyfrom,
            'JUMP': self.cmd_jump,
            'JUMPIFZERO': self.cmd_jumpifzero,
            'JUMPIFNEG': self.cmd_jumpifneg
        }

    def run_program(self, program_str):
        self.parse_commands(program_str)
        self.subroutine = self.subroutine if self.subroutine else 'Main'

        while not self.exit_flag:
            current_commands = self.program[self.subroutine]

            for cmd in current_commands:
                cmd_fn = self.commands[cmd['name']]

                if 'arg' in cmd:
                    self.debug(cmd['name'], cmd['arg'])
                    cmd_fn(cmd['arg'])
                else:
                    self.debug(cmd['name'])
                    cmd_fn()

                if self.exit_subroutine:
                    self.debug(f'\n[{self.subroutine}]')
                    self.exit_subroutine = False
                    break

    def parse_commands(self, program_str):
        program_str = textwrap.dedent(program_str).strip()
        self.program = {}
        subroutine = None

        if not program_str:
            return

        for line in program_str.split('\n'):
            if not line:
                continue

            command = {}

            if ':' in line:
                subroutine = line.split(':')[0]
                self.program.setdefault(subroutine, [])

                if not self.subroutine:
                    self.subroutine = subroutine

                continue

            if '(' in line and ')' in line:
                pieces = line.split('(')
                command['name'] = pieces[0]
                command['arg'] = pieces[1].split(')')[0]

                try:
                    command['arg'] = int(command['arg'])
                except ValueError:
                    pass
            else:
                command['name'] = line

            if command['name'] not in self.commands:
                return self.error(f"Command not found: {command['name']}")

            if not subroutine:
                subroutine = 'Main'

            self.program.setdefault(subroutine, []).append(command)

    def cmd_input(self):
        if not len(self.input):
            self.hand = None
            self.exit_flag = True
            return

        self.hand = self.input.pop(0)

    def cmd_output(self):
        if self.hand is None:
            return

        self.output.append(self.hand)
        self.hand = None

        if not len(self.input):
            self.exit_flag = True
            return

    def cmd_add(self, mem_index):
        if self.hand is None:
            return

        self.hand += self.memory[mem_index]

    def cmd_sub(self, mem_index):
        if self.hand is None:
            return

        self.hand -= self.memory[mem_index]

    def cmd_copyto(self, mem_index):
        if len(self.memory) <= mem_index:
            self.memory = [None] * (mem_index + 1)

        self.memory[mem_index] = self.hand

    def cmd_copyfrom(self, mem_index):
        self.hand = self.memory[mem_index]

    def cmd_jump(self, subroutine):
        if not self.valid_subroutine(subroutine):
            return

        self.subroutine = subroutine
        self.exit_subroutine = True

    def cmd_jumpifzero(self, subroutine):
        if not self.valid_subroutine(subroutine):
            return

        if self.hand is not None and self.hand == 0:
            self.subroutine = subroutine
            self.exit_subroutine = True

    def cmd_jumpifneg(self, subroutine):
        if not self.valid_subroutine(subroutine):
            return

        if self.hand is not None and self.hand < 0:
            self.subroutine = subroutine
            self.exit_subroutine = True

    def valid_subroutine(self, subroutine):
        if subroutine not in self.program:
            self.error(f'Subroutine not found: {subroutine}')
            return False

        return True

    def debug(self, *args):
        if self.debug_mode:
            print(*args)

    @staticmethod
    def error(message):
        print(f'(ERR) {message}')

    def __str__(self):
        return f'Input\t{self.input}\nOutput\t{self.output}\nHand\t{self.hand}\n'


if __name__ == '__main__':
    r = Robot(debug_mode=True)
    r.input = [8, 3, 5, 0, 0, 6]
    r.memory = [1]

    program = '''
        Alku:
        INPUT
        ADD(0)
        OUTPUT
        INPUT
        SUB(0)
        JUMPIFNEG(VainNeg)
        JUMP(Alku)
        
        VainNeg:
        OUTPUT
        JUMP(Alku)
    '''

    r.run_program(program)
    print(str(r))
