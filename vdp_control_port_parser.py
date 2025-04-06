def calculate_vram_words(address):
    address = address & 0xFFFF
    C05, C04, C03, C02, C01, C00 = 0, 0, 0, 0, 0, 1

    A15 = (address >> 15) & 1
    A14 = (address >> 14) & 1
    A13 = (address >> 13) & 1
    A12 = (address >> 12) & 1
    A11 = (address >> 11) & 1
    A10 = (address >> 10) & 1
    A09 = (address >> 9) & 1
    A08 = (address >> 8) & 1
    A07 = (address >> 7) & 1
    A06 = (address >> 6) & 1
    A05 = (address >> 5) & 1
    A04 = (address >> 4) & 1
    A03 = (address >> 3) & 1
    A02 = (address >> 2) & 1
    A01 = (address >> 1) & 1
    A00 = (address >> 0) & 1
    
    word1 = (C01 << 15) | (C00 << 14) | (A13 << 13) | (A12 << 12) | (A11 << 11) | \
            (A10 << 10) | (A09 << 9) | (A08 << 8) | (A07 << 7) | (A06 << 6) | \
            (A05 << 5) | (A04 << 4) | (A03 << 3) | (A02 << 2) | (A01 << 1) | A00
    
    word2 = (C05 << 7) | (C04 << 6) | (C03 << 5) | (C02 << 4) | (A15 << 1) | A14
    
    return f"Word 1: 0x{word1:04X}, Word 2: 0x{word2:04X}"

def address_mode(long_word):
    # Long-word (32 bits): CCAA AAAA AAAA AAAA 0000 0000 CCCC 00AA
    long_word = long_word & 0xFFFFFFFF
    
    operations = {
        0b000000: "VRAM read",
        0b000001: "VRAM write",
        0b001000: "CRAM read",
        0b000011: "CRAM write",
        0b000100: "VSRAM read",
        0b000101: "VSRAM write",
        0b001100: "VRAM read, 8-bit (undocumented)"
    }
    
    C01 = (long_word >> 31) & 1
    C00 = (long_word >> 30) & 1
    A13 = (long_word >> 29) & 1
    A12 = (long_word >> 28) & 1
    A11 = (long_word >> 27) & 1
    A10 = (long_word >> 26) & 1
    A09 = (long_word >> 25) & 1
    A08 = (long_word >> 24) & 1
    A07 = (long_word >> 23) & 1
    A06 = (long_word >> 22) & 1
    A05 = (long_word >> 21) & 1
    A04 = (long_word >> 20) & 1
    A03 = (long_word >> 19) & 1
    A02 = (long_word >> 18) & 1
    A01 = (long_word >> 17) & 1
    A00 = (long_word >> 16) & 1
    C05 = (long_word >> 7) & 1
    C04 = (long_word >> 6) & 1
    C03 = (long_word >> 5) & 1
    C02 = (long_word >> 4) & 1
    A15 = (long_word >> 1) & 1
    A14 = (long_word >> 0) & 1
    
    address = (A15 << 15) | (A14 << 14) | (A13 << 13) | (A12 << 12) | (A11 << 11) | \
             (A10 << 10) | (A09 << 9) | (A08 << 8) | (A07 << 7) | (A06 << 6) | \
             (A05 << 5) | (A04 << 4) | (A03 << 3) | (A02 << 2) | (A01 << 1) | A00
    
    code = (C05 << 5) | (C04 << 4) | (C03 << 3) | (C02 << 2) | (C01 << 1) | C00
    
    reserved_bits = (long_word >> 8) & 0xFF 
    reserved_bits |= (long_word >> 2) & 0x3 
    if reserved_bits != 0:
        return "Erro: Bits reservados não são 0 (long-word inválida)."
    
    operation = operations.get(code, "Código inválido")
    return f"Tipo: Long-word, Endereço: 0x{address:04X}, Operação: {operation}"

def register_mode(word):
    word = word & 0xFFFF
    
    if not (word & 0x8000):
        return "Erro: MSB não está setado (inválido para Register Mode)"
    
    adjusted_word = word & 0x7FFF
    
    mode_byte = (adjusted_word >> 8) & 0xFF
    data_byte = adjusted_word & 0xFF        
    
    registers = {
        0x00: "Mode Register 1",
        0x01: "Mode Register 2",
        0x02: "Plane A Name Table Location",
        0x03: "Window Name Table Location",
        0x04: "Plane B Name Table Location",
        0x05: "Sprite Attribute Table Location",
        0x06: "Sprite Pattern Generator Base Address",
        0x07: "Background Colour",
        0x08: "Unused (Mode 5)",
        0x09: "Unused (Mode 5)",
        0x0A: "Horizontal Interrupt Counter",
        0x0B: "Mode Register 3",
        0x0C: "Mode Register 4",
        0x0D: "HScroll Data Location",
        0x0E: "Nametable Pattern Generator Base Address",
        0x0F: "Auto-Increment Value",
        0x10: "Plane Size",
        0x11: "Window Plane Horizontal Position",
        0x12: "Window Plane Vertical Position",
        0x13: "DMA Length (Low)",
        0x14: "DMA Length (High)",
        0x15: "DMA Source (Low)",
        0x16: "DMA Source (Middle)",
        0x17: "DMA Source (High)"
    }
    register_name = registers.get(mode_byte, f"Registrador desconhecido (0x{mode_byte:02X})")
    
    if mode_byte == 0x00:  # Mode Register 1
        L = (data_byte >> 5) & 1
        IE1 = (data_byte >> 4) & 1
        M3 = (data_byte >> 1) & 1
        DE = data_byte & 1
        details = (f"Bits: L={L} (Left 8px blank: {'Yes' if L else 'No'}), "
                  f"IE1={IE1} (H Interrupt: {'Enabled' if IE1 else 'Disabled'}), "
                  f"M3={M3} (H/V Counter Latch: {'Yes' if M3 else 'No'}), "
                  f"DE={DE} (Display Enable: {'Yes' if DE else 'No'})")
    
    elif mode_byte == 0x01:  # Mode Register 2
        VRAM = (data_byte >> 7) & 1
        DE = (data_byte >> 6) & 1
        IE0 = (data_byte >> 5) & 1
        M1 = (data_byte >> 4) & 1
        M2 = (data_byte >> 3) & 1
        M5 = (data_byte >> 2) & 1
        details = (f"Bits: VRAM={VRAM} (Extra 64KB VRAM: {'Yes' if VRAM else 'No'}), "
                  f"DE={DE} (Display Enable: {'Yes' if DE else 'No'}), "
                  f"IE0={IE0} (V Interrupt: {'Enabled' if IE0 else 'Disabled'}), "
                  f"M1={M1} (DMA: {'Enabled' if M1 else 'Disabled'}), "
                  f"M2={M2} (Vert Mode: {'30-cell' if M2 else '28-cell'}), "
                  f"M5={M5} (Video Mode: {'Mega Drive' if M5 else 'Master System'})")
    
    elif mode_byte == 0x02:  # Plane A Name Table Location
        SA16 = (data_byte >> 6) & 1
        SA15 = (data_byte >> 5) & 1
        SA14 = (data_byte >> 4) & 1
        SA13 = (data_byte >> 3) & 1
        vram_addr = (SA15 << 15) | (SA14 << 14) | (SA13 << 13)  # Multiplo de $2000
        details = (f"Bits: SA16={SA16} (128KB Mode: {'Second 64KB' if SA16 else 'First 64KB'}), "
                  f"SA15-SA13={SA15}{SA14}{SA13} (VRAM Addr: 0x{vram_addr:04X})")
    
    elif mode_byte == 0x03:  # Window Name Table Location
        WD16 = (data_byte >> 6) & 1
        WD15 = (data_byte >> 5) & 1
        WD14 = (data_byte >> 4) & 1
        WD13 = (data_byte >> 3) & 1
        WD12 = (data_byte >> 2) & 1
        WD11 = (data_byte >> 1) & 1
        vram_addr = (WD15 << 15) | (WD14 << 14) | (WD13 << 13) | (WD12 << 12) | (WD11 << 11)  # Multiplo de $800
        details = (f"Bits: WD16={WD16} (128KB Mode: {'Second 64KB' if WD16 else 'First 64KB'}), "
                  f"WD15-WD11={WD15}{WD14}{WD13}{WD12}{WD11} (VRAM Addr: 0x{vram_addr:04X})")
    
    elif mode_byte == 0x04:  # Plane B Name Table Location
        SB16 = (data_byte >> 3) & 1
        SB15 = (data_byte >> 2) & 1
        SB14 = (data_byte >> 1) & 1
        SB13 = data_byte & 1
        vram_addr = (SB15 << 15) | (SB14 << 14) | (SB13 << 13)  # Multiplo de $2000
        details = (f"Bits: SB16={SB16} (128KB Mode: {'Second 64KB' if SB16 else 'First 64KB'}), "
                  f"SB15-SB13={SB15}{SB14}{SB13} (VRAM Addr: 0x{vram_addr:04X})")
    
    elif mode_byte == 0x05:  # Sprite Attribute Table Location
        AT16 = (data_byte >> 7) & 1
        AT15 = (data_byte >> 6) & 1
        AT14 = (data_byte >> 5) & 1
        AT13 = (data_byte >> 4) & 1
        AT12 = (data_byte >> 3) & 1
        AT11 = (data_byte >> 2) & 1
        AT10 = (data_byte >> 1) & 1
        AT9 = data_byte & 1
        vram_addr = (AT15 << 15) | (AT14 << 14) | (AT13 << 13) | (AT12 << 12) | \
                    (AT11 << 11) | (AT10 << 10) | (AT9 << 9)  # Multiplo de $200
        details = (f"Bits: AT16={AT16} (128KB Mode: {'Second 64KB' if AT16 else 'First 64KB'}), "
                  f"AT15-AT9={AT15}{AT14}{AT13}{AT12}{AT11}{AT10}{AT9} (VRAM Addr: 0x{vram_addr:04X})")
    
    elif mode_byte == 0x06:  # Sprite Pattern Generator Base Address
        AP16 = (data_byte >> 5) & 1
        details = f"Bits: AP16={AP16} (Sprite Pattern Base: {'Second 64KB' if AP16 else 'First 64KB'})"
    
    elif mode_byte == 0x07:  # Background Colour
        CPT1 = (data_byte >> 5) & 1
        CPT0 = (data_byte >> 4) & 1
        COL3 = (data_byte >> 3) & 1
        COL2 = (data_byte >> 2) & 1
        COL1 = (data_byte >> 1) & 1
        COL0 = data_byte & 1
        palette = (CPT1 << 1) | CPT0
        color = (COL3 << 3) | (COL2 << 2) | (COL1 << 1) | COL0
        details = f"Bits: CPT={CPT1}{CPT0} (Palette Line: {palette}), COL={COL3}{COL2}{COL1}{COL0} (Color Entry: {color})"
    
    elif mode_byte == 0x08 or mode_byte == 0x09:  # Unused
        details = "Não utilizado em Mode 5 (Master System legacy)"
    
    elif mode_byte == 0x0A:  # Horizontal Interrupt Counter
        details = f"Bits: H Counter=0x{data_byte:02X} (Horizontal Interrupt every {data_byte} scanlines)"
    
    elif mode_byte == 0x0B:  # Mode Register 3
        IE2 = (data_byte >> 3) & 1
        VS = (data_byte >> 2) & 1
        HS1 = (data_byte >> 1) & 1
        HS0 = data_byte & 1
        hs_mode = (HS1 << 1) | HS0
        hs_desc = {0b00: "Full screen", 0b01: "Prohibited", 0b10: "Every 8px", 0b11: "Every scanline"}
        details = (f"Bits: IE2={IE2} (External Interrupt: {'Enabled' if IE2 else 'Disabled'}), "
                  f"VS={VS} (Vert Scroll: {'Per screen' if VS == 0 else 'Per 2 cells'}), "
                  f"HS={HS1}{HS0} (Horz Scroll: {hs_desc.get(hs_mode, 'Unknown')})")
    
    elif mode_byte == 0x0C:  # Mode Register 4
        RS0 = (data_byte >> 7) & 1
        VSY = (data_byte >> 6) & 1
        HSY = (data_byte >> 5) & 1
        SPR = (data_byte >> 4) & 1
        SHI = (data_byte >> 3) & 1
        LSM1 = (data_byte >> 2) & 1
        LSM0 = (data_byte >> 1) & 1
        RS1 = data_byte & 1
        lsm_mode = (LSM1 << 1) | LSM0
        lsm_desc = {0b00: "No interlace", 0b01: "Interlace", 0b10: "Prohibited", 0b11: "Double resolution"}
        details = (f"Bits: RS={RS0}{RS1} (Horz Res: {'40 tiles' if RS0 and RS1 else '32 tiles'}), "
                  f"VSY={VSY} (VSync: {'Pixel clock' if VSY else 'Normal'}), "
                  f"HSY={HSY} (HSync tweak), "
                  f"SPR={SPR} (Ext Pixel Bus: {'Enabled' if SPR else 'Disabled'}), "
                  f"SHI={SHI} (Shadow/Highlight: {'Enabled' if SHI else 'Disabled'}), "
                  f"LSM={LSM1}{LSM0} ({lsm_desc.get(lsm_mode, 'Unknown')})")
    
    elif mode_byte == 0x0D:  # HScroll Data Location
        HS16 = (data_byte >> 6) & 1
        HS15 = (data_byte >> 5) & 1
        HS14 = (data_byte >> 4) & 1
        HS13 = (data_byte >> 3) & 1
        HS12 = (data_byte >> 2) & 1
        HS11 = (data_byte >> 1) & 1
        HS10 = data_byte & 1
        vram_addr = (HS15 << 15) | (HS14 << 14) | (HS13 << 13) | (HS12 << 12) | (HS11 << 11) | (HS10 << 10)
        details = (f"Bits: HS16={HS16} (128KB Mode: {'Second 64KB' if HS16 else 'First 64KB'}), "
                  f"HS15-HS10={HS15}{HS14}{HS13}{HS12}{HS11}{HS10} (VRAM Addr: 0x{vram_addr:04X})")
    
    elif mode_byte == 0x0E:  # Nametable Pattern Generator Base Address
        PB16 = (data_byte >> 4) & 1
        PA16 = data_byte & 1
        details = (f"Bits: PB16={PB16} (Plane B Base: {'Second 64KB' if PB16 else 'First 64KB'}), "
                  f"PA16={PA16} (Plane A/Window Base: {'Second 64KB' if PA16 else 'First 64KB'})")
    
    elif mode_byte == 0x0F:  # Auto-Increment Value
        details = f"Bits: Increment Value=0x{data_byte:02X} (Add {data_byte} after VRAM access)"
    
    elif mode_byte == 0x10:  # Plane Size
        VSZ1 = (data_byte >> 5) & 1
        VSZ0 = (data_byte >> 4) & 1
        HSZ1 = (data_byte >> 1) & 1
        HSZ0 = data_byte & 1
        size_desc = {0b00: "32 tiles", 0b01: "64 tiles", 0b10: "Prohibited", 0b11: "128 tiles"}
        vsz = (VSZ1 << 1) | VSZ0
        hsz = (HSZ1 << 1) | HSZ0
        details = (f"Bits: VSZ={VSZ1}{VSZ0} (Vert Size: {size_desc.get(vsz, 'Unknown')}), "
                  f"HSZ={HSZ1}{HSZ0} (Horz Size: {size_desc.get(hsz, 'Unknown')})")
    
    elif mode_byte == 0x11:  # Window Plane Horizontal Position
        RGHT = (data_byte >> 7) & 1
        WHP5 = (data_byte >> 4) & 1
        WHP4 = (data_byte >> 3) & 1
        WHP3 = (data_byte >> 2) & 1
        WHP2 = (data_byte >> 1) & 1
        WHP1 = data_byte & 1
        whp = (WHP5 << 4) | (WHP4 << 3) | (WHP3 << 2) | (WHP2 << 1) | WHP1
        details = (f"Bits: RGHT={RGHT} (Direction: {'Right' if RGHT else 'Left'}), "
                  f"WHP={WHP5}{WHP4}{WHP3}{WHP2}{WHP1} (Cells: {whp * 2})")
    
    elif mode_byte == 0x12:  # Window Plane Vertical Position
        DOWN = (data_byte >> 7) & 1
        WVP5 = (data_byte >> 4) & 1
        WVP4 = (data_byte >> 3) & 1
        WVP3 = (data_byte >> 2) & 1
        WVP2 = (data_byte >> 1) & 1
        WVP1 = data_byte & 1
        wvp = (WVP5 << 4) | (WVP4 << 3) | (WVP3 << 2) | (WVP2 << 1) | WVP1
        details = (f"Bits: DOWN={DOWN} (Direction: {'Down' if DOWN else 'Up'}), "
                  f"WVP={WVP5}{WVP4}{WVP3}{WVP2}{WVP1} (Cells: {wvp * 2})")
    
    elif mode_byte == 0x13:  # DMA Length (Low)
        details = f"Bits: DMA Length Low Byte=0x{data_byte:02X}"
    
    elif mode_byte == 0x14:  # DMA Length (High)
        details = f"Bits: DMA Length High Byte=0x{data_byte:02X}"
    
    elif mode_byte == 0x15:  # DMA Source (Low)
        details = f"Bits: DMA Source Low Byte=0x{data_byte:02X}"
    
    elif mode_byte == 0x16:  # DMA Source (Middle)
        details = f"Bits: DMA Source Middle Byte=0x{data_byte:02X}"
    
    elif mode_byte == 0x17:  # DMA Source (High)
        DMD1 = (data_byte >> 7) & 1
        DMD0 = (data_byte >> 6) & 1
        H5 = (data_byte >> 5) & 1
        H4 = (data_byte >> 4) & 1
        H3 = (data_byte >> 3) & 1
        H2 = (data_byte >> 2) & 1
        H1 = (data_byte >> 1) & 1
        H0 = data_byte & 1
        dma_mode = {0b00: "M68K Copy", 0b01: "M68K Copy", 0b10: "DMA Fill", 0b11: "DMA Copy"}
        details = (f"Bits: DMD={DMD1}{DMD0} (Mode: {dma_mode.get((DMD1 << 1) | DMD0, 'Unknown')}), "
                  f"H5-H0={H5}{H4}{H3}{H2}{H1}{H0}")
    
    else:
        details = f"Dados: 0x{data_byte:02X} (sem detalhes para registrador desconhecido)"
    
    return (f"Tipo: Word (Register Mode), Registrador: {register_name}, "
            f"Valor: 0x{data_byte:02X}, {details}")

def main():
    while True:
        print("\n1. Calcular words para VRAM write a partir de endereço")
        print("2. Extrair informações a partir de long-word ou word")
        print("3. Sair")
        choice = input("Escolha uma opção (1-3): ")
        
        if choice == "1":
            try:
                addr_input = input("Digite o endereço (decimal ou hex, ex: 0x1234): ")
                if addr_input.startswith("0x"):
                    address = int(addr_input, 16)
                else:
                    address = int(addr_input)
                result = calculate_vram_words(address)
                print(result)
            except ValueError:
                print("Erro: Endereço inválido.")
        
        elif choice == "2":
            try:
                value_input = input("Digite o valor (hex, ex: 0x1234 para word, 0x12345678 para long-word): ")
                if value_input.startswith("0x"):
                    value = int(value_input, 16)
                else:
                    value = int(value_input, 16)
                
                is_long_word = (value > 0xFFFF) or (len(value_input.strip("0x")) > 4)
                
                if is_long_word:
                    result = address_mode(value)
                else:
                    result = register_mode(value)
                print(result)
            except ValueError:
                print("Erro: Valor inválido.")
        
        elif choice == "3":
            print("Saindo...")
            break
        
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()