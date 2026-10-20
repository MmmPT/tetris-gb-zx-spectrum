wait_frame:
 HALT
 RET
music_interrupt:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 LD HL,$5C78
 INC (HL)
 CALL @music_tick
 CALL @sfx_tick
 POP IX
 POP HL
 POP DE
 POP BC
 POP AF
 EI
 RETI
ay_write:
 PUSH BC
 PUSH AF
 LD BC,$FFFD
 OUT (C),E
 POP AF
 LD B,$BF
 OUT (C),A
 POP BC
 RET
ay_init:
 LD E,0
ay_clear:
 XOR A
 CALL @ay_write
 INC E
 LD A,E
 CP 14
 JR NZ,@ay_clear
 LD E,7
 LD A,56
 JP @ay_write
ay_mute:
 LD E,8
 XOR A
 CALL @ay_write
 INC E
 CALL @ay_write
 INC E
 JP @ay_write
select_song:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 DI
 LD (@song_index),A
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,@music
 ADD HL,DE
 LD (@song_base),HL
 LD DE,6
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD (@drum_ptr),DE
 XOR A
 LD HL,$7040
 LD DE,$7041
 LD BC,23
 LD (HL),A
 LDIR
 LD (@drum_left),A
 LD (@drum_age),A
 LD (@drum_note),A
 EI
 POP HL
 POP DE
 POP BC
 POP AF
 RET
music_tick:
 LD A,(@music_on)
 OR A
 JP Z,@ay_mute
 LD A,(@mode)
 CP 2
 JP Z,@ay_mute
 LD IX,$7040
 LD C,0
voice_loop:
 LD A,(IX+2)
 OR A
 JR NZ,@voice_envelope
 LD L,(IX+0)
 LD H,(IX+1)
 LD A,H
 OR L
 JR NZ,@voice_load
voice_start:
 LD L,C
 LD H,0
 ADD HL,HL
 LD DE,(@song_base)
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 EX DE,HL
voice_load:
 LD E,(HL)
 INC HL
 LD D,(HL)
 INC HL
 LD A,(HL)
 INC HL
 OR A
 JP Z,@voice_end
 LD (IX+0),L
 LD (IX+1),H
 LD (IX+2),A
 XOR A
 LD (IX+3),A
 LD A,D
 OR E
 JR Z,@voice_rest
 PUSH HL
 PUSH DE
 LD L,C
 LD H,0
 LD DE,@voice_volumes
 ADD HL,DE
 LD A,(HL)
 POP DE
 POP HL
voice_rest:
 LD (IX+4),A
 LD (IX+6),E
 LD (IX+7),D
voice_envelope:
 LD A,C
 ADD A,A
 LD E,A
 LD A,(IX+6)
 CALL @ay_write
 INC E
 LD A,(IX+7)
 CALL @ay_write
 LD B,(IX+4)
 LD A,(IX+3)
 CP 2
 JR C,@voice_gate
 DEC B
 CP 6
 JR C,@voice_gate
 DEC B
voice_gate:
 LD A,(IX+2)
 CP 2
 JR NC,@voice_volume
 LD B,0
voice_volume:
 LD A,(IX+4)
 OR A
 JR NZ,@voice_sound
 LD B,0
voice_sound:
 LD A,C
 ADD A,8
 LD E,A
 LD A,B
 CALL @ay_write
 INC (IX+3)
 DEC (IX+2)
 LD DE,8
 ADD IX,DE
 INC C
 LD A,C
 CP 3
 JP NZ,@voice_loop
 JP @drum_tick
voice_end:
 LD A,(@song_index)
 LD L,A
 LD H,0
 LD DE,@song_loops
 ADD HL,DE
 LD A,(HL)
 OR A
 JP NZ,@voice_start
 LD HL,@silent_music
 JP @voice_load
voice_volumes:
 DB 13,9,11
silent_music:
 DB 0,0,255,0,0,0
song_loops:
 INCBIN music_loops.bin
drum_tick:
 LD A,(@drum_left)
 OR A
 JR NZ,@drum_advance
 LD HL,(@drum_ptr)
 LD A,(HL)
 INC HL
 LD B,A
 LD A,(HL)
 INC HL
 OR A
 JR NZ,@drum_loaded
 LD A,(@song_index)
 LD L,A
 LD H,0
 LD DE,@song_loops
 ADD HL,DE
 LD A,(HL)
 OR A
 JR NZ,@drum_restart
 XOR A
 LD (@drum_note),A
 LD A,255
 LD (@drum_left),A
 RET
drum_restart:
 LD HL,(@song_base)
 LD DE,6
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD (@drum_ptr),DE
 JP @drum_tick
drum_loaded:
 LD (@drum_left),A
 LD (@drum_ptr),HL
 LD A,B
 LD (@drum_note),A
 XOR A
 LD (@drum_age),A
drum_advance:
 LD HL,@drum_left
 DEC (HL)
 INC HL
 INC (HL)
 RET
drum_output:
 LD A,(@music_on)
 OR A
 RET Z
 LD A,(@mode)
 CP 2
 RET Z
 LD A,(@drum_note)
 OR A
 RET Z
 LD B,A
 LD A,(@drum_age)
 CP 4
 RET NC
 ADD A,A
 LD C,A
 LD A,10
 SUB C
 LD E,9
 CALL @ay_write
 LD A,B
 ADD A,A
 ADD A,A
 LD E,6
 CALL @ay_write
 LD E,7
 LD A,42
 JP @ay_write
request_sfx:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD B,A
 LD L,A
 LD H,0
 LD DE,@sfx_priorities
 ADD HL,DE
 LD A,(HL)
 LD C,A
 LD A,(@sfx_priority)
 CP C
 JR C,@sfx_request_ok
 JR Z,@sfx_request_ok
 JR @sfx_request_done
sfx_request_ok:
 LD A,C
 LD (@sfx_priority),A
 LD A,B
 LD (@sfx_pending),A
sfx_request_done:
 POP HL
 POP DE
 POP BC
 POP AF
 RET
sfx_tick:
 LD A,(@sfx_pending)
 OR A
 JR Z,@sfx_continue
 LD (@sfx_active),A
 DEC A
 ADD A,A
 LD L,A
 LD H,0
 LD DE,@sfx_table
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD (@sfx_ptr),DE
 XOR A
 LD (@sfx_pending),A
 LD (@sfx_left),A
sfx_continue:
 LD E,7
 LD A,56
 CALL @ay_write
 LD A,(@sfx_active)
 OR A
 JP Z,@drum_output
 LD A,(@sfx_left)
 OR A
 JR NZ,@sfx_output
 LD HL,(@sfx_ptr)
 LD DE,5
 ADD HL,DE
 LD A,(HL)
 OR A
 JR NZ,@sfx_step_ready
 XOR A
 LD (@sfx_active),A
 LD (@sfx_priority),A
 RET
sfx_step_ready:
 LD (@sfx_left),A
sfx_output:
 LD HL,(@sfx_ptr)
 LD E,2
 LD A,(HL)
 INC HL
 CALL @ay_write
 INC E
 LD A,(HL)
 INC HL
 CALL @ay_write
 LD E,9
 LD A,(HL)
 INC HL
 CALL @ay_write
 LD E,7
 LD A,(HL)
 INC HL
 CALL @ay_write
 LD E,6
 LD A,(HL)
 CALL @ay_write
 LD A,(@sfx_left)
 DEC A
 LD (@sfx_left),A
 RET NZ
 LD HL,(@sfx_ptr)
 LD DE,6
 ADD HL,DE
 LD (@sfx_ptr),HL
 RET
sfx_priorities:
 INCBIN sfx_priority.bin
sfx_table:
 SFXTABLE
sfx_data:
 INCBIN sfx.bin
