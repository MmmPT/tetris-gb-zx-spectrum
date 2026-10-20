; Tetris GB -> ZX Spectrum 128K + AY. Native Z80 implementation.
; Original Game Boy sprite matrices and tile art; 50 Hz timings adapted.
entry:
 DI
 LD SP,$7FFE
 ; IM2 vector table at 7400, trampoline at 7676; game code stays in fixed RAM.
 LD HL,$7400
 LD DE,$7401
 LD BC,256
 LD (HL),$76
 LDIR
 LD A,$C3
 LD ($7676),A
 LD HL,@music_interrupt
 LD ($7677),HL
 LD A,$74
 LD I,A
 IM 2
 XOR A
 OUT ($FE),A
 LD HL,$7000
 LD DE,$7001
 LD BC,$01FF
 LD (HL),A
 LDIR
 LD A,1
 LD (@music_on),A
 LD ($703D),A
 LD HL,12345
 LD (@rng),HL
 CALL @init_records
 CALL @ay_init
 EI
 CALL @show_menu
main:
 CALL @wait_frame
 CALL @read_keys
 CALL @check_soft_reset
 LD A,(@edge)
 BIT 7,A
 CALL NZ,@toggle_music
 LD A,(@mode)
 OR A
 JP Z,@menu_input
 CP 2
 JP Z,@paused_input
 CP 5
 JP Z,@summary_input
 CP 6
 JP Z,@name_input
 CP 7
 JP Z,@records_input
 CP 8
 JP Z,@ending_input
 CP 3
 JP NC,@end_input
 LD A,(@edge)
 BIT 5,A
 JP NZ,@pause_game
 BIT 6,A
 CALL NZ,@toggle_preview
 CALL @erase_piece
 CALL @input_piece
 CALL @fall_piece
 LD A,(@mode)
 CP 1
 CALL Z,@draw_piece
 JP @main

show_menu:
 LD A,3
 CALL @select_song
 LD HL,@menu_screen
 CALL @load_screen
 XOR A
 LD (@mode),A
 CALL @menu_values
 LD HL,0
 LD (@idle),HL
 RET
menu_values:
 LD A,(@startlevel)
 LD B,17
 LD C,21
 CALL @draw_tile
 LD A,(@gametype)
 OR A
 LD A,10
 JR Z,@menu_letter
 LD A,11
menu_letter:
 LD B,17
 LD C,7
 CALL @draw_tile
 LD A,(@height)
 LD B,19
 LD C,25
 CALL @draw_tile
 RET
menu_input:
 CALL @menu_extra
 LD A,(@mode)
 OR A
 JP NZ,@main
 LD A,(@edge)
 BIT 0,A
 CALL NZ,@level_left
 LD A,(@edge)
 BIT 1,A
 CALL NZ,@level_right
 LD A,$7F
 IN A,($FE)
 AND 16
 LD B,A
 LD A,(@menu_b)
 LD C,A
 LD A,B
 LD (@menu_b),A
 LD A,C
 OR A
 JR Z,@menu_check_h
 LD A,B
 OR A
 CALL Z,@toggle_type
menu_check_h:
 LD A,$BF
 IN A,($FE)
 AND 16
 LD B,A
 LD A,(@menu_h)
 LD C,A
 LD A,B
 LD (@menu_h),A
 LD A,C
 OR A
 JR Z,@menu_check_start
 LD A,B
 OR A
 CALL Z,@height_next
menu_check_start:
 LD A,(@edge)
 BIT 5,A
 JP Z,@main
 LD A,2
 CALL @request_sfx
 CALL @new_game
 JP @main
level_left:
 LD A,(@startlevel)
 OR A
 JR NZ,@level_dec
 LD A,10
level_dec:
 DEC A
 LD (@startlevel),A
 LD A,1
 CALL @request_sfx
 JP @menu_values
level_right:
 LD A,(@startlevel)
 INC A
 CP 10
 JR C,@level_store
 XOR A
level_store:
 LD (@startlevel),A
 LD A,1
 CALL @request_sfx
 JP @menu_values
toggle_type:
 LD A,(@gametype)
 LD L,A
 LD H,0
 LD DE,$70B8
 ADD HL,DE
 LD A,(@startlevel)
 LD (HL),A
 LD A,(@gametype)
 XOR 1
 LD (@gametype),A
 LD L,A
 LD H,0
 LD DE,$70B8
 ADD HL,DE
 LD A,(HL)
 LD (@startlevel),A
 LD A,1
 CALL @request_sfx
 JP @menu_values
height_next:
 LD A,(@height)
 INC A
 CP 6
 JR C,@height_store
 XOR A
height_store:
 LD (@height),A
 JP @menu_values

new_game:
 CALL @reset_result
 LD A,(@music_choice)
 CALL @select_song
 LD HL,($5C78)
 LD A,R
 XOR L
 LD L,A
 LD A,H
 OR L
 JR NZ,@seed_ready
 INC HL
seed_ready:
 LD A,(@demo)
 OR A
 JR Z,@normal_seed
 LD HL,$3456
normal_seed:
 LD (@rng),HL
 XOR A
 LD HL,@board
 LD DE,@board+1
 LD BC,179
 LD (HL),A
 LDIR
 LD HL,@score
 LD DE,@score+1
 LD BC,6
 LD (HL),A
 LDIR
 LD (@softcount),A
 LD (@softtimer),A
 LD (@repeat),A
 LD (@lastdir),A
 LD (@hidden),A
 LD (@cleared),A
 LD ($7039),A
 LD ($703A),A
 LD ($703B),A
 LD ($703C),A
 LD (@pieces),A
 LD (@pieces+1),A
 LD A,25
 LD (@remaining),A
 LD A,(@startlevel)
 LD (@level),A
 LD A,(@gametype)
 OR A
 LD HL,@game_a_screen
 JR Z,@new_screen
 LD HL,@game_b_screen
new_screen:
 CALL @load_screen
 LD A,(@gametype)
 OR A
 CALL NZ,@garbage
 CALL @render_board
 CALL @random_piece
 LD (@next),A
 LD A,1
 LD (@mode),A
 CALL @spawn
 CALL @hud
 RET

garbage:
 LD A,(@height)
 ADD A,A
 OR A
 RET Z
 LD B,A
 LD A,18
 SUB B
 PUSH BC
 CALL @row_pointer
 LD (@temp_ptr),HL
 POP BC
garbage_row:
 PUSH BC
 LD HL,(@temp_ptr)
 LD B,10
 LD C,0
garbage_cell:
 PUSH BC
 PUSH HL
 CALL @random_byte
 POP HL
 POP BC
 AND 1
 JR Z,@garbage_hole
 PUSH BC
 PUSH HL
 CALL @random_byte
 POP HL
 POP BC
 AND 7
 OR $80
 INC C
 LD (HL),A
garbage_hole:
 INC HL
 DJNZ @garbage_cell
 LD A,C
 CP 10
 JR NZ,@garbage_done_row
 DEC HL
 LD (HL),0
 INC HL
garbage_done_row:
 LD (@temp_ptr),HL
 POP BC
 DJNZ @garbage_row
 RET

spawn:
 LD A,(@next)
 LD (@piece),A
 CALL @random_piece
 LD (@next),A
 XOR A
 LD (@rot),A
 LD (@softcount),A
 LD (@softtimer),A
 LD (@repeat),A
 LD (@lastdir),A
 LD A,(@keys)
 AND 4
 LD (@softgate),A
 LD A,3
 LD (@px),A
 LD A,254
 LD (@py),A
 LD HL,(@pieces)
 INC HL
 LD (@pieces),HL
 CALL @reset_gravity
 CALL @render_preview
 RET
reset_gravity:
 LD A,(@heart)
 LD B,A
 LD A,(@level)
 INC B
 DEC B
 JR Z,@normal_gravity
 ADD A,10
normal_gravity:
 CP 21
 JR C,@gravity_level_ok
 LD A,20
gravity_level_ok:
 LD L,A
 LD H,0
 ADD HL,HL
 LD BC,@gravity
 ADD HL,BC
 LD B,(HL)
 INC HL
 LD A,($703A)
 ADD A,(HL)
 LD ($703A),A
 JR NC,@gravity_interval
 INC B
gravity_interval:
 LD A,B
 LD (@falltimer),A
 RET

candidate_current:
 LD A,(@px)
 LD (@cx),A
 LD A,(@py)
 LD (@cy),A
 LD A,(@rot)
 LD (@cr),A
 RET
shape_pointer:
 LD A,(@piece)
 ADD A,A
 ADD A,A
 LD B,A
 LD A,(@cr)
 ADD A,B
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 LD E,L
 LD D,H
 ADD HL,HL
 ADD HL,DE
 LD DE,@shapes
 ADD HL,DE
 RET
collision:
 CALL @shape_pointer
 LD A,(@cx)
 LD D,A
 LD A,(@cy)
 LD E,A
 LD B,4
collision_cell:
 LD A,(HL)
 INC HL
 ADD A,D
 CP 10
 JP NC,@collision_yes
 LD (@cellx),A
 LD A,(HL)
 INC HL
 ADD A,E
 BIT 7,A
 JR NZ,@collision_above
 CP 18
 JP NC,@collision_yes
 PUSH HL
 PUSH BC
 PUSH DE
 CALL @cell_pointer
 LD A,(HL)
 OR A
 POP DE
 POP BC
 POP HL
 JP NZ,@collision_yes
collision_above:
 INC HL
 DJNZ @collision_cell
 XOR A
 RET
collision_yes:
 LD A,1
 OR A
 RET
cell_pointer:
 LD L,A
 LD H,0
 LD B,H
 LD C,L
 ADD HL,HL
 ADD HL,HL
 ADD HL,BC
 ADD HL,HL
 LD A,(@cellx)
 LD C,A
 LD B,0
 ADD HL,BC
 LD BC,@board
 ADD HL,BC
 RET
row_pointer:
 LD (@rowtemp),A
 XOR A
 LD (@cellx),A
 LD A,(@rowtemp)
 JP @cell_pointer

input_piece:
 LD A,(@edge)
 BIT 3,A
 JR Z,@try_cw
 CALL @candidate_current
 LD A,(@cr)
 INC A
 AND 3
 LD (@cr),A
 CALL @apply_rotation
try_cw:
 LD A,(@edge)
 BIT 4,A
 JR Z,@horizontal
 CALL @candidate_current
 LD A,(@cr)
 DEC A
 AND 3
 LD (@cr),A
 CALL @apply_rotation
horizontal:
 LD A,(@keys)
 AND 3
 LD D,0
 BIT 1,A
 JR Z,@test_left
 LD D,2
 JR @direction_ready
test_left:
 BIT 0,A
 JR Z,@direction_ready
 LD D,1
direction_ready:
 LD A,D
 OR A
 JR NZ,@direction_held
 LD (@lastdir),A
 RET
direction_held:
 LD A,(@lastdir)
 CP D
 JR NZ,@new_direction
 LD A,(@repeat)
 DEC A
 LD (@repeat),A
 RET NZ
 CALL @repeat_period
 JR @repeat_ready
new_direction:
 LD A,D
 LD (@lastdir),A
 CALL @repeat_initial
repeat_ready:
 LD (@repeat),A
 PUSH DE
 CALL @candidate_current
 POP DE
 LD A,(@cx)
 CP 255
 ; Signed base X is allowed when all four cells remain in bounds.
 LD A,D
 CP 1
 LD A,(@cx)
 JR NZ,@move_right
 DEC A
 JR @move_test
move_right:
 INC A
move_test:
 LD (@cx),A
 CALL @collision
 JR Z,@move_accepted
 LD A,1
 LD (@repeat),A
 RET
move_accepted:
 LD A,(@cx)
 LD (@px),A
 LD A,4
 CALL @request_sfx
 RET
apply_rotation:
 CALL @collision
 RET NZ
 LD A,(@cr)
 LD (@rot),A
 LD A,3
 CALL @request_sfx
 RET

fall_piece:
 LD A,(@keys)
 BIT 2,A
 JR NZ,@soft_gate_check
 XOR A
 LD (@softgate),A
soft_gate_check:
 LD A,(@softgate)
 OR A
 JP NZ,@normal_fall
 LD A,(@keys)
 AND 7
 CP 4
 JR NZ,@normal_fall
 LD A,(@softtimer)
 OR A
 JR Z,@soft_step
 DEC A
 LD (@softtimer),A
 RET
soft_step:
 CALL @soft_interval
 LD (@softtimer),A
 LD A,(@softcount)
 INC A
 LD (@softcount),A
 JP @try_drop
normal_fall:
 XOR A
 LD (@softcount),A
 LD (@softtimer),A
 LD A,(@falltimer)
 DEC A
 LD (@falltimer),A
 RET NZ
 CALL @reset_gravity
try_drop:
 CALL @candidate_current
 LD A,(@cy)
 INC A
 LD (@cy),A
 CALL @collision
 JP NZ,@lock_piece
 LD A,(@cy)
 LD (@py),A
 RET

; Draw or erase exactly the four active cells.
draw_piece:
 XOR A
 LD (@erase),A
 JP @paint_piece
erase_piece:
 LD A,1
 LD (@erase),A
paint_piece:
 CALL @candidate_current
 CALL @shape_pointer
 LD B,4
paint_cell:
 LD A,(@px)
 LD D,A
 LD A,(HL)
 ADD A,D
 LD C,A
 INC HL
 LD A,(@py)
 LD D,A
 LD A,(HL)
 ADD A,D
 INC HL
 BIT 7,A
 JR NZ,@paint_skip
 CP 18
 JR NC,@paint_skip
 PUSH BC
 LD B,A
 LD A,(HL)
 LD D,A
 LD A,(@erase)
 OR A
 LD A,D
 JR Z,@paint_color
 PUSH HL
 PUSH BC
 PUSH DE
 LD A,C
 LD (@cellx),A
 LD A,B
 CALL @cell_pointer
 LD A,(HL)
 OR A
 JR NZ,@paint_background
 LD A,$2F
paint_background:
 LD (@tiletemp),A
 POP DE
 POP BC
 POP HL
 LD A,(@tiletemp)
paint_color:
 PUSH HL
 LD D,A
 LD A,B
 ADD A,3
 LD B,A
 LD A,C
 ADD A,8
 LD C,A
 LD A,D
 CALL @draw_game_tile
 POP HL
 POP BC
paint_skip:
 INC HL
 DJNZ @paint_cell
 RET

lock_piece:
 LD A,(@py)
 CP 254
 JR NZ,@lock_normal
 LD A,(@px)
 CP 3
 JR NZ,@lock_normal
 LD A,($7039)
 INC A
 LD ($7039),A
 CP 2
 JP NC,@game_over
lock_normal:
 CALL @candidate_current
 CALL @shape_pointer
 LD B,4
lock_cell:
 LD A,(@px)
 LD D,A
 LD A,(HL)
 ADD A,D
 LD (@cellx),A
 INC HL
 LD A,(@py)
 LD D,A
 LD A,(HL)
 ADD A,D
 INC HL
 BIT 7,A
 JR NZ,@lock_above
 PUSH HL
 PUSH BC
 CALL @cell_pointer
 POP BC
 POP DE
 LD A,(DE)
 LD (HL),A
 EX DE,HL
lock_above:
 INC HL
 DJNZ @lock_cell
 ; Award the consecutive soft-drop distance, excluding the blocked step.
 LD A,(@softcount)
 OR A
 JR Z,@lock_score_done
 DEC A
 JR Z,@lock_score_done
 LD B,A
soft_points:
 LD HL,(@soft_total)
 INC HL
 LD (@soft_total),HL
 PUSH BC
 LD DE,1
 LD C,0
 CALL @add_score
 POP BC
 DJNZ @soft_points
lock_score_done:
 CALL @draw_piece
 LD A,5
 CALL @request_sfx
 CALL @clear_lines
 CALL @hud
 LD A,(@mode)
 CP 1
 RET NZ
 CALL @spawn
 RET

clear_lines:
 XOR A
 LD (@cleared),A
 LD A,17
 LD (@scanrow),A
clear_scan:
 LD A,(@scanrow)
 CALL @row_pointer
 PUSH HL
 LD B,10
full_test:
 LD A,(HL)
 OR A
 JR Z,@not_full
 INC HL
 DJNZ @full_test
 POP HL
 PUSH HL
 LD A,(@cleared)
 LD L,A
 LD H,0
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 ADD HL,HL
 LD DE,$7300
 ADD HL,DE
 EX DE,HL
 POP HL
 PUSH HL
 LD BC,10
 LDIR
 LD A,(@cleared)
 LD L,A
 LD H,0
 LD DE,$73C0
 ADD HL,DE
 LD A,(@scanrow)
 LD (HL),A
 POP HL
 LD B,10
mark_full:
 LD (HL),255
 INC HL
 DJNZ @mark_full
 LD A,(@cleared)
 INC A
 LD (@cleared),A
 JR @scan_next
not_full:
 POP HL
scan_next:
 LD A,(@scanrow)
 DEC A
 LD (@scanrow),A
 CP 1
 JR NZ,@clear_scan
 LD A,(@cleared)
 OR A
 JR NZ,@animate_clear
 JP @render_board
animate_clear:
 LD A,(@cleared)
 CP 4
 LD A,6
 JR NZ,@clear_sound
 LD A,7
clear_sound:
 CALL @request_sfx
 LD B,7
flash_loop:
 PUSH BC
 LD A,B
 AND 1
 LD (@flash),A
 CALL @wait_frame
 CALL @flash_completed_rows
 LD B,7
clear_flash_wait:
 PUSH BC
 CALL @wait_frame
 POP BC
 DJNZ @clear_flash_wait
 POP BC
 DJNZ @flash_loop
 ; Copy the stable final white phase to bank 7; visible bank 5 stays untouched.
 CALL @copy_to_shadow
 CALL @wait_frame
 LD BC,$7FFD
 LD A,$18
 OUT (C),A

 LD A,17
 LD (@scanrow),A
 LD (@writerow),A
compact_loop:
 LD A,(@scanrow)
 CALL @row_pointer
 LD A,(HL)
 CP 255
 JR Z,@compact_skip
 PUSH HL
 LD A,(@writerow)
 CALL @row_pointer
 EX DE,HL
 POP HL
 LD BC,10
 LDIR
 LD A,(@writerow)
 DEC A
 LD (@writerow),A
compact_skip:
 LD A,(@scanrow)
 DEC A
 LD (@scanrow),A
 CP 255
 JR NZ,@compact_loop
 LD A,(@writerow)
 CP 255
 JR Z,@compact_done
clear_top:
 PUSH AF
 CALL @row_pointer
 LD B,10
clear_top_row:
 LD (HL),0
 INC HL
 DJNZ @clear_top_row
 POP AF
 DEC A
 CP 255
 JR NZ,@clear_top
compact_done:
 LD A,9
 CALL @request_sfx
 CALL @award_lines
 ; Draw all compacted cells into bank 5 while the ULA displays bank 7.
 CALL @render_board
 CALL @wait_frame
 LD BC,$7FFD
 LD A,$10
 OUT (C),A
 RET

award_lines:
 CALL @count_clear
 LD A,(@cleared)
 LD B,A
 LD A,(@gametype)
 OR A
 JR Z,@line_count
 LD A,(@remaining)
 SUB B
 JR C,@b_done
 JR Z,@b_done
 LD (@remaining),A
 JR @line_count
b_done:
 LD A,5
 CALL @select_song
 XOR A
 LD (@remaining),A
 LD A,4
 LD (@mode),A
line_count:
 LD A,(@cleared)
 LD B,A
increment_lines:
 LD HL,(@lines)
 LD DE,9999
 OR A
 SBC HL,DE
 JR NC,@lines_capped
 LD HL,(@lines)
 INC HL
 LD (@lines),HL
 LD A,(@lines_bcd)
 ADD A,1
 DAA
 LD (@lines_bcd),A
 LD A,(@lines_bcd+1)
 ADC A,0
 DAA
 LD (@lines_bcd+1),A
lines_capped:
 DJNZ @increment_lines
 LD A,(@cleared)
 DEC A
 ADD A,A
 LD L,A
 LD H,0
 LD DE,@awards
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD A,(@level)
 INC A
 LD B,A
award_loop:
 PUSH BC
 PUSH DE
 LD C,0
 CALL @add_score
 POP DE
 POP BC
 DJNZ @award_loop
 LD A,(@gametype)
 OR A
 RET NZ
level_check:
 LD A,(@level)
 CP 20
 RET NC
 INC A
 LD L,A
 LD H,0
 LD B,H
 LD C,L
 ADD HL,HL
 ADD HL,HL
 ADD HL,BC
 ADD HL,HL
 EX DE,HL
 LD HL,(@lines)
 OR A
 SBC HL,DE
 RET C
 LD A,(@level)
 INC A
 LD (@level),A
 LD A,8
 CALL @request_sfx
 CALL @reset_gravity
 JR @level_check

add_score:
 LD A,(@score)
 ADD A,E
 DAA
 LD (@score),A
 LD A,(@score+1)
 ADC A,D
 DAA
 LD (@score+1),A
 LD A,(@score+2)
 ADC A,C
 DAA
 LD (@score+2),A
 RET NC
 LD A,$99
 LD (@score),A
 LD (@score+1),A
 LD (@score+2),A
 RET

render_board:
 LD HL,@board
 LD B,18
 LD D,3
board_row:
 PUSH BC
 LD C,8
 LD B,10
board_column:
 PUSH BC
 LD A,(HL)
 INC HL
 OR A
 JR NZ,@board_nonempty
 LD A,$2F
board_nonempty:
 CP 255
 JR NZ,@board_color
 LD A,(@flash)
 OR A
 LD A,255
 JR NZ,@board_color
 LD A,$2F
board_color:
 PUSH HL
 LD B,D
 CALL @draw_game_tile
 POP HL
 POP BC
 INC C
 DJNZ @board_column
 INC D
 POP BC
 DJNZ @board_row
 RET
render_preview:
 LD B,4
 LD D,16
preview_clear_row:
 PUSH BC
 LD C,21
 LD B,4
preview_clear_col:
 PUSH BC
 LD B,D
 LD A,$2F
 CALL @draw_game_tile
 POP BC
 INC C
 DJNZ @preview_clear_col
 INC D
 POP BC
 DJNZ @preview_clear_row
 LD A,(@hidden)
 OR A
 RET NZ
 LD A,(@piece)
 PUSH AF
 LD A,(@next)
 LD (@piece),A
 XOR A
 LD (@cr),A
 CALL @shape_pointer
 POP AF
 LD (@piece),A
 LD B,4
preview_cell:
 PUSH BC
 LD A,(HL)
 INC HL
 ADD A,21
 LD C,A
 LD A,(HL)
 INC HL
 ADD A,15
 LD B,A
 LD A,(HL)
 INC HL
 PUSH HL
 CALL @draw_game_tile
 POP HL
 POP BC
 DJNZ @preview_cell
 RET
hud:
 LD A,(@gametype)
 OR A
 JR NZ,@hud_b
 LD A,(@score+2)
 LD B,6
 LD C,19
 CALL @draw_bcd
 LD A,(@score+1)
 LD C,21
 CALL @draw_bcd
 LD A,(@score)
 LD C,23
 CALL @draw_bcd
 LD A,(@level)
 LD B,10
 LD C,22
 CALL @draw_decimal
 LD A,(@lines_bcd+1)
 LD B,13
 LD C,20
 CALL @draw_bcd
 LD A,(@lines_bcd)
 LD C,22
 JP @draw_bcd
hud_b:
 LD A,(@level)
 LD B,5
 LD C,22
 CALL @draw_decimal
 LD A,(@height)
 LD B,8
 LD C,22
 CALL @draw_tile
 LD A,(@remaining)
 LD B,13
 LD C,22
 CALL @draw_decimal
 LD A,(@mode)
 CP 4
 JP Z,@success
 RET
draw_bcd:
 PUSH AF
 RRCA
 RRCA
 RRCA
 RRCA
 AND 15
 CALL @draw_tile
 INC C
 POP AF
 AND 15
 CALL @draw_tile
 DEC C
 RET
draw_decimal:
 LD D,0
decimal_tens:
 CP 10
 JR C,@decimal_ready
 SUB 10
 INC D
 JR @decimal_tens
decimal_ready:
 LD E,A
 LD A,D
 CALL @draw_tile
 INC C
 LD A,E
 CALL @draw_tile
 DEC C
 RET

toggle_preview:
 LD A,(@hidden)
 XOR 1
 LD (@hidden),A
 JP @render_preview
toggle_music:
 LD A,(@music_on)
 XOR 1
 LD (@music_on),A
 RET
pause_game:
 LD A,10
 CALL @request_sfx
 LD A,2
 LD (@mode),A
 LD HL,@pause_text
 LD B,11
 LD C,8
 CALL @print_text
 JP @main
paused_input:
 LD A,(@edge)
 BIT 5,A
 JP Z,@main
 LD A,1
 LD (@mode),A
 CALL @render_board
 CALL @draw_piece
 JP @main
end_input:
 LD A,(@edge)
 BIT 5,A
 CALL NZ,@finish_result
 JP @main
game_over:
 LD A,(@demo)
 OR A
 JP NZ,@demo_finish
 LD A,4
 CALL @select_song
 LD A,11
 CALL @request_sfx
 LD A,3
 LD (@mode),A
 CALL @render_board
 LD HL,@gameover_text
 LD B,10
 LD C,8
 CALL @print_text
 LD HL,@return_text
 LD B,12
 LD C,8
 JP @print_text
success:
 LD A,(@result_done)
 OR A
 RET NZ
 JP @show_b_summary
 LD HL,@success_text
 LD B,10
 LD C,8
 CALL @print_text
 LD HL,@return_text
 LD B,12
 LD C,8
 JP @print_text
print_text:
 LD A,(HL)
 INC HL
 CP 254
 RET Z
 CALL @draw_tile
 INC C
 JR @print_text

load_screen:
 LD DE,$4000
unpack_next:
 LD A,(HL)
 INC HL
 OR A
 RET Z
 CP 128
 JR NC,@unpack_run
 LD C,A
 LD B,0
 LDIR
 JR @unpack_next
unpack_run:
 AND 127
 INC A
 LD B,A
 LD A,(HL)
 INC HL
unpack_repeat:
 LD (DE),A
 INC DE
 DJNZ @unpack_repeat
 JR @unpack_next
draw_tile:
 PUSH AF
 LD A,56
 CALL @set_cell_attribute
 POP AF
 JP @draw_tile_bitmap
draw_game_tile:
 PUSH AF
 PUSH HL
 PUSH DE
 CP $80
 JR C,@tile_plain
 CP $90
 JR NC,@tile_plain
 SUB $80
 LD L,A
 LD H,0
 LD DE,@piece_attributes
 ADD HL,DE
 LD A,(HL)
 JR @tile_attribute_ready
tile_plain:
 LD A,56
tile_attribute_ready:
 CALL @set_cell_attribute
 POP DE
 POP HL
 POP AF
 JP @draw_tile_bitmap
set_cell_attribute:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD E,A
 LD L,B
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD A,C
 ADD A,L
 LD L,A
 JR NC,@attribute_page
 INC H
attribute_page:
 LD BC,$5800
 ADD HL,BC
 LD (HL),E
 POP HL
 POP DE
 POP BC
 POP AF
 RET
piece_attributes:
 DB 104,72,80,112,120,88,96,120,104,104,104,104,56,56,56,104
draw_tile_bitmap:
 LD (@tiletemp),A
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD A,B
 AND $18
 OR $40
 LD H,A
 LD A,B
 AND 7
 RRCA
 RRCA
 RRCA
 OR C
 LD L,A
 EX DE,HL
 LD A,(@tiletemp)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD BC,@tiles
 ADD HL,BC
 LD B,8
draw_tile_loop:
 LD A,(HL)
 LD (DE),A
 INC HL
 INC D
 DJNZ @draw_tile_loop
 POP HL
 POP DE
 POP BC
 POP AF
 RET

read_keys:
 LD D,0
 LD A,$DF
 IN A,($FE)
 BIT 1,A
 JR NZ,@no_left
 SET 0,D
no_left:
 BIT 0,A
 JR NZ,@no_right
 SET 1,D
no_right:
 LD A,$FD
 IN A,($FE)
 BIT 0,A
 JR NZ,@no_down
 SET 2,D
no_down:
 LD A,$FB
 IN A,($FE)
 BIT 0,A
 JR NZ,@no_q
 SET 4,D
no_q:
 LD A,$7F
 IN A,($FE)
 BIT 2,A
 JR NZ,@no_m
 SET 7,D
no_m:
 BIT 3,A
 JR NZ,@no_n
 SET 6,D
no_n:
 LD A,$BF
 IN A,($FE)
 BIT 0,A
 JR NZ,@no_enter
 SET 5,D
no_enter:
 CALL @read_kempston
 CALL @demo_keys
 LD A,(@keys)
 CPL
 AND D
 LD (@edge),A
 LD A,D
 LD (@keys),A
 RET

random_byte:
 LD HL,(@rng)
 LD A,H
 RRCA
 XOR L
 RRA
 XOR H
 LD H,L
 LD L,A
 LD (@rng),HL
 RET
random_piece:
 LD B,3
random_try:
 PUSH BC
 CALL @random_byte
 POP BC
 AND 7
 CP 7
 JR Z,@random_try
 LD D,A
 LD A,(@next)
 LD C,A
 LD A,(@history)
 OR C
 OR D
 LD C,A
 LD A,(@history)
 CP C
 JR NZ,@random_accept
 DJNZ @random_try
random_accept:
 LD A,(@next)
 LD (@history),A
 LD A,D
 RET

INCLUDE clear_animation.asm
INCLUDE kempston.asm
INCLUDE ui.asm
INCLUDE audio.asm
; Data assembled and embedded by build.py.
pause_text:
 DB 47,47,25,10,30,28,14,13,47,47,254
gameover_text:
 DB 47,16,10,22,14,47,24,31,14,27,254
success_text:
 DB 47,28,30,12,12,14,28,28,47,47,254
return_text:
 DB 14,23,29,14,27,47,22,14,23,30,254
awards:
 DW $0040,$0100,$0300,$1200
gravity:
 INCBIN gravity.bin
shapes:
 INCBIN shapes.bin
tiles:
 INCBIN tiles.bin
music:
 MUSICTABLE
music_data:
 INCBIN music_all.bin

menu_screen:
 INCBIN menu.rle
game_a_screen:
 INCBIN game_a.rle
game_b_screen:
 INCBIN game_b.rle
