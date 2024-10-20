import sys

def copy_and_increment_1(source, target: bytearray, offset_source):
    CONTROL_MASK = 0x80
    COUNT_MASK = 0x7F
    
    source_cpos = offset_source
    count = 0
    D_TG = 0

    while True:
        
        if source[source_cpos] == 0x0 and count == 0:               
            source_cpos += 1
            return target
        
        
        if count == 0:
            control = ( source[source_cpos] & CONTROL_MASK ) >> 7
            count = source[source_cpos] & COUNT_MASK

        if control == 0:
            # Sequencial
            source_cpos += 1
            print(f'SEQ\t{hex(source[source_cpos])}\t* {hex(count)}\tAt {hex(source_cpos)}\tinto {hex(D_TG)}')
            current_byte = source[source_cpos]
                        
            for _ in range(count):
                
                #prevent overflow
                if current_byte == 0xFF:
                    current_byte = 0x0 
                                  
                target.append(current_byte)
                D_TG += 1
                current_byte += 1
            source_cpos += 1
            count = 0    
        else:
            # Direct
            source_cpos += 1
            print(f'DIR\t{hex(source[source_cpos])}\t* {hex(count)}\tAt {hex(source_cpos)}\tinto {hex(D_TG)}')

            for _ in range(count):
                target.append(source[source_cpos])
                D_TG += 1
                source_cpos += 1
            count = 0                   

def copy_and_increment_N(source: bytearray, target: bytearray, offset_source, skip, debug):
    CONTROL_MASK = 0x80
    COUNT_MASK = 0x7F

    cpos = offset_source
    count = 0
    tc_pos = 0
    pattern_step = 0
    first_loop = True

    while True:
        
        if source[cpos] == 0 and count == 0 and first_loop == False:
            cpos += 1
            
            #UPDATE TARGET ADDRESS
            pattern_step += 1 
            tc_pos = pattern_step
            
            if pattern_step > skip:
                return target
        
        if count == 0:
            control = ( source[cpos] & CONTROL_MASK ) >> 7
            count = source[cpos] & COUNT_MASK
        #print('___________________________')   
        #debug_print(target)
        
        if control == 0:
            # Same bit
            cpos += 1  
            print(f'SAM\t{hex(source[cpos])}\t* {hex(count)}\tAt {hex(cpos)}\tinto {hex(tc_pos)}')
            current_byte = source[cpos]

            for _ in range(count):
                
                #prevent out of bounds
                if tc_pos >= len(target):
                    target.extend([0x00] * (tc_pos - len(target) + skip))
                    
                target[tc_pos] = current_byte
                tc_pos += skip
                
            cpos += 1                
            count = 0
            
        else:
            # Diff bit
            cpos += 1
            print(f'DIF\t{hex(source[cpos])}\t* {hex(count)}\tAt {hex(cpos)}\tinto {hex(tc_pos)}')
            
            for _ in range(count):
                
                #prevent out of bounds
                if tc_pos >= len(target):
                    target.extend([0x00] * (tc_pos - len(target) + 1))
                    
                target[tc_pos] = source[cpos]
                cpos += 1
                tc_pos += skip
                
            count = 0
                
        first_loop = False
        
def debug_print(source: bytearray):
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
        #utf8_string = utf8_string.replace('\t', '.')
        utf8_string = utf8_string.replace(' ', '.')
    
        print(f"{address}:\t{' '.join(words)}\t\t{utf8_string}")
        
def get_offset(rom: bytearray, p):
    
    word = []
    
    for i in range(0, 3):  
        word.append( get_long_word(rom, (int(p) + (i * 4))) )
        
    return word[0], word[1], word[2]
        
def get_byte(source, pos):
    return source[pos]

def get_word(source, pos, little_endian= False):
    if little_endian:
        return source[pos + 1] << 8 | source[pos]
    
    return source[pos] << 8 | source[pos + 1]

def get_word_mode_5(source, pos):
    return source[pos] << 8 | source[pos]

def get_long_word(source, pos):    
    return source[pos] << 24 | source[pos + 1] << 16 | source[pos + 2] << 8 | source[pos + 3]

def get_word_test(source, pos):

    byte1 =  source[pos + 1] << 8
    byte2 = source[pos]
    
    word = byte1 & 0xF0 | (( byte2 & 0xF0) >> 4)
    
    return word
  
def create_tilemap(rom, offset):
    
    sect1 = bytearray()      #0x0
    sect2 = bytearray()   #0x9000
    sect3 = bytearray()   #0x4000
    
    offsetA, offsetB, offsetC, = get_offset(rom, offset)

    target = copy_and_increment_1(
        rom, 
        sect1, 
        offsetA
    )
    
    #print("==================================")    
    #print(sect1)
    
    sect1.extend([0x0] * 0xF)
    
    sect2 = copy_and_increment_N( 
        sect1, 
        sect2, 
        0, 
        2,
        1
    )
    
    #print("==================================")
    #debug_print(sect1)  
    #print('sect2')  
    #debug_print(sect2)
    
    sect1 = copy_and_increment_N(
        rom, 
        sect1, 
        offsetB,
        1,
        2
    )
    
    #print("==================================")
    #debug_print(sect1)
    
    sect3 = copy_and_increment_N(
        rom, 
        sect3, 
        offsetC,
        1,
        3
    )
    #debug_print(sect3)    
    
    return sect1, sect2, sect3

def get_tile(tileset: bytearray, pattern):
    
    tile = bytearray()
    TILE_MASK = 0x07FF
    TILE_SIZE = 32
    
    offset = ( pattern & TILE_MASK ) << 5
    
    for i in range(0x0, TILE_SIZE):        
        tile.append(tileset[offset + i])
        
    return tile

def get_tile_from_byte(tileset: bytearray, pattern):
    
    tile = bytearray()
    TILE_SIZE = 32
    

    offset = ((pattern << 1) + 0x40) << 5


    for i in range(0x0, TILE_SIZE):
        tile.append(tileset[offset + i])
        
    return tile

def revert_endianess(word):
    
    byte1 = word & 0xFF 
    byte2 = (word >> 8) & 0xFF     

    reversed_word = (byte1 << 8) | byte2
    
    return reversed_word

def swap(byte):
    return int('{:08b}'.format(byte)[::-1], 2)

def create_plane(sect1, sect2, sect3, tileset):
    
    a = bytearray()
    b = bytearray()
    c = bytearray()
    
    """
    for i in range(0, len(sect1) - 1, 2):
        
        pattern = get_word(sect1, i, True)        
        #print(f'TILE ID { hex(tile_id * 0x20) }')
        
        a += get_tile(tileset, pattern)
    """
    
    for i in range(0, len(sect1) - 1, 1):
        word = get_word_mode_5(sect1, i)
        a += get_tile(tileset, word )
        #a += get_tile(tileset, word & 0xFF)
        
    for i in range(0, len(sect2) - 1, 2):
        word = get_word_mode_5(sect2, i)
        b += get_tile(tileset, word )
        #b += get_tile(tileset, word & 0xFF)
        
    for i in range(0, len(sect3) - 1, 2):
        word = get_word_mode_5(sect3, i)
        c += get_tile(tileset, word )
        #c += get_tile(tileset, word & 0xFF)
        
    
    """    
    for i in range(0, len(sect2) - 1, 2):
        
        pattern = get_word(sect2, i)
        #print(f'TILE ID { hex(tile_id * 0x20) }')
        
        b += get_tile(tileset, pattern)
        
    for i in range(0, len(sect3) - 1, 2):
        
        pattern = get_word(sect3, i)        
        #print(f'TILE ID { hex(tile_id * 0x20) }')
        
        c += get_tile(tileset, pattern)]
    """
        
    return a, b, c

if __name__ == "__main__":
    output_name = 'plane'
    ext = '.bin'  
    
    if len(sys.argv) < 4:
        print("Usage: python create_scene.py <rom.bin> <hex offset map> <decompressed graphics.bin> <-o --out>")
        sys.exit(1)
        
    try:
        if len(sys.argv) == 6 or len(sys.argv) == 5:
            if sys.argv[4].lower() == '-o' or sys.argv[4].lower() == '--out':
                output_name = f'plane_{sys.argv[5]}'
                print(output_name)
            else:
                print("Usage: python create_scene.py <rom.bin> <hex offset map> <decompressed graphics.bin> <-o --out>")
                sys.exit(1)
                
    except Exception:
        print('invalid output name.')
        sys.exit(1)
    
    rom_path = sys.argv[1]
    hex_offset_map = sys.argv[2]
    decomp_graph = sys.argv[3]
    
    
    rom = open(rom_path, "rb").read()
    get_offset(rom, 0x54dc)
    tileset = open(decomp_graph, "rb").read()
 
    sect1, sect2, sect3 = create_tilemap(rom, int(hex_offset_map, 16))
    
    debug_print(sect1)
    
    with open('pre.bin', 'wb') as pre:
        pre.write(sect1)
    
    
    

    a, b, c = create_plane(sect1, sect2, sect3, tileset)
    
    with open(output_name + ' a' + ext, 'wb') as f:
        f.write(a)
        
    with open(output_name + ' b' + ext, 'wb') as f:
        f.write(b)
        
    with open(output_name + ' c' + ext, 'wb') as f:
        f.write(c)
    
    #print('=============== SECT 1 ======================')    
    #debug_print(sect1)
    #print('=============== SECT 2 ======================')    
    #debug_print(sect2)
    #print('=============== SECT 3 ======================')    
    #debug_print(sect3)
    
    print('Parsed successfully.')