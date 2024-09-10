import os, json, copy, re, zipfile, shutil, urllib
from urllib import request
from zipfile import ZipFile
from io import BytesIO
from collections import OrderedDict
from utils.ontology import all_domains

# 2.1
data_path = '../multiwoz21/'
save_path = 'multi-woz-analysis/'
save_path_exp = 'multi-woz-processed/'
data_file = 'data.json'
domains = all_domains


def loadDataMultiWoz():
    data_url = os.path.join(data_path, 'data.json')
    dataset_url = "https://github.com/budzianowski/multiwoz/blob/master/data/MultiWOZ_2.1.zip?raw=true"
    download_path = data_path
    
    """The function loadDataMultiWoz() checks if the MultiWOZ 2.1 dataset 
    is present locally. If not, it downloads the dataset from a URL, 
    unzips it, and organizes the files into the required directories."""
    
    if not os.path.exists(os.path.join(data_url)):
        print("Downloading and unzipping the MultiWOZ dataset")
        resp = urllib.request.urlopen(dataset_url)
        zip_ref = ZipFile(BytesIO(resp.read()))
        zip_ref.extractall(download_path)
        zip_ref.close()
        
        """moveFilestoDB moves domain-specific database files 
        (e.g., attraction_db.json, hotel_db.json) to a database directory (db/).
        moveFiles moves general dataset files (e.g., data.json, slot_descriptions.json) 
        to the main data path (data_path)."""
        
        extract_path = os.path.join(download_path, 'MultiWOZ_2.1')
        moveFilestoDB(src_path=extract_path, dst_path= 'db/')
        moveFiles(src_path=extract_path, dst_path= data_path)
        return

def moveFilestoDB(src_path, dst_path):
    os.makedirs(dst_path, exist_ok=True)
    """shutil.copy(os.path.join(src_path, 'attraction_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'attraction_db.json'))"""
    
    shutil.copy(os.path.join(src_path, 'hospital_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'hospital_db.json'))
    
    """shutil.copy(os.path.join(src_path, 'hotel_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'hotel_db.json'))
    shutil.copy(os.path.join(src_path, 'police_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'police_db.json'))
    shutil.copy(os.path.join(src_path, 'restaurant_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'restaurant_db.json'))
    shutil.copy(os.path.join(src_path, 'taxi_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'taxi_db.json'))
    shutil.copy(os.path.join(src_path, 'train_db.json'), dst_path)
    os.remove(os.path.join(src_path, 'train_db.json'))"""
    return

def moveFiles(src_path, dst_path):
    shutil.copy(os.path.join(src_path, 'data.json'), dst_path)
    os.remove(os.path.join(src_path, 'data.json'))
    shutil.copy(os.path.join(src_path, 'slot_descriptions.json'), dst_path)
    os.remove(os.path.join(src_path, 'slot_descriptions.json'))
    shutil.copy(os.path.join(src_path, 'system_acts.json'), dst_path)
    os.remove(os.path.join(src_path, 'system_acts.json'))
    shutil.copy(os.path.join(src_path, 'testListFile.txt'), dst_path)
    os.remove(os.path.join(src_path, 'testListFile.txt'))
    shutil.copy(os.path.join(src_path, 'valListFile.txt'), dst_path)
    os.remove(os.path.join(src_path, 'valListFile.txt'))
    shutil.rmtree(os.path.join(src_path))
    shutil.rmtree('__MACOSX')
    return

"""The analysis() function performs the main analysis and data compression tasks.
It reads the data, extracts relevant statistics, and generates summaries:"""
"""Adjust the analysis() function to filter data and compute statistics only for
the "hospital" domain. Here is the modified part of the function:"""
def analysis():
    compressed_raw_data = {}
    goal_of_dials = {}
    req_slots = {'hospital': []}
    info_slots = {'hospital': []}
    dom_count = {}
    dom_fnlist = {}
    all_domain_specific_slots = set()
    
    archive = zipfile.ZipFile(data_path + data_file + '.zip', 'w')
    archive.write(data_path + data_file)
    archive.close()

    archive = zipfile.ZipFile(data_path + data_file + '.zip', 'r')
    data = archive.open(data_path + data_file, 'r').read().decode('utf-8').lower()
    ref_nos = list(set(re.findall(r'\"reference\"\: \"(\w+)\"', data)))

    with open(data_path + data_file, 'r') as f:
        data = json.load(f)

    for fn, dial in data.items():
        goals = dial['goal']
        logs = dial['log']

        # Only process dialogues related to the "hospital" domain
        if 'hospital' not in goals:
            continue

        # get compressed_raw_data and goal_of_dials
        compressed_raw_data[fn] = {'goal': {}, 'log': []}
        goal_of_dials[fn] = {}

        # Process goals for the "hospital" domain
        if 'hospital' in goals:
            compressed_raw_data[fn]['goal']['hospital'] = goals['hospital']
            goal_of_dials[fn]['hospital'] = goals['hospital']

        # Process dialogue logs
        for turn in logs:
            if not turn['metadata']:  # user's turn
                compressed_raw_data[fn]['log'].append({'text': turn['text']})
            else:  # system's turn
                meta = turn['metadata']
                if 'hospital' in meta:
                    turn_dict = {'text': turn['text'], 'metadata': {'hospital': {}}}
                    book, semi = meta['hospital']['book'], meta['hospital']['semi']

                    # Add "book" information if present
                    if any(value not in ['', []] for value in book.values()):
                        turn_dict['metadata']['hospital']['book'] = book

                    # Add "semi" information if present
                    if any(value not in ['', []] for value in semi.values()):
                        turn_dict['metadata']['hospital']['semi'] = {s: v for s, v in semi.items() if v != 'not mentioned'}

                    compressed_raw_data[fn]['log'].append(turn_dict)

        # Process domain statistics
        dom_str = 'hospital'
        if not dom_count.get(dom_str + '_single'):
            dom_count[dom_str + '_single'] = 1
        else:
            dom_count[dom_str + '_single'] += 1

        if not dom_fnlist.get(dom_str + '_single'):
            dom_fnlist[dom_str + '_single'] = [fn]
        else:
            dom_fnlist[dom_str + '_single'].append(fn)

        # Process slot statistics
        info_ss = goals['hospital'].get('info', {})
        book_ss = goals['hospital'].get('book', {})
        req_ss = goals['hospital'].get('reqt', {})
        
        for info_s in info_ss:
            all_domain_specific_slots.add('hospital-' + info_s)
            if info_s not in info_slots['hospital']:
                info_slots['hospital'].append(info_s)
        for book_s in book_ss:
            if 'book_' + book_s not in info_slots['hospital'] and book_s not in ['invalid', 'pre_invalid']:
                all_domain_specific_slots.add('hospital-' + book_s)
                info_slots['hospital'].append('book_' + book_s)
        for req_s in req_ss:
            if req_s not in req_slots['hospital']:
                req_slots['hospital'].append(req_s)

    # Save the results
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if not os.path.exists(save_path_exp):
        os.mkdir(save_path_exp)

    with open(save_path + 'req_slots.json', 'w') as sf:
        json.dump(req_slots, sf, indent=2)
    with open(save_path + 'info_slots.json', 'w') as sf:
        json.dump(info_slots, sf, indent=2)
    with open(save_path + 'all_domain_specific_info_slots.json', 'w') as sf:
        json.dump(list(all_domain_specific_slots), sf, indent=2)
        print("slot num:", len(list(all_domain_specific_slots)))
    with open(save_path + 'goal_of_each_dials.json', 'w') as sf:
        json.dump(goal_of_dials, sf, indent=2)
    with open(save_path + 'compressed_data.json', 'w') as sf:
        json.dump(compressed_raw_data, sf, indent=2)
    with open(save_path + 'domain_count.json', 'w') as sf:
        json.dump(dom_count, sf, indent=2)
    with open(save_path_exp + 'reference_no.json', 'w') as sf:
        json.dump(ref_nos, sf, indent=2)
    with open(save_path_exp + 'domain_files.json', 'w') as sf:
        json.dump(dom_fnlist, sf, indent=2)



if __name__ == '__main__':
    loadDataMultiWoz()
    analysis()
