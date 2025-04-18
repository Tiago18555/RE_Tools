import argparse
import sys

pos_a0 = 0x0
pos_a1 = 0x0
pos_a2 = 0x0
pos_a3 = 0x0

d0 = 0x0
d1 = 0x0
d2 = 0x0
d4 = 0x0
r_offset = 0x6da4

a0 = bytearray()
a1 = bytearray()
a2 = bytearray()
a3 = bytearray()

def lzss(offset, size):
    global pos_a0, pos_a1, pos_a2, pos_a3, d0, a1, a3, d1

    pos_a1 = offset
    pos_a2 = 0x0000
    pos_a0 = 0x0000
    d0 = size
    pos_a3 = d0 + pos_a1

    d1 = move_b(a1[pos_a1], d1)
    pos_a1 += 0x1
    d1 |= 0xFF00
    first_loop = True

    while True:
        
        if blt_l(d1) and not first_loop:
            d1 = move_b(a1[pos_a1], d1)
            pos_a1 += 0x1
            d1 |= 0xFF00
            
        first_loop = False

        if (d1 & 0x1) == 0x0:
            d1 = lsr_w(0x1, d1)
            back_ref_copy()
            if pos_a1 > pos_a3:
                break
            else:
                continue
            
        else:
            d1 = lsr_w(0x1, d1)
            direct_copy()
            if pos_a1 > pos_a3:
                break
            else:
                continue            

    d0 = pos_a2
    d0 += 0x1
    d0 &= 0xFFFFFFFE
    pos_a0 = d0
    
def direct_copy():
    
    global a1, a2, pos_a1, pos_a2
    
    try:
        a2.append( a1[pos_a1] )
        pos_a1 += 0x1
        pos_a2 += 0x1
    except IndexError:
        print(f"INDEX OUT OF RANGE: A1:{hex(pos_a1)}, A2: {hex(pos_a2)}")
        sys.exit()   
    
    return

def back_ref_copy(): 
    
    global d0, d2, d4, a0, a1, a2, pos_a0, pos_a1, pos_a2, pos_a3, r_offset 
    a0 = a2
    
    try:
        d0 = move_b(a1[pos_a1], d0)
        pos_a1 += 0x1
        
        d4 = move_b(a1[pos_a1], d4)
        pos_a1 += 0x1
    except(IndexError):
        print(f"INDEX OUT OF RANGE: A1:{hex(pos_a1)}")
        sys.exit()

    d2 = 0xF  
    d2 = and_b(d4, d2)
    d2 += 0x2 
    d4 = and_w(0xF0, d4)
    
    d4 = lsl_w(0x4, d4)
    d4 = move_b(d0, d4) 
    pos_a0 = pos_a2
    pos_a0 = sub_w(d4, pos_a0)        
    pos_a0 -= 0x1   
    

    for _ in range(0, (d2 + 1)):
        # prevent out of bounds
        if pos_a0 >= len(a0):
            a0.extend([0x00] * (pos_a0 - len(a0) + 0x1))
        try:
            a2.append( a0[pos_a0] )
            pos_a0 += 0x1
            pos_a2 += 0x1
        except(IndexError):
            print(f"INDEX ERROR: pos_a0: {hex(pos_a0)}, pos_a2 :{hex(pos_a2)}")
            sys.exit() 
            
    d2 = 0x0;           
        
    return

def and_b(operand1, operand2):
    bitof1 = operand1 & 0xFF
    bitof2 = operand2 & 0xFF
    
    res = bitof1 & bitof2
    
    return (operand2 & 0xFFFFFF00) | (res & 0xFF)

def and_w(operand1, operand2):
    wordof1 = operand1 & 0xFFFF
    wordof2 = operand2 & 0xFFFF
    
    res = wordof1 & wordof2
    
    return (operand2 & 0xFFFF0000) | (res & 0xFFFF)

def lsl_w(shifts, operand2):
    wordof2 = operand2 & 0xFFFF    
    
    res = wordof2 << shifts

    return (operand2 & 0xFFFF0000) | (res & 0xFFFF)

def lsr_w(shifts, operand2):
    wordof2 = operand2 & 0xFFFF
    
    res = wordof2 >> shifts
    
    
    return (operand2 & 0xFFFF0000) | (res & 0xFFFF)
    
def lsl_b(shifts, operand2):
    bitof2 = operand2 & 0xFFFF
    
    res = bitof2 << shifts
    
    return (operand2 & 0xFFFFFF00) | (res & 0xFF)

def move_b(src, dst):
    return (dst & 0xFFFFFF00) | (src & 0xFF)

def move_w(src, dst):
    return (dst & 0xFFFF0000) | (src & 0xFFFF)

def sub_w(operand1, operand2):
    high = operand2 & 0xFFFF0000
    low1 = operand1 & 0xFFFF
    low2 = operand2 & 0xFFFF

    res = (low2 - low1) & 0xFFFF

    return high | res 

def btst_l(bit_number, operand):    
    res = (
            operand & 
            (1 << bit_number) #0x100
           
           
        ) != 0
    
    return res

def blt_l(operand):    
    return operand < 0x100

def debug_print(source: bytearray, limit):
    if not limit:
        limit = len(source)

    for i in range(0, limit, 16):
        line_end = min(i + 16, limit)
        line_bytes = source[i:line_end]        
        address = f"{i:08X}"        
    
        words = []
        for j in range(0, len(line_bytes), 2):
            if j + 1 < len(line_bytes):
                words.append(f"{line_bytes[j]:02X}{line_bytes[j+1]:02X}")
            else:
                words.append(f"{line_bytes[j]:02X}  ")
        
    
        utf8_string = line_bytes.decode('utf-8', errors='replace')    
        utf8_string = utf8_string.replace('�', '.')
        utf8_string = utf8_string.replace('\n', '.')     
        utf8_string = utf8_string.replace('\r', '.')  
        utf8_string = utf8_string.replace(' ', '.')
    
        print(f"{address}:\t{' '.join(words)}\t\t{utf8_string}")
        
    if limit:
        print(f"... ({hex(len(source) - limit)})")

def main():
    global a0, a1, a2

    parser = argparse.ArgumentParser(description="LZSS decoder")
    parser.add_argument("file", help="Arquivo de entrada (compactado)")
    parser.add_argument("offset", type=lambda x: int(x, 16), help="Offset de origem no arquivo (em hexadecimal)")
    parser.add_argument("size", type=lambda x: int(x, 16), help="Tamanho dos dados comprimidos (em hexadecimal)")
    parser.add_argument("--output", help="Arquivo para salvar a saída descomprimida")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        rom = f.read()

    a1 = bytearray(rom)


    lzss(args.offset, args.size)
    
    print(f"{hex(args.offset)} extracted sucessfully")
    
    #debug_print(a2, 0x500)

    if args.output:
        with open(f"{args.output}.bin", "wb") as out:
            out.write(a2)

if __name__ == "__main__":
    main()
