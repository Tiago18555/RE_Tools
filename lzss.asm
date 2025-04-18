; =============== S U B R O U T I N E =======================================

LZSS_Decomp_Main:

; A1: source
; A2: target
; D0: length

    movem.l    A2-A0/D4-D0,-(SP)
    moveq      #$8,D3
    movea.l    A1,A3
    adda.w     D0,A3

load_next_control_byte:                                        
    move.b     (A1)+,D1
    ori.w      #$FF00,D1
    bra.b      shift_right_and_check_carry

test_current_bit_in_control_byte:                                      
    btst.l     D3,D1
    beq.b      load_next_control_byte

shift_right_and_check_carry:                                          
    lsr.w      #$1,D1
    bcc.w      back_ref_copy
    move.b     (A1)+,(A2)+
    cmpa.l     A1,A3
    bhi.b      test_current_bit_in_control_byte
    bra.b      end

back_ref_copy:                                          
    move.b     (A1)+,D0b
    move.b     (A1)+,D4b
    moveq      #$f,D2
    and.b      D4,D2
    addq.w     #$2,D2
    andi.w     #$f0,D4
    lsl.w      #$4,D4
    move.b     D0,D4
    movea.l    A2,A0
    suba.w     D4,A0
    subq.l     #$1,A0

loc_loop:                                            
    move.b     (A0)+,(A2)+
    dbf        D2,loc_loop
    cmpa.l     A1,A3
    bhi.b      test_current_bit_in_control_byte

end:                                          
    move.l     A2,D0
    addq.l     #$1,D0
    bclr.l     #$0,D0
    movea.l    D0,A0
    movem.l    (SP)+,D0-D4/A0-A2
    rts