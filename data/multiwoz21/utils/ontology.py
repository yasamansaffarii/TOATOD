# Hospital domain only
all_domains = ['hospital']
db_domains = ['hospital']

# Original slot names in goals (including booking slots)
requestable_slots_in_goals = {
    "hospital": ["address", "phone", "postcode"]
}

informable_slots_in_goals = {
    "hospital": ["department"]
}

normlize_slot_names = {
    # No changes needed for hospital slots
}

# Requestable and Informable Slots for the Hospital Domain
requestable_slots = {
    "hospital": ["address", "phone", "postcode"]
}
all_reqslot = ["address", "phone", "postcode"]  # Hospital related request slots

informable_slots = {
    "hospital": ["department"]
}
all_infslot = ["department"]  # Hospital related informable slots

# All Slots Related to Hospital
all_slots = all_reqslot + ["department"]  # All hospital slots
get_slot = {s: 1 for s in all_slots}  # Initialize get_slot dictionary
# Total slots count: 4

# Mapping slots in dialogue act to original goal slot names
da_abbr_to_slot_name = {
    # Hospital domain does not need specific mappings
}

# Dialog Acts for the Hospital Domain
dialog_acts = {
    'hospital': ['inform', 'request'],
    'general': ['bye', 'greet', 'reqmore', 'welcome']
}

# All acts for hospital domain
all_acts = []
for acts in dialog_acts.values():
    for act in acts:
        if act not in all_acts:
            all_acts.append(act)

# Dialogue Act Parameters for the Hospital Domain
dialog_act_params = {
    'inform': all_slots + ['choice'],
    'request': all_infslot + ['choice'],
    'reqmore': [],
    'welcome': [],
    'bye': [],
    'greet': []
}

# Slots and Act Tokens in Dialogues for Hospital
dialog_act_all_slots = all_slots + ['choice']
slot_name_to_slot_token = {}

# Special tokens related to database operations and responses
db_tokens = ['<sos_db>', '<eos_db>', '[db_nores]', '[db_0]', '[db_1]', '[db_2]', '[db_3]']

special_tokens = ['<pad>', '<go_r>', '<unk>', '<go_b>', '<go_a>',
                  '<eos_u>', '<eos_r>', '<eos_b>', '<eos_a>', '<go_d>', '<eos_d>',
                  '<sos_u>', '<sos_r>', '<sos_b>', '<sos_a>', '<sos_d>'] + db_tokens

sos_eos_tokens = ['<_PAD_>', '<go_r>', '<go_b>', '<go_a>', '<eos_u>', '<eos_r>', '<eos_b>', 
                  '<eos_a>', '<go_d>', '<eos_d>', '<sos_u>', '<sos_r>', '<sos_b>', '<sos_a>', '<sos_d>', 
                  '<sos_db>', '<eos_db>', '<sos_context>', '<eos_context>']

eos_tokens = {
    'user': '<eos_u>', 'user_delex': '<eos_u>',
    'resp': '<eos_r>', 'resp_gen': '<eos_r>', 'pv_resp': '<eos_r>',
    'bspn': '<eos_b>', 'bspn_gen': '<eos_b>', 'pv_bspn': '<eos_b>',
    'bsdx': '<eos_b>', 'bsdx_gen': '<eos_b>', 'pv_bsdx': '<eos_b>',
    'aspn': '<eos_a>', 'aspn_gen': '<eos_a>', 'pv_aspn': '<eos_a>',
    'dspn': '<eos_d>', 'dspn_gen': '<eos_d>', 'pv_dspn': '<eos_d>'
}

sos_tokens = {
    'user': '<sos_u>', 'user_delex': '<sos_u>',
    'resp': '<sos_r>', 'resp_gen': '<sos_r>', 'pv_resp': '<sos_r>',
    'bspn': '<sos_b>', 'bspn_gen': '<sos_b>', 'pv_bspn': '<sos_b>',
    'bsdx': '<sos_b>', 'bsdx_gen': '<sos_b>', 'pv_bsdx': '<sos_b>',
    'aspn': '<sos_a>', 'aspn_gen': '<sos_a>', 'pv_aspn': '<sos_a>',
    'dspn': '<sos_d>', 'dspn_gen': '<sos_d>', 'pv_dspn': '<sos_d>'
}
