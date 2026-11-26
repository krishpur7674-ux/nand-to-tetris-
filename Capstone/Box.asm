// Box: Ayush Kumar, Roll 2501730337, K=37
// 32 pixels wide, 20 rows tall, starting at screen row 37.
// Absolute start address = SCREEN (16384) + 32 * 37 = 17568.

(LOOP)
    @KBD
    D=M
    @DRAW
    D;JNE

(CLEAR)
    @17568
    D=A
    @R1
    M=D

    @20
    D=A
    @R2
    M=D

(CLEAR_ROW)
    @R1
    A=M
    M=0
    A=A+1
    M=0

    @R1
    D=M
    @32
    D=D+A
    @R1
    M=D

    @R2
    MD=M-1
    @CLEAR_ROW
    D;JGT

    @LOOP
    0;JMP

(DRAW)
    @17568
    D=A
    @R1
    M=D

    @20
    D=A
    @R2
    M=D

(DRAW_ROW)
    @R1
    A=M
    M=-1
    A=A+1
    M=-1

    @R1
    D=M
    @32
    D=D+A
    @R1
    M=D

    @R2
    MD=M-1
    @DRAW_ROW
    D;JGT

    @LOOP
    0;JMP
