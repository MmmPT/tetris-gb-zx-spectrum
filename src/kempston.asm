; Kempston active-high port 1F: R L D U FIRE, bits 0..4.
; Combine with the keyboard. Reject absent-interface values and invalid opposites.
read_kempston:
 PUSH BC
 LD A,($703D)
 OR A
 JR Z,@kempston_done
 XOR A
 IN A,($1F)
 LD C,A
 AND $E0
 JR NZ,@kempston_done
 LD A,C
 AND 3
 CP 3
 JR Z,@kempston_done
 LD A,C
 AND 12
 CP 12
 JR Z,@kempston_done
 BIT 1,C
 JR Z,@kempston_right
 SET 0,D
kempston_right:
 BIT 0,C
 JR Z,@kempston_down
 SET 1,D
kempston_down:
 BIT 2,C
 JR Z,@kempston_fire
 SET 2,D
kempston_fire:
 BIT 4,C
 JR Z,@kempston_up
 LD A,(@mode)
 CP 1
 JR NZ,@kempston_confirm
 SET 4,D
 JR @kempston_up
kempston_confirm:
 SET 5,D
kempston_up:
 BIT 3,C
 JR Z,@kempston_done
 LD A,(@mode)
 CP 6
 JR NZ,@kempston_done
 SET 4,D
kempston_done:
 POP BC
 RET
menu_kempston:
 LD A,$BF
 IN A,($FE)
 AND 4
 LD B,A
 LD A,($70BF)
 LD C,A
 LD A,B
 LD ($70BF),A
 LD A,C
 OR A
 JR Z,@kempston_indicator
 LD A,B
 OR A
 JR NZ,@kempston_indicator
 LD A,($703D)
 XOR 1
 LD ($703D),A
 LD A,1
 CALL @request_sfx
kempston_indicator:
 LD B,20
 LD C,24
 LD A,($703D)
 OR A
 LD A,47
 JR Z,@kempston_draw_indicator
 LD A,19
kempston_draw_indicator:
 JP @draw_tile
