import sys
import argparse

def get_tile(tileset: bytearray, pattern, pos):
    tile = bytearray()
    TILE_SIZE = 0x20
    TILE_MASK = 0x7FF 
    
    h_flip = (pattern & 0x0800) != 0 
    v_flip = (pattern & 0x1000) != 0  
    tile_index = pattern & TILE_MASK
    
    offset = tile_index << 5    
    try:
        for i in range(TILE_SIZE):
            tile.append(tileset[offset + i])
    except Exception:
        print(f"Index out of range: {hex(offset)} at pos {pos}; pattern: {hex(pattern)}")
        sys.exit(1)
    
    if h_flip or v_flip:
        flipped = bytearray(TILE_SIZE)
        bytes_per_row = 4 
        
        for row in range(8): 
            row_start = row * bytes_per_row
            new_row = row
            
            if v_flip:
                new_row = 7 - row
                
            dest_start = new_row * bytes_per_row
            src_start = row * bytes_per_row
            
            if h_flip:
                flipped[dest_start] = tile[src_start + 3]
                flipped[dest_start + 1] = tile[src_start + 2]
                flipped[dest_start + 2] = tile[src_start + 1]
                flipped[dest_start + 3] = tile[src_start]
            else:
                flipped[dest_start:dest_start + 4] = tile[src_start:src_start + 4]
        
        tile = flipped
    
    return tile

def create_plane(tilemap, tileset):
    output = bytearray()    
    
    for i in range(0, len(tilemap), 2):
        pattern = (tilemap[i + 1] << 8 | tilemap[i]) 
        debug_info = f"offset 0x{i:04X}"
        #print(f"Pattern at {debug_info}: 0x{pattern:04X} " +
        #      f"(H:{'1' if (pattern & 0x0800) else '0'} " +
        #      f"V:{'1' if (pattern & 0x1000) else '0'})")
        
        tile_data = get_tile(tileset, pattern, debug_info)
        output += tile_data
    
    return output

def read_file(filename):
    try:
        with open(filename, 'rb') as f:
            return bytearray(f.read())
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        sys.exit(1)
        
def write_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)
    print(f"Arquivo {filename} gerado com sucesso.")

def main():
    parser = argparse.ArgumentParser(description="Processa um tileset e tilemap com suporte a H/V flips.")
    parser.add_argument("tileset_file", help="Caminho para o arquivo de tileset")
    parser.add_argument("tilemap_file", help="Caminho para o arquivo de tilemap")
    parser.add_argument("-o", "--output", help="Nome do arquivo de saída", default="plane.bin")
    args = parser.parse_args()

    tileset = read_file(args.tileset_file)
    tilemap = read_file(args.tilemap_file)

    output = create_plane(tilemap, tileset)
    write_file(args.output, output)

if __name__ == "__main__":
    main()