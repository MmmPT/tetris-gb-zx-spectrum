; Only change attributes of completed rows. Their bitmap remains intact.
; White phase uses white ink and paper; colour phase restores each piece.
flash_completed_rows:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 LD IX,$7300
 XOR A
 LD ($73F2),A
flash_next_row:
 LD A,($73F2)
 LD L,A
 LD H,0
 LD DE,$73C0
 ADD HL,DE
 LD A,(HL)
 ADD A,3
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,$5808
 ADD HL,DE
 EX DE,HL
 LD C,10
flash_next_cell:
 LD A,(@flash)
 OR A
 LD A,63
 JR NZ,@flash_store
 LD A,(IX+0)
 CP $80
 JR C,@flash_plain
 CP $90
 JR NC,@flash_plain
 SUB $80
 LD L,A
 LD H,0
 PUSH DE
 LD DE,@piece_attributes
 ADD HL,DE
 POP DE
 LD A,(HL)
 JR @flash_store
flash_plain:
 LD A,56
flash_store:
 LD (DE),A
 INC DE
 INC IX
 DEC C
 JR NZ,@flash_next_cell
 LD A,($73F2)
 INC A
 LD ($73F2),A
 LD B,A
 LD A,(@cleared)
 CP B
 JR NZ,@flash_next_row
 POP IX
 POP HL
 POP DE
 POP BC
 POP AF
 RET

; Copy visible screen to the 128K shadow screen in short safe paging windows.
; 48 chunks x 32 bytes per frame leaves ample time before the next interrupt,
; including contention. The sound ISR always runs with RAM bank 0 mapped.
copy_to_shadow:
 LD HL,$4000
 LD DE,$C000
 LD A,216
 LD ($73F0),A
shadow_next_frame:
 CALL @wait_frame
 LD A,48
 LD ($73F1),A
shadow_chunk:
 DI
 LD BC,$7FFD
 LD A,$17
 OUT (C),A
 LD BC,32
 LDIR
 LD BC,$7FFD
 LD A,$10
 OUT (C),A
 EI
 NOP
 LD A,($73F0)
 DEC A
 LD ($73F0),A
 RET Z
 LD A,($73F1)
 DEC A
 LD ($73F1),A
 JR NZ,@shadow_chunk
 JR @shadow_next_frame
