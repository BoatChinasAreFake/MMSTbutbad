import re

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Find the script block
    match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if not match:
        print("No script block found!")
        return

    script_content = match.group(1)
    
    stack = []
    line_starts = [0]
    for i, char in enumerate(script_content):
        if char == '\n':
            line_starts.append(i + 1)
            
    def get_line_col(pos):
        line = 0
        for start in line_starts:
            if start <= pos:
                line += 1
            else:
                break
        col = pos - line_starts[line - 1] + 1
        return line + 441, col # offset of <script> tag

    in_single = False
    in_double = False
    in_template = False
    in_line_comment = False
    in_block_comment = False
    
    i = 0
    length = len(script_content)
    
    while i < length:
        char = script_content[i]
        
        # Handle escape characters inside strings
        if char == '\\' and (in_single or in_double or in_template):
            i += 2
            continue
            
        # Block comments
        if in_block_comment:
            if i < length - 1 and script_content[i:i+2] == '*/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
            
        # Line comments
        if in_line_comment:
            if char == '\n':
                in_line_comment = False
            i += 1
            continue
            
        # Strings
        if in_single:
            if char == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if char == '"':
                in_double = False
            i += 1
            continue
        if in_template:
            if char == '`':
                in_template = False
            i += 1
            continue
            
        # Check start of comments
        if i < length - 1 and script_content[i:i+2] == '/*':
            in_block_comment = True
            i += 2
            continue
        if i < length - 1 and script_content[i:i+2] == '//':
            in_line_comment = True
            i += 2
            continue
            
        # Check start of strings
        if char == "'":
            in_single = True
            i += 1
            continue
        if char == '"':
            in_double = True
            i += 1
            continue
        if char == '`':
            in_template = True
            i += 1
            continue
            
        # Brace matching
        if char == '{':
            stack.append(i)
        elif char == '}':
            if stack:
                stack.pop()
            else:
                line_num, col = get_line_col(i)
                print(f"Extra closing brace '}}' at HTML line {line_num}, col {col}")
                
        i += 1
        
    if stack:
        print(f"Brace mismatch: {len(stack)} braces left unclosed!")
        print("Unclosed braces opened at HTML lines:")
        for pos in stack[-10:]:
            line_num, col = get_line_col(pos)
            # Print a preview
            start_pos = max(0, pos - 20)
            end_pos = min(length, pos + 20)
            preview = script_content[start_pos:end_pos].replace('\n', ' ')
            print(f"  Line {line_num}, col {col}: ... {preview} ...")
    else:
        print("All braces match perfectly!")

if __name__ == '__main__':
    main()
