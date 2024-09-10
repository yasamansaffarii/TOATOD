import re
import progressbar

def restore_text(text):
    text = re.sub('=', '', text)
    text = re.sub(',', '', text)
    text = ' '.join(text.split()).strip()
    return text

def split_bs_text_by_domain(bs_text, bsdx_text):
    """
    This function is customized to handle only the 'hospital' domain.
    """
    res_text_list = []
    bs_text = bs_text.strip('<sos_b>').strip('<eos_b>').strip()
    bsdx_text = bsdx_text.strip('<sos_b>').strip('<eos_b>').strip()

    # Check if the domain is 'hospital'
    if '[hospital]' not in bsdx_text:
        return [], []

    # Extract the portion related to 'hospital'
    bs_list = [bs_text.split('[hospital]')[1].strip()] if '[hospital]' in bs_text else []
    bsdx_list = [bsdx_text.split('[hospital]')[1].strip()] if '[hospital]' in bsdx_text else []
    
    return bs_list, bsdx_list

def parse_bs_bsdx(bs_text, bsdx_text):
    """
    This function processes belief states within the 'hospital' domain.
    """
    dx_token_list = bsdx_text.split()
    bs_name_list = bsdx_text.split()
    token_num = len(bs_name_list)
    map_dict = {}
    res_bs_text = ''
    res_bsdx_text = ''

    for idx in range(token_num):
        curr_slot = bs_name_list[idx]
        if curr_slot.startswith('[') and curr_slot.endswith(']'):
            continue
        else:
            if idx == token_num - 1:
                curr_value = bs_text.split(' ' + curr_slot + ' ')[-1].strip()
            else:
                next_slot = bs_name_list[idx + 1]
                curr_value = bs_text.split(' ' + curr_slot + ' ')[1].split(' ' + next_slot)[0].strip()
            map_dict[curr_slot] = curr_value

    for curr_slot in bs_name_list:
        if curr_slot.startswith('[') and curr_slot.endswith(']'):
            res_bs_text += curr_slot + ' '
            res_bsdx_text += curr_slot + ' '
        else:
            res_bs_text += curr_slot + ' = ' + map_dict[curr_slot] + ' , '
            res_bsdx_text += curr_slot + ' , '

    res_bs_text = res_bs_text.strip().strip(',').strip()
    res_bsdx_text = res_bsdx_text.strip().strip(',').strip()
    return ' '.join(res_bs_text.split()).strip(), ' '.join(res_bsdx_text.split()).strip()

def overall_parsing_bs_bsdx(bs_text, bsdx_text):
    """
    This function processes the overall belief state texts specifically for the 'hospital' domain.
    """
    in_bs_text, in_bsdx_text = bs_text, bsdx_text
    if bs_text == '<sos_b> <eos_b>':
        assert bsdx_text == '<sos_b> <eos_b>'
        return bs_text, bsdx_text
    bs_text_list, bsdx_text_list = split_bs_text_by_domain(bs_text, bsdx_text)
    if not bs_text_list or not bsdx_text_list:
        return '<sos_b> <eos_b>', '<sos_b> <eos_b>'
    res_bs_text, res_bsdx_text = ' ', ' '
    for idx in range(len(bs_text_list)):
        one_bs_text, one_bsdx_text = parse_bs_bsdx(bs_text_list[idx], bsdx_text_list[idx])
        res_bs_text += one_bs_text + ' '
        res_bsdx_text += one_bsdx_text + ' '
    res_bs_text = '<sos_b> ' + res_bs_text.strip() + ' <eos_b>'
    res_bsdx_text = '<sos_b> ' + res_bsdx_text.strip() + ' <eos_b>'
    assert restore_text(res_bs_text) == in_bs_text
    assert restore_text(res_bsdx_text) == in_bsdx_text
    return res_bs_text, res_bsdx_text

def parse_action_text(text):
    """
    This function parses the action text.
    """
    in_text = text
    res_text = ''
    token_list = text.strip('<sos_a>').strip('<eos_a>').strip().split()
    token_num = len(token_list)
    for idx in range(token_num):
        curr_token = token_list[idx]
        if curr_token.startswith('[') and curr_token.endswith(']'):
            res_text += curr_token + ' '
        else:
            if idx == token_num - 1:
                res_text += curr_token
            else:
                next_token = token_list[idx + 1]
                if next_token.startswith('[') and next_token.endswith(']'):
                    res_text += curr_token + ' '
                else:
                    res_text += curr_token + ' , '
    res_text = '<sos_a> ' + ' '.join(res_text.split()).strip() + ' <eos_a>'
    assert restore_text(res_text) == in_text
    return res_text

def transform_id_dict(in_dict, data):
    """
    This function transforms an input dictionary using a tokenizer.
    """
    res_dict = {}
    for key in in_dict:
        if key in ['pointer','turn_num','turn_domain','dial_id']:
            res_dict[key] = in_dict[key]
        else:
            res_dict[key] = data.tokenized_decode(in_dict[key])
    return res_dict

def process_dict(in_dict, data):
    """
    This function processes a single dictionary entry to focus on the 'hospital' domain.
    """
    in_dict = transform_id_dict(in_dict, data)
    res_dict = in_dict.copy()
    bs_text_reform, bsdx_text_reform = overall_parsing_bs_bsdx(in_dict['bspn'], in_dict['bsdx'])
    res_dict['bspn_reform'] = bs_text_reform
    res_dict['bsdx_reform'] = bsdx_text_reform
    action_text_reform = parse_action_text(in_dict['aspn'])
    res_dict['aspn_reform'] = action_text_reform
    return res_dict

def process_data_list(data_list):
    """
    This function processes a list of data entries to handle only 'hospital' domain data.
    """
    res_list = []
    p = progressbar.ProgressBar(len(data_list))
    p.start()
    p_idx = 0
    for item in data_list:
        p_idx += 1
        p.update(p_idx)
        try:
            one_res_list = [process_dict(sub_item, data) for sub_item in item if '[hospital]' in sub_item['bspn']]
        except: 
            continue
        res_list.append(one_res_list)
    p.finish()
    print(len(res_list), len(data_list))
    return res_list
