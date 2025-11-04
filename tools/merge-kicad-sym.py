#!/usr/bin/env python3

"""
Merges multiple KiCad 9 (or later) .kicad_sym files into a single library file.

This script parses .kicad_sym files to extract header information from the
first file and all (symbol ...) S-expressions from all provided files.
It then combines them into a single, new .kicad_sym file.

Usage:
    python3 merge-kicad-sym.py <output_file.kicad_sym> <input1.kicad_sym> [input2.kicad_sym ...]

Example:
    python3 merge-kicad-sym.py my_merged_lib.kicad_sym custom_symbols/*.kicad_sym
"""

import sys
import os

def parse_kicad_lib_file(content: str):
    """
    Parses a kicad_sym file's content.

    Returns a tuple: (header_string, list_of_symbol_sexprs)
    
    - header_string: The (kicad_symbol_lib ...) block containing only
                     non-symbol definitions (version, generator, etc.).
    - list_of_symbol_sexprs: A list of strings, where each string is a
                             complete (symbol ...) S-expression.
    """
    header_parts = []
    symbol_sexprs = []
    
    try:
        # Find the start of the (kicad_symbol_lib block
        lib_start = content.find('(kicad_symbol_lib')
        if lib_start == -1:
            print("Warning: File does not contain '(kicad_symbol_lib'.", file=sys.stderr)
            return None, []
            
        # Find the first parenthesis *after* (kicad_symbol_lib
        # This marks the beginning of the library's content
        content_start = content.find('(', lib_start + 1)
        if content_start == -1:
            print("Warning: Malformed '(kicad_symbol_lib'.", file=sys.stderr)
            return None, []
            
    except ValueError:
        print("Warning: Malformed file.", file=sys.stderr)
        return None, []

    # State machine to parse S-expressions at nesting level 1
    balance = 1 # We are inside (kicad_symbol_lib ... )
    in_quote = False
    sexpr_start = -1
    # Start scanning AT the first top-level S-expression
    i = content_start 

    while i < len(content):
        char = content[i]

        if in_quote:
            # Handle escaped quotes
            if char == '"' and (i == 0 or content[i-1] != '\\'):
                in_quote = False
        elif char == '"':
            in_quote = True
        elif char == '(':
            if balance == 1: # Start of a top-level sexpr
                sexpr_start = i
            balance += 1
        elif char == ')':
            balance -= 1
            if balance == 1 and sexpr_start != -1: # End of a top-level sexpr
                sexpr = content[sexpr_start:i+1]
                
                # Check if it's a symbol
                if sexpr.lstrip().startswith('(symbol'):
                    symbol_sexprs.append(sexpr)
                else:
                    # It's a header element
                    header_parts.append(sexpr)
                
                sexpr_start = -1 # Reset
            elif balance == 0:
                # We've hit the end of the (kicad_symbol_lib ...)
                break
        
        i += 1
    
    if balance != 0:
        print(f"Warning: File has unbalanced parentheses (balance: {balance}).", file=sys.stderr)
        
    # Reconstruct the header string
    # (kicad_symbol_lib
    #   (version ...)
    #   (generator ...)
    # ...
    # (This will be closed by the main script)
    
    # Get just the '(kicad_symbol_lib' part, up to the first child's '('
    header = content[lib_start:content_start].strip()
    
    if header_parts:
         header += "\n\t" + "\n\t".join(header_parts)
    
    return header, symbol_sexprs

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    output_filename = sys.argv[1]
    input_filenames = sys.argv[2:]

    if not input_filenames:
        print("Error: No input files specified.", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

    all_symbols = []
    main_header = None

    print(f"Processing {len(input_filenames)} input file(s)...")

    for filename in input_filenames:
        if not os.path.exists(filename):
            print(f"Warning: Input file not found, skipping: {filename}", file=sys.stderr)
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            header, symbols = parse_kicad_lib_file(content)
            
            if header is None:
                print(f"Warning: Could not parse file, skipping: {filename}", file=sys.stderr)
                continue

            # Take the header from the first valid file
            if main_header is None:
                main_header = header
                print(f"Using header from: {filename}")

            if symbols:
                all_symbols.extend(symbols)
                print(f"  Found {len(symbols)} symbol(s) in: {filename}")
            
        except Exception as e:
            print(f"Error processing file {filename}: {e}", file=sys.stderr)

    if main_header is None:
        print("Error: No valid KiCad symbol library files were found.", file=sys.stderr)
        sys.exit(1)

    if not all_symbols:
        print("Warning: No symbols were found in any input files.", file=sys.stderr)

    try:
        with open(output_filename, 'w', encoding='utf-8') as out_f:
            # Write the header
            out_f.write(main_header)
            
            # Write all symbols
            if all_symbols:
                out_f.write("\n\n\t" + "\n\n\t".join(all_symbols))
            
            # Write the final closing parenthesis
            out_f.write("\n)\n")
            
    except IOError as e:
        print(f"Error writing to output file {output_filename}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nSuccessfully merged {len(all_symbols)} symbol(s) into {output_filename}")

if __name__ == "__main__":
    main()
