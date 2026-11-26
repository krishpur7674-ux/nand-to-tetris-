#!/usr/bin/env python3
"""Two-pass assembler for the Hack computer (Nand2Tetris)."""

import argparse
import sys

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
PREDEFINED.update({f"R{i}": i for i in range(16)})

COMP = {
    "0":"0101010", "1":"0111111", "-1":"0111010", "D":"0001100",
    "A":"0110000", "!D":"0001101", "!A":"0110001", "-D":"0001111",
    "-A":"0110011", "D+1":"0011111", "A+1":"0110111", "D-1":"0001110",
    "A-1":"0110010", "D+A":"0000010", "D-A":"0010011", "A-D":"0000111",
    "D&A":"0000000", "D|A":"0010101", "M":"1110000", "!M":"1110001",
    "-M":"1110011", "M+1":"1110111", "M-1":"1110010", "D+M":"1000010",
    "D-M":"1010011", "M-D":"1000111", "D&M":"1000000", "D|M":"1010101",
}
DEST = {
    "": "000", "M":"001", "D":"010", "MD":"011", "A":"100",
    "AM":"101", "AD":"110", "AMD":"111",
}
JUMP = {
    "": "000", "JGT":"001", "JEQ":"010", "JGE":"011",
    "JLT":"100", "JNE":"101", "JLE":"110", "JMP":"111",
}


def strip_comment(raw):
    return raw.split("//", 1)[0].strip()


def valid_symbol(symbol):
    if not symbol:
        return False
    if symbol[0].isdigit():
        return False
    return all(ch.isalpha() or ch.isdigit() or ch in "_.:$" for ch in symbol)


def assemble(source):
    lines = []
    for original_line, raw in enumerate(source.splitlines(), 1):
        text = strip_comment(raw)
        if text:
            lines.append((original_line, text))

    # Pass one: labels are ROM locations, in the absence of blank/comment lines.
    labels = dict(PREDEFINED)
    rom_address = 0
    cleaned = []
    for line_no, text in lines:
        if text.startswith("(") and text.endswith(")"):
            name = text[1:-1].strip()
            if not valid_symbol(name):
                raise ValueError(f"Line {line_no}: Invalid instruction.")
            if name in labels:
                raise ValueError(f"Line {line_no}: Invalid instruction.")
            labels[name] = rom_address
        elif "(" in text or ")" in text:
            raise ValueError(f"Line {line_no}: Invalid instruction.")
        else:
            cleaned.append((line_no, text))
            rom_address += 1

    # Pass two: translate instructions and allocate variables from RAM 16.
    variables = {}
    next_variable = 16
    binary = []

    for line_no, text in cleaned:
        if text.startswith("@"):
            operand = text[1:].strip()
            if not operand:
                raise ValueError(f"Line {line_no}: Invalid instruction.")
            if operand.isdigit():
                address = int(operand, 10)
                if address < 0 or address > 32767:
                    raise ValueError(f"Line {line_no}: Invalid instruction.")
            elif valid_symbol(operand):
                if operand in labels:
                    address = labels[operand]
                elif operand in variables:
                    address = variables[operand]
                else:
                    address = next_variable
                    variables[operand] = address
                    next_variable += 1
                    if next_variable > 24576:
                        raise ValueError(f"Line {line_no}: Invalid instruction.")
            else:
                raise ValueError(f"Line {line_no}: Invalid instruction.")
            binary.append(format(address | 0x0000, "016b") if address < 32768 else None)
            continue

        # C-instruction: optional dest = comp ; optional jump.
        if "=" in text:
            dest, remainder = text.split("=", 1)
            dest = dest.strip()
            if dest not in DEST:
                raise ValueError(f"Line {line_no}: Invalid instruction.")
        else:
            dest = ""
            remainder = text

        if ";" in remainder:
            comp, jump = remainder.split(";", 1)
            comp = comp.strip()
            jump = jump.strip().upper()
        else:
            comp = remainder.strip()
            jump = ""

        if comp not in COMP or jump not in JUMP:
            raise ValueError(f"Line {line_no}: Invalid instruction.")
        binary.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])

    return binary


def main():
    parser = argparse.ArgumentParser(description="Assemble Hack assembly language into 16-bit binary")
    parser.add_argument("input", help="input .asm file")
    parser.add_argument("-o", "--output", help="output .hack file")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path.rsplit(".", 1)[0] + ".hack"

    try:
        with open(input_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        binary = assemble(source)
        with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
            for instruction in binary:
                handle.write(instruction + "\n")
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: Unable to assemble file ({exc})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main":
    raise SystemExit(main())
