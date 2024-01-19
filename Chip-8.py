import pygame
import random
import sys
import time

class Chip8():
    def __init__(self):
        # 4 KB of memory
        self.memory = [0] * 4096
        # 16 registers
        self.v = [0] * 16
        # Store memory addresses
        self.i = 0
        # Timers
        self.delayTimer = 0
        self.soundTimer = 0
        # Program counter
        self.pc = 0
        # The Stack
        self.stack = [0] * 16
        # Stack pointer
        self.sp = 0

        self.draw = True
        
        self.x = 0
        self.y = 0
        # Pygame/screen initialization
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("Insert buzz file path here")
        self.screen = pygame.display.set_mode((64 * 10, 32 * 10))
        self.key_inputs = [0] * 16 
        self.display_buffer = [0] * 32 * 64

        self.opcode = 0

        self.opcodeFunctions = {
            0x0000: self.opcode_0nnn,
            0x00E0: self.opcode_00E0,
            0x000E: self.opcode_00EE,
            0x1000: self.opcode_1nnn,
            0x2000: self.opcode_2nnn,
            0x3000: self.opcode_3xkk,
            0x4000: self.opcode_4xkk,
            0x5000: self.opcode_5xy0,
            0x6000: self.opcode_6xkk,
            0x7000: self.opcode_7xkk,
            0x8000: self.opcode_8nnn,
            0x8001: self.opcode_8xy1,
            0x8002: self.opcode_8xy2,
            0x8003: self.opcode_8xy3,
            0x8004: self.opcode_8xy4,
            0x8005: self.opcode_8xy5,
            0x8006: self.opcode_8xy6,
            0x8007: self.opcode_8xy7,
            0x800E: self.opcode_8xyE,
            0x9000: self.opcode_9xy0,
            0xA000: self.opcode_Annn,
            0xB000: self.opcode_Bnnn,
            0xC000: self.opcode_Cxkk,
            0xD000: self.opcode_Dxyn,
            0xE000: self.opcode_Ennn,
            0xE00E: self.opcode_Ex9E,
            0xE001: self.opcode_ExA1,
            0xF000: self.opcode_Fnnn,
            0xF007: self.opcode_Fx07,
            0xF00A: self.opcode_Fx0A,
            0xF015: self.opcode_Fx15,
            0xF018: self.opcode_Fx18,
            0xF01E: self.opcode_Fx1E,
            0xF029: self.opcode_Fx29,
            0xF033: self.opcode_Fx33,
            0xF055: self.opcode_Fx55,
            0xF065: self.opcode_Fx65
        }

    def loadFontsIntoMemory(self):
        fonts = [
                0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                0xF0, 0x80, 0xF0, 0x10, 0xF8,  # 5
                0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
                0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
            ]
        
        self.pc = 512 # <-- Start in memory for majority of Chip-8 programs
        # Iterate over each byte in fonts to load into memory
        for i in range(80):
            self.memory[i] = fonts[i]
        print("Fonts loaded into memory!")

    def loadROM(self, filePath):
        file = open(filePath, "rb").read()
        for i, program in enumerate(file):
            self.memory[i + 0x200] = program
        print("Program loaded into memory!")
    
    def cycle(self):
        self.draw = False

        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Get second nibble & shift 8 bits right (get rid of everything else but 2nd nibble)
        self.x = (self.opcode & 0x0F00) >> 8 
        # Get third nibble & shift 4 bits
        self.y = (self.opcode & 0x00F0) >> 4  
        
        hexop = self.opcode & 0xF000
        try:
            self.opcodeFunctions[hexop]()
        except Exception as e:
            print(f"Unknown Instruction: {hex(hexop)}")
            print(e.with_traceback())
            self.pc += 2

        self.updateTimers()

    def updateTimers(self):
        if self.delayTimer > 0:
            self.delayTimer -= 1

        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                pygame.mixer.music.play()
    
    ############ OPCODE Instructions ############
    def opcode_0nnn(self):
        if self.opcode == 0x0:
            pygame.quit()
            sys.exit()
        if self.opcode == 0xe0:
            self.opcode_00E0()
            return
        
        extrop = self.opcode & 0xF00F
        try:
            self.opcodeFunctions[extrop]()
        except:
            print("Unknown Instruction: %X" % self.opcode)
            self.pc += 2
    
    # CLS - clear the display
    def opcode_00E0(self):
        self.display_buffer = [0] * 64 * 32
        self.draw = True
        self.pc += 2

    # RET - Return from a subroutine
    def opcode_00EE(self):
        self.pc = self.stack[self.sp] + 2
        self.sp -= 1
        
    # 1nnn - JP addr: Jump to location nnn - sets program counter to nnn
    def opcode_1nnn(self):
        self.pc = self.opcode & 0x0FFF

    # 2nnn - Call addr: Call subroutine at nnn
    def opcode_2nnn(self):
        # Increments stack pointer, puts current PC on top of stack
        nnn = self.opcode & 0xFFF
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = nnn

    # 3xkk - SE Vx, byte: Skip next instruction if Vx = kk
    def opcode_3xkk(self):
        # Compare register Vx to kk, if equal, increment PC by 2
        # opcode & 0xFF is getting last byte of opcode (where the kk is)
        if self.v[self.x] == (self.opcode & 0x00FF):
            self.pc += 4
        else:
            self.pc += 2
    # 4xkk - SNE Vx, byte: skip next instruction if Vx != kk
    def opcode_4xkk(self):
        # Interpreter compares register Vx to kk, if not equal, += 2
        if self.v[self.x] != (self.opcode & 0x00FF):
            self.pc += 4
        else:
            self.pc += 2

    # 5xy0 - SE Vx, Vy: Skip next instruction if Vx = Vy
    def opcode_5xy0(self):
       # Compare register Vx to register Vy, if equal, pc += 2
        if self.v[self.x] == self.v[self.y]:
            self.pc += 4
        else:
            self.pc += 2
    
    # 6xkk - LD Vx, byte: Set Vx = kk 
    def opcode_6xkk(self):
        # Put value kk into register Vx
        self.v[self.x] = self.opcode & 0x00FF 
        self.pc += 2
    
    # 7xkk - ADD Vx, byte: Set Vx = Vx + kk
    def opcode_7xkk(self):
        # Adds value kk to the value of register Vx, then stores in Vx
        self.v[self.x] += (self.opcode & 0x00FF)
        self.v[self.x] &= 0xFF
        self.pc += 2
    
    def opcode_8nnn(self):
        if self.opcode & 0x000F == 0:
            self.opcode_8xy0()
            return
        try:
            self.opcodeFunctions[self.opcode & 0xF00F]()
        except:
            print("Unknown Instruction: %X" % self.opcode)
            self.pc += 2
    
    # 8xy0 - LD Vx, Vy: Set Vx = Vy
    def opcode_8xy0(self):
        # Stores value of register Vy in Vx
        self.v[self.x] = self.v[self.y]
        self.v[self.x] &= 0xFF
        self.pc += 2
    
    # 8xy1 - OR Vx, Vy: Set Vx OR Vy
    def opcode_8xy1(self):
        # Bitwise OR on Vx & Vy then store in Vx
        self.v[self.x] |= self.v[self.y]
        self.v[self.x] &= 0xFF
        self.pc += 2

    # 8xy2 - AND Vx, Vy: Set Vx AND Vy
    def opcode_8xy2(self):
        # Bitwise AND on Vx & Vy then store in Vx
        self.v[self.x] &= self.v[self.y]
        self.v[self.x] &= 0xFF
        self.pc += 2

    # 8xy3 - XOR Vx, Vy: Set Vx XOR Vy
    def opcode_8xy3(self):
        # Bitwise XOR on Vx & Vy then store in Vx
        self.v[self.x] ^= self.v[self.y]
        self.v[self.x] &= 0xFF
        self.pc += 2
    
    # 8xy4 - ADD Vx, Vy: Set Vx = Vx + Vy
    def opcode_8xy4(self):
        # Vx = Vx + Vy
        total = self.v[self.x] + self.v[self.y]
        self.v[self.x] = total
        # VF is 0
        self.v[0xF] = 0
        # VF is 1 if sum greater than 8 bits
        if total > 0x00FF:
            self.v[0xF] = 1
        
        self.v[self.x] &= 0xFF
        self.pc += 2
            
    # 8xy5 - SUB Vx, Vy: Set Vx = Vx - Vy, set VF = carry
    def opcode_8xy5(self):
        # VF = 0
        self.v[0xF] = 0
        # Set VF = 1 if Vx > Vy
        if self.v[self.x] > self.v[self.y]:
            self.v[0xF] = 1

        # Vy is subtracted from Vx, stored in Vx
        self.v[self.x] -= self.v[self.y]
        self.v[self.x] &= 0xFF
        self.pc += 2
    
    # 8xy6 - SHR Vx {, Vy}: Set Vx = Vx SHR 1
    def opcode_8xy6(self):
        # If least significant bit of Vx is 1, set VF to 1, otherwise 0
        self.v[0xF] = self.v[self.x] & 0x1
        # Then Vx is divided by 2
        self.v[self.x] >>= 1
        self.pc += 2
    
    # 8xy7 - SUBN Vx, Vy: Set Vx = Vy - Vx, then set VF = NOT borrow
    def opcode_8xy7(self):
        # If Vy > Vx, set VF = 1
        if self.v[self.y] < self.v[self.x]:
            self.v[0xF] = 0
        else:        
            self.v[0xF] = 1
        # Vx is then subtractred from Vy and stored in Vx
        self.v[self.x] = self.v[self.y] - self.v[self.x]
        self.v[self.x] &= 0xFF
        self.pc += 2

    # 8xyE - SHL Vx {, Vy}: Set Vx = Vx SHL 1
    def opcode_8xyE(self):
        # If most significant bit if Vx is 1, set VF to 1, else 0
        self.v[0xF] = (self.v[self.x] & 0x80) >> 7
        # Vx is multiplied by 2
        self.v[self.x] <<= 1
        self.v[self.x] &= 0xFF
        self.pc += 2

    # 9xy0 - SNE Vx, Vy: Skip next instruction if Vx != Vy
    def opcode_9xy0(self):
        if self.v[self.x] != self.v[self.y]:
            self.pc += 4
        else:
            self.pc += 2
    
    # Annn - LD I, addr: Set I = nnn
    def opcode_Annn(self):
        self.i = self.opcode & 0x0FFF
        self.pc += 2
    
    # Bnnn - JP V0, addr: Jump to location nnn + V0
    def opcode_Bnnn(self):
        # PC is set to nnn + V0
        self.pc = (self.opcode & 0x0FFF) + self.v[0]

    # Cxkk - RND Vx, byte: Set Vx = random byte AND kk
    def opcode_Cxkk(self):
        # Generate random number from 0 to 255
        rand = random.randint(0, 255)
        # AND with kk, store in Vx
        self.v[self.x] = rand & (self.opcode & 0x0FF)
        self.pc += 2
    
    # Dxyn - DRW Vx, Vy, nibble:
    # Display n-byte sprite starting at memory location I at (Vx, Vy), 
    # set VF = collision
    def opcode_Dxyn(self):
        x = self.v[self.x]
        y = self.v[self.y]
        self.v[0xF] = 0
        
        width = 8
        height = self.opcode & 0x000F # last nibble of opcode

        for h in range(height):
            pixel = self.memory[self.i + h]
            for w in range(width):
                if (pixel & (0x80 >> w)) != 0:
                    location = (x + w + (h + y) * 64) % 2048
                    if self.display_buffer[location] == 1:
                        self.v[0xF] = 1

                    self.display_buffer[location] ^= 1
        
        self.draw = True
        self.pc += 2
    
    def opcode_Ennn(self):
        try:
            self.opcodeFunctions[self.opcode & 0xF00F]()
        except Exception as e:
            print(e.with_traceback())
            print("Unknown Instruction: %X" % self.opcode)

    # Ex9E - SKP Vx: skip next instruction if key w/ value Vx is pressed
    def opcode_Ex9E(self):
        # iF key at corresponding value is pressed, increase PC by 2
        if self.key_inputs[self.v[self.x] & 0xF] != 0:
            self.pc += 4
        else:
            self.pc += 2
    
    # ExA1 - SKNP Vx: Skip next instruction if key w/ value Vx is not pressed
    def opcode_ExA1(self):
        if self.key_inputs[self.v[self.x] & 0xF] == 0:
            self.pc += 4
        else:
            self.pc += 2

    def opcode_Fnnn(self):
        try:
            self.opcodeFunctions[self.opcode & 0xF0FF]()
        except Exception as e:
            print(e.with_traceback())
            print("Unknown Instruction: %X" % self.opcode)
    
    # Fx07 - LD Vx, DT: Set Vx = delay timer value
    def opcode_Fx07(self):
        self.v[self.x] = self.delayTimer
        self.pc += 2
    
    # Fx0A - LD Vx, K: Wait for a key press, store value of key in Vx
    def opcode_Fx0A(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key in self.keyset.keys():
                    self.key_inputs[self.keyset[event.key]] = 1
                    break
        self.pc += 2

    # Fx15 - LD DT, Vx: Set delay timer = Vx
    def opcode_Fx15(self):
        self.delayTimer = self.v[self.x]
        self.pc += 2

    # Fx18 - LD ST, Vx: Set sound timer = Vx
    def opcode_Fx18(self):
        self.soundTimer = self.v[self.x]
        self.pc += 2

    # Fx1E - ADD I, Vx: Set I = I + Vx
    def opcode_Fx1E(self):
        self.i += self.v[self.x]
        if self.i > 0xFFF:
            self.v[0xF] = 1
            self.i &= 0xFFF
        else:
            self.v[0xf] = 0
        self.pc += 2
    # Fx29 - LD F, Vx - ADD I, Vx: Set I = location of sprite for digit Vx
    def opcode_Fx29(self):
        self.i = (5 * (self.v[self.x])) & 0x0FFF # multiplied by 5 because each sprite is 5 bytes long
        self.pc += 2

    # Fx33 - LD B, Vx: Store BCD representation of Vx in memory @ I, I+1, and I+2
    def opcode_Fx33(self):
        # Decimal value of Vx, place 100s digit in I
        self.memory[self.i] = self.v[self.x] // 100
        # Decimal value of Vx, place 10s digit in I+1
        self.memory[self.i + 1] = (self.v[self.x] % 100) // 10
        # Decimal value of Vx, place 1s digit in I+2
        self.memory[self.i + 2] = self.v[self.x] % 10
        self.pc += 2

    # Fx55 - LD [I], Vx: Store registers V0 - Vx in memory starting at I
    def opcode_Fx55(self):
        # Loop through registers V0 - Vx
        regIndex = 0
        while regIndex <= self.x:
            # Copy into memory
            self.memory[self.i + regIndex] = self.v[regIndex]
            regIndex += 1
        self.i += (self.x) + 1
        self.pc += 2

    # Fx65 - LD Vx, [I]: Read registers V0 - Vx from memory starting at I
    def opcode_Fx65(self):
        # Loop through registers V0 - Vx
        regIndex = 0
        while regIndex <= self.x:
            # Read values from memory starting at I
            self.v[regIndex] = self.memory[self.i + regIndex]
            regIndex += 1
        self.i += (self.x) + 1
        self.pc += 2

    def drawScreen(self):
        black = (0, 0, 0)
        white = (255, 255, 255)
        self.screen.fill(black)

        for y in range(32):
            for x in range(64):
                if self.display_buffer[x + (y*64)] == 1:
                    pygame.draw.rect(self.screen, white, (x*10,y*10,10,10), 0)
                else:
                    pygame.draw.rect(self.screen, black, (x*10,y*10,10,10), 0)

        pygame.display.update()
    
    keyset = {
        pygame.K_1: 1,
        pygame.K_2: 2,
        pygame.K_3: 3,
        pygame.K_4: 12,
        pygame.K_q: 4,
        pygame.K_w: 5,
        pygame.K_e: 6,
        pygame.K_r: 13,
        pygame.K_a: 7,
        pygame.K_s: 8,
        pygame.K_d: 9,
        pygame.K_f: 14,
        pygame.K_z: 10,
        pygame.K_x: 0,
        pygame.K_b: 11,
        pygame.K_v: 15

    }
    
    def main(self):
        self.loadFontsIntoMemory()
        self.loadROM("Insert ROM path here")
        
        clock_speed = 540
        interval = 1 / clock_speed
        while (True):
            start = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in self.keyset.keys():
                        self.key_inputs[self.keyset[event.key]] = 1

                if event.type == pygame.KEYUP:
                    if event.key in self.keyset.keys():
                        self.key_inputs[self.keyset[event.key]] = 0

            self.cycle()
            if self.draw:
                self.drawScreen()
            
            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)


def main():
    cpu = Chip8()
    Chip8.main(cpu)

if __name__ == '__main__':
    main()
