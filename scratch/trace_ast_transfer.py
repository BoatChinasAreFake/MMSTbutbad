from parse_mod_data_2024 import parse_statements, eval_block

with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's extract the completion_reward block content
start_idx = content.find('completion_reward')
idx = content.find('{', start_idx)
brace_count = 0
block_content = ""
for i in range(idx, len(content)):
    char = content[i]
    if char == '{':
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if brace_count == 0:
            block_content = content[idx+1:i]
            break

statements = parse_statements(block_content)
print(f"Total top-level statements parsed: {len(statements)}")

# Let's search for every_state block that has AST
found_ast_block = False
for key, val, is_block in statements:
    if is_block and key == 'every_state':
        sub_statements = parse_statements(val)
        for skey, sval, sis_block in sub_statements:
            if sis_block and len(skey) == 3 and skey.upper() == 'AST':
                print("Found AST transfer block in every_state:")
                print("Sub-statements in this block:")
                for k, v, ib in sub_statements:
                    print(f"  Key: {k}, IsBlock: {ib}, Content: {v[:100]}")
                found_ast_block = True
                
                # Let's trace evaluation for state 15258
                limit_text = ""
                for k, v, ib in sub_statements:
                    if ib and k == 'limit':
                        limit_text = v
                
                print("Limit text of the block:")
                print(repr(limit_text))
                
                # Trace eval_block
                owner = 'AA0'
                cores = ['AA0', 'AST', 'NAT', 'CET', 'NA2']
                claims = []
                state_cores = {15258: cores}
                state_claims = {15258: claims}
                res = eval_block(15258, owner, state_cores, state_claims, limit_text)
                print(f"eval_block result for state 15258: {res}")

if not found_ast_block:
    print("AST block was NOT parsed or found in the statements!")
