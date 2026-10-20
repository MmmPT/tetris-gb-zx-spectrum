init_records:
 XOR A
 LD HL,$6000
 LD DE,$6001
 LD BC,3779
 LD (HL),A
 LDIR
 RET
reset_result:
 XOR A
 LD (@result_done),A
 LD (@ending_done),A
 LD HL,@stats
 LD DE,@stats+1
 LD BC,9
 LD (HL),A
 LDIR
 RET
count_clear:
 LD A,(@cleared)
 DEC A
 ADD A,A
 LD L,A
 LD H,0
 LD DE,@stats
 ADD HL,DE
 INC (HL)
 RET NZ
 INC HL
 INC (HL)
 RET
menu_extra:
 CALL @menu_kempston
 LD A,$FB
 IN A,($FE)
 AND 16
 LD B,A
 LD A,(@menu_t)
 LD C,A
 LD A,B
 LD (@menu_t),A
 LD A,C
 OR A
 JR Z,@menu_check_heart
 LD A,B
 OR A
 JR NZ,@menu_check_heart
 LD A,(@music_choice)
 INC A
 CP 3
 JR C,@menu_music_set
 XOR A
menu_music_set:
 LD (@music_choice),A
 LD A,1
 CALL @request_sfx
menu_check_heart:
 LD A,$BF
 IN A,($FE)
 AND 2
 LD B,A
 LD A,(@menu_l)
 LD C,A
 LD A,B
 LD (@menu_l),A
 LD A,C
 OR A
 JR Z,@menu_check_records
 LD A,B
 OR A
 JR NZ,@menu_check_records
 LD A,(@heart)
 XOR 1
 LD (@heart),A
 LD A,1
 CALL @request_sfx
menu_check_records:
 LD A,$FB
 IN A,($FE)
 AND 8
 LD B,A
 LD A,(@menu_r)
 LD C,A
 LD A,B
 LD (@menu_r),A
 LD A,C
 OR A
 JR Z,@menu_extra_draw
 LD A,B
 OR A
 JP Z,@show_records
menu_extra_draw:
 LD B,18
 LD C,24
 LD A,(@music_choice)
 ADD A,10
 CALL @draw_tile
 LD B,17
 LD C,24
 LD A,(@heart)
 OR A
 LD A,47
 JR Z,@menu_heart_draw
 LD A,17
menu_heart_draw:
 CALL @draw_tile
 LD A,(@keys)
 OR A
 JR Z,@menu_idle_tick
 LD HL,0
 LD (@idle),HL
 RET
menu_idle_tick:
 LD HL,(@idle)
 INC HL
 LD (@idle),HL
 LD DE,750
 OR A
 SBC HL,DE
 RET C
 LD A,1
 LD (@demo),A
 CALL @new_game
 RET
demo_keys:
 LD A,(@demo)
 OR A
 RET Z
 LD A,D
 OR A
 JR Z,@demo_auto
 XOR A
 LD (@demo),A
 CALL @show_menu
 LD D,0
 RET
demo_auto:
 PUSH HL
 PUSH BC
 LD HL,(@idle)
 INC HL
 LD (@idle),HL
 LD BC,1700
 OR A
 SBC HL,BC
 JR C,@demo_play
 POP BC
 POP HL
 CALL @demo_finish
 LD D,0
 RET
demo_play:
 LD D,0
 LD A,($5C78)
 AND 3
 JR Z,@demo_play_done
 LD A,(@piece)
 AND 3
 LD B,A
 LD A,(@rot)
 CP B
 JR Z,@demo_position
 LD A,($5C78)
 AND 8
 JR Z,@demo_play_done
 LD D,16
 JR @demo_play_done
demo_position:
 LD A,B
 ADD A,A
 LD B,A
 LD A,(@px)
 CP B
 JR Z,@demo_drop
 LD D,1
 JR NC,@demo_play_done
 LD D,2
 JR @demo_play_done
demo_drop:
 LD D,4
demo_play_done:
 POP BC
 POP HL
 RET
demo_finish:
 XOR A
 LD (@demo),A
 JP @show_menu
clear_ui:
 XOR A
 LD HL,$4000
 LD DE,$4001
 LD BC,6143
 LD (HL),A
 LDIR
 LD A,56
 LD HL,$5800
 LD DE,$5801
 LD BC,767
 LD (HL),A
 LDIR
 RET
show_b_summary:
 LD A,1
 LD (@result_done),A
 LD A,5
 LD (@mode),A
 CALL @clear_ui
 LD HL,@b_result_text
 LD B,2
 LD C,5
 CALL @print_text
 LD HL,@summary_labels
 LD B,6
 LD C,5
 CALL @print_text
 LD HL,@summary_double
 LD B,8
 LD C,5
 CALL @print_text
 LD HL,@summary_triple
 LD B,10
 LD C,5
 CALL @print_text
 LD HL,@summary_tetris
 LD B,12
 LD C,5
 CALL @print_text
 LD HL,@summary_soft
 LD B,14
 LD C,5
 CALL @print_text
 LD HL,@summary_total
 LD B,17
 LD C,5
 CALL @print_text
 LD IX,@stats
 LD B,6
summary_counts:
 LD L,(IX+0)
 LD H,(IX+1)
 LD C,15
 CALL @print_word
 CALL @print_subtotal
 INC IX
 INC IX
 INC B
 INC B
 LD A,B
 CP 14
 JR NZ,@summary_counts
 LD HL,(@soft_total)
 LD B,14
 LD C,15
 CALL @print_word
 LD HL,@score
 LD B,17
 LD C,18
 CALL @print_score_at
 LD HL,@continue_text
 LD B,21
 LD C,8
 JP @print_text
summary_input:
 LD A,(@edge)
 BIT 5,A
 JP Z,@main
 CALL @finish_result
 JP @main
finish_result:
 LD A,(@demo)
 OR A
 JP NZ,@demo_finish
 LD A,(@ending_done)
 OR A
 JR NZ,@check_record
 LD A,(@gametype)
 OR A
 JR Z,@check_a_ending
 LD A,(@remaining)
 OR A
 JR NZ,@check_record
 LD A,(@startlevel)
 CP 9
 JP Z,@show_ending
 JR @check_record
check_a_ending:
 LD A,(@score+2)
 CP $10
 JP NC,@show_ending
check_record:
 CALL @group_pointer
 LD D,3
record_compare:
 PUSH HL
 INC HL
 INC HL
 LD A,(@score+2)
 CP (HL)
 JR NZ,@record_decide
 DEC HL
 LD A,(@score+1)
 CP (HL)
 JR NZ,@record_decide
 DEC HL
 LD A,(@score)
 CP (HL)
record_decide:
 POP HL
 JR C,@record_next
 JR Z,@record_next
 JR @record_insert
record_next:
 LD BC,9
 ADD HL,BC
 DEC D
 JR NZ,@record_compare
 JP @show_records
record_insert:
 LD (@record_ptr),HL
 LD A,D
 DEC A
 JR Z,@record_no_shift
 PUSH AF
 PUSH HL
 LD DE,$70C0
 LD BC,18
 LDIR
 POP HL
 LD DE,9
 ADD HL,DE
 EX DE,HL
 LD HL,$70C0
 POP AF
 LD BC,9
 CP 1
 JR Z,@record_copy_tail
 LD BC,18
record_copy_tail:
 LDIR
record_no_shift:
 LD DE,(@record_ptr)
 LD HL,@score
 LD BC,3
 LDIR
 LD HL,@name_buf
 LD B,6
record_blank_name:
 LD (HL),10
 INC HL
 DJNZ @record_blank_name
 XOR A
 LD (@name_pos),A
 LD A,6
 LD (@mode),A
 LD A,6
 CALL @select_song
 CALL @clear_ui
 LD HL,@new_record_text
 LD B,5
 LD C,8
 CALL @print_text
 LD HL,@name_help_text
 LD B,17
 LD C,2
 CALL @print_text
 LD HL,@continue_text
 LD B,20
 LD C,8
 CALL @print_text
 JP @render_name
group_pointer:
 LD A,(@startlevel)
 LD L,A
 LD H,0
 LD A,(@gametype)
 OR A
 JR Z,@group_heart
 ADD HL,HL
 LD E,L
 LD D,H
 ADD HL,HL
 ADD HL,DE
 LD A,(@height)
 ADD A,L
 ADD A,10
 LD L,A
 LD H,0
group_heart:
 LD A,(@heart)
 OR A
 JR Z,@group_index
 LD DE,70
 ADD HL,DE
group_index:
 LD A,L
 LD (@record_group),A
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,DE
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 ADD HL,DE
 ADD HL,DE
 LD DE,$6000
 ADD HL,DE
 RET
render_name:
 LD HL,@name_buf
 LD B,11
 LD C,12
 LD D,6
name_draw_loop:
 LD A,(HL)
 INC HL
 CALL @draw_tile
 INC C
 DEC D
 JR NZ,@name_draw_loop
 LD B,12
 LD C,12
 LD D,6
 LD A,47
name_clear_cursor:
 CALL @draw_tile
 INC C
 DEC D
 JR NZ,@name_clear_cursor
 LD A,(@name_pos)
 ADD A,12
 LD C,A
 LD A,37
 JP @draw_tile
name_input:
 LD A,(@edge)
 BIT 5,A
 JR Z,@name_edit
 LD HL,@name_buf
 LD DE,(@record_ptr)
 INC DE
 INC DE
 INC DE
 LD BC,6
 LDIR
 CALL @show_records
 JP @main
name_edit:
 LD A,(@name_pos)
 LD L,A
 LD H,0
 LD DE,@name_buf
 ADD HL,DE
 LD A,(@edge)
 BIT 4,A
 JR Z,@name_check_down
 LD A,(HL)
 INC A
 CP 36
 JR C,@name_up_store
 LD A,10
name_up_store:
 LD (HL),A
name_check_down:
 LD A,(@edge)
 BIT 2,A
 JR Z,@name_check_left
 LD A,(HL)
 DEC A
 CP 10
 JR NC,@name_down_store
 LD A,35
name_down_store:
 LD (HL),A
name_check_left:
 LD A,(@edge)
 BIT 0,A
 JR Z,@name_check_right
 LD A,(@name_pos)
 OR A
 JR Z,@name_check_right
 DEC A
 LD (@name_pos),A
name_check_right:
 LD A,(@edge)
 BIT 1,A
 JR Z,@name_redraw
 LD A,(@name_pos)
 CP 5
 JR Z,@name_redraw
 INC A
 LD (@name_pos),A
name_redraw:
 CALL @render_name
 JP @main
show_records:
 LD A,7
 LD (@mode),A
 LD A,6
 CALL @select_song
 CALL @clear_ui
 LD HL,@records_text
 LD B,2
 LD C,10
 CALL @print_text
 LD HL,@record_group_text
 LD B,4
 LD C,5
 CALL @print_text
 LD A,(@gametype)
 ADD A,10
 LD C,5
 CALL @draw_tile
 LD A,(@startlevel)
 LD C,15
 CALL @draw_tile
 LD A,(@height)
 LD C,25
 CALL @draw_tile
 CALL @group_pointer
 LD B,7
records_row:
 LD A,B
 LD (@ui_row),A
 PUSH HL
 LD C,20
 CALL @print_score_at
 POP HL
 PUSH HL
 LD DE,3
 ADD HL,DE
 LD C,8
 LD D,6
record_name_loop:
 LD A,(HL)
 INC HL
 OR A
 JR NZ,@record_has_name
 LD A,37
record_has_name:
 CALL @draw_tile
 INC C
 DEC D
 JR NZ,@record_name_loop
 POP HL
 LD DE,9
 ADD HL,DE
 LD A,(@ui_row)
 ADD A,3
 LD B,A
 CP 16
 JR NZ,@records_row
 LD HL,@continue_text
 LD B,21
 LD C,8
 JP @print_text
records_input:
 LD A,(@edge)
 BIT 5,A
 CALL NZ,@show_menu
 JP @main
print_score_at:
 PUSH HL
 INC HL
 INC HL
 LD A,(HL)
 CALL @draw_bcd
 DEC HL
 INC C
 INC C
 LD A,(HL)
 CALL @draw_bcd
 DEC HL
 INC C
 INC C
 LD A,(HL)
 CALL @draw_bcd
 POP HL
 RET
print_word:
 PUSH IX
 LD IX,@decimal_divisors
 LD A,4
 LD ($70BC),A
word_digit:
 LD E,(IX+0)
 LD D,(IX+1)
 XOR A
word_subtract:
 OR A
 SBC HL,DE
 JR C,@word_ready
 INC A
 JR @word_subtract
word_ready:
 ADD HL,DE
 CALL @draw_tile
 INC C
 INC IX
 INC IX
 LD A,($70BC)
 DEC A
 LD ($70BC),A
 JR NZ,@word_digit
 POP IX
 RET
decimal_divisors:
 DW 1000,100,10,1
show_ending:
 LD A,1
 LD (@ending_done),A
 LD A,8
 LD (@mode),A
 LD HL,500
 LD (@ending_time),HL
 LD A,(@gametype)
 OR A
 JR Z,@ending_a_song
 LD A,(@height)
 ADD A,7
 CALL @select_song
 JR @ending_draw
ending_a_song:
 LD A,13
 CALL @select_song
ending_draw:
 CALL @render_ending
 RET
ending_input:
 LD A,(@edge)
 BIT 5,A
 JR NZ,@ending_finished
 LD HL,(@ending_time)
 DEC HL
 LD (@ending_time),HL
 LD A,H
 OR L
 JR Z,@ending_finished
 LD A,L
 AND 7
 CALL Z,@render_ending
 JP @main
ending_finished:
 CALL @check_record
 JP @main
render_ending:
 CALL @clear_ui
 LD HL,@congrats_text
 LD B,2
 LD C,8
 CALL @print_text
 LD A,(@gametype)
 OR A
 JR Z,@render_rocket
 LD A,(@height)
 CP 5
 JR NZ,@render_dancers
 LD HL,(@ending_time)
 LD DE,250
 OR A
 SBC HL,DE
 JR NC,@render_dancers
 LD A,23
 JR @rocket_stamp
render_rocket:
 LD A,(@score+2)
 CP $20
 LD A,20
 JR NC,@rocket_stamp
 LD A,(@score+2)
 CP $15
 LD A,21
 JR NC,@rocket_stamp
 LD A,22
rocket_stamp:
 PUSH AF
 LD HL,(@ending_time)
 LD A,H
 OR A
 LD A,L
 JR Z,@rocket_low_time
 LD A,240
rocket_low_time:
 SRL A
 SRL A
 SRL A
 SRL A
 ADD A,3
 CP 16
 JR C,@rocket_row_ok
 LD A,15
rocket_row_ok:
 LD B,A
 LD C,15
 POP AF
 CALL @get_stamp
 CALL @draw_stamp
 LD HL,@continue_text
 LD B,22
 LD C,8
 JP @print_text
render_dancers:
 LD HL,(@ending_time)
 LD A,L
 AND 16
 LD A,0
 JR Z,@dancer_phase
 LD A,10
dancer_phase:
 LD (@ending_phase),A
 LD A,(@height)
 INC A
 CP 6
 JR C,@dancer_count
 LD A,10
dancer_count:
 LD ($70BD),A
 XOR A
 LD ($70BE),A
dancer_loop:
 LD A,($70BE)
 LD L,A
 LD H,0
 LD DE,@dancer_rows
 ADD HL,DE
 LD B,(HL)
 LD DE,10
 ADD HL,DE
 LD C,(HL)
 LD A,(@ending_phase)
 LD D,A
 LD A,($70BE)
 ADD A,D
 CALL @get_stamp
 CALL @draw_stamp
 LD A,($70BE)
 INC A
 LD ($70BE),A
 LD B,A
 LD A,($70BD)
 CP B
 JR NZ,@dancer_loop
 RET
get_stamp:
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,@ending_table
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 EX DE,HL
 RET
draw_stamp:
 LD D,(HL)
 INC HL
 LD E,(HL)
 INC HL
stamp_row:
 PUSH DE
 PUSH BC
stamp_column:
 CALL @draw_raw
 INC C
 DEC D
 JR NZ,@stamp_column
 POP BC
 INC B
 POP DE
 DEC E
 JR NZ,@stamp_row
 RET
draw_raw:
 PUSH BC
 PUSH DE
 LD A,B
 AND $18
 OR $40
 LD D,A
 LD A,B
 AND 7
 RRCA
 RRCA
 RRCA
 OR C
 LD E,A
 LD B,8
raw_pixel:
 LD A,(HL)
 INC HL
 LD (DE),A
 INC D
 DJNZ @raw_pixel
 POP DE
 POP BC
 RET
dancer_rows:
 DB 7,7,7,14,16,16,12,12,17,17
 DB 14,10,12,10,15,17,15,18,22,24
ending_table:
 ENDINGTABLE
ending_data:
 INCBIN ending_stamps.bin

b_result_text:
 DB 11,37,29,34,25,14,47,12,24,22,25,21,14,29,14,254

summary_labels:
 DB 28,18,23,16,21,14,254

summary_double:
 DB 13,24,30,11,21,14,254

summary_triple:
 DB 29,27,18,25,21,14,254

summary_tetris:
 DB 29,14,29,27,18,28,254

summary_soft:
 DB 28,24,15,29,47,13,27,24,25,254

summary_total:
 DB 29,24,29,10,21,254

continue_text:
 DB 14,23,29,14,27,47,12,24,23,29,18,23,30,14,254

new_record_text:
 DB 23,14,32,47,29,24,25,47,28,12,24,27,14,254

name_help_text:
 DB 26,47,10,47,21,14,29,29,14,27,47,47,24,47,25,47,12,30,27,28,24,27,254

records_text:
 DB 29,24,25,47,28,12,24,27,14,28,254

congrats_text:
 DB 12,24,23,16,27,10,29,30,21,10,29,18,24,23,28,254

soft_interval:
 LD A,($703B)
 ADD A,131
 LD ($703B),A
 LD A,1
 RET NC
 INC A
 RET
repeat_initial:
 LD A,($703C)
 ADD A,65
 LD ($703C),A
 LD A,19
 RET NC
 INC A
 RET
repeat_period:
 LD A,($703C)
 ADD A,137
 LD ($703C),A
 LD A,7
 RET NC
 INC A
 RET
check_soft_reset:
 LD A,$F7
 IN A,($FE)
 BIT 0,A
 RET NZ
 XOR A
 LD (@demo),A
 LD (@sfx_active),A
 LD (@sfx_priority),A
 LD (@sfx_pending),A
 JP @show_menu
print_subtotal:
 PUSH BC
 LD A,B
 SUB 6
 LD L,A
 LD H,0
 LD DE,@awards
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD ($70E5),DE
 LD L,(IX+0)
 LD H,(IX+1)
 LD ($70E3),HL
 LD HL,@score
 LD DE,$70E0
 LD BC,3
 LDIR
 XOR A
 LD (@score),A
 LD (@score+1),A
 LD (@score+2),A
subtotal_outer:
 LD HL,($70E3)
 LD A,H
 OR L
 JR Z,@subtotal_done
 DEC HL
 LD ($70E3),HL
 LD A,(@startlevel)
 INC A
 LD B,A
subtotal_inner:
 PUSH BC
 LD DE,($70E5)
 LD C,0
 CALL @add_score
 POP BC
 DJNZ @subtotal_inner
 JR @subtotal_outer
subtotal_done:
 POP BC
 PUSH BC
 LD C,22
 LD HL,@score
 CALL @print_score_at
 LD HL,$70E0
 LD DE,@score
 LD BC,3
 LDIR
 POP BC
 RET

record_group_text:
 DB 10,47,21,14,31,14,21,47,47,47,0,47,47,11,14,18,16,11,29,47,0,254
