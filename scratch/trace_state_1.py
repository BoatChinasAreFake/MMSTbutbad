from parse_mod_data_2024 import parse_base_states, tokenize, parse_to_structures, eval_block_struct
import re

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

# Let's read water.txt and find WTR_2024_start
water_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\national_focus\water.txt"
with open(water_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    
start_idx = content.find('id = WTR_2024_start')
reward_start = content.find('completion_reward', start_idx)
brace_count = 0
idx = content.find('{', reward_start)
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

tokens = tokenize(block_content)
statements = parse_to_structures(tokens)

current_owners = dict(state_owners)

# Let's run process_effects but track state 1
def process_effects(stmts, depth=0):
    for key, val, is_block in stmts:
        if is_block:
            if key == 'every_state':
                limit_statements = []
                transfers = []
                for skey, sval, sis_block in val:
                    if sis_block and skey == 'limit':
                        limit_statements = sval
                    elif sis_block and len(skey) == 3:
                        transfers.append((skey.upper(), sval))
                    elif not sis_block and skey == 'transfer_state_to':
                        transfers.append((sval.upper(), None))
                        
                owner = current_owners[1]
                # Check if this block would transfer state 1
                if not limit_statements or eval_block_struct(1, owner, state_cores, state_claims, limit_statements):
                    for target_tag, sub_block in transfers:
                        if target_tag == 'EUR':
                            continue
                        if current_owners[1] != target_tag:
                            print(f"State 1 transferred: {current_owners[1]} -> {target_tag}")
                            print(f"  Cause: every_state block at depth {depth}")
                            # Print the limit_statements and transfers
                            print("  Limit statements:", limit_statements)
                            print("  Transfers:", transfers)
                            current_owners[1] = target_tag
            elif len(key) == 3:
                tag = key.upper()
                if tag != 'EUR':
                    for skey, sval, sis_block in val:
                        if not sis_block and skey == 'transfer_state':
                            try:
                                sid = int(sval)
                                if sid == 1:
                                    print(f"State 1 direct transfer: {current_owners[1]} -> {tag}")
                                    current_owners[sid] = tag
                            except ValueError:
                                pass
            else:
                process_effects(val, depth+1)

process_effects(statements)
