from parse_mod_data_2024 import tokenize, parse_to_structures, eval_block_struct

block_text = """
limit = {
    is_core_of = BRA
    OR = {
        is_core_of = YMM
        is_core_of = CNL
    }
}
BRA = {
    transfer_state = PREV
}
"""

tokens = tokenize(block_text)
statements = parse_to_structures(tokens)
print("Parsed statements of block:")
for k, v, ib in statements:
    print(f"  Key: {k}, IsBlock: {ib}")
    if ib:
        print("  Sub-statements:")
        for sk, sv, sib in v:
            print(f"    Key: {sk}, IsBlock: {sib}, Value: {sv}")

limit_statements = []
for k, v, ib in statements:
    if k == 'limit':
        limit_statements = v

# Trace evaluation for state 1 (France)
# Cores for state 1 is ['FRA']
cores = ['FRA']
state_cores = {1: cores}
state_claims = {1: []}
owner = 'FRA'

res = eval_block_struct(1, owner, state_cores, state_claims, limit_statements)
print(f"Evaluation result for state 1: {res}")
