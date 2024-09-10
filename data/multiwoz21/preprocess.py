import json, os, re, copy, zipfile
import spacy
from collections import OrderedDict
from tqdm import tqdm

from utils import ontology
from utils.config import Config
from utils.db_ops import MultiWozDB
from utils.clean_dataset import clean_slot_values, clean_text
from utils import utils


def get_db_values(value_set_path):  # value_set.json, all the domain[slot] values in datasets
    processed = {}
    bspn_word = []
    nlp = spacy.load('en_core_web_sm')

    with open(value_set_path, 'r') as f:  # read value set file in lower
        value_set = json.loads(f.read().lower())

    with open('ontology.json', 'r') as f:  # read ontology in lower, all the domain-slot values
        otlg = json.loads(f.read().lower())

    # Process only the "hospital" domain
    hospital_value_set = value_set.get('hospital', {})
    hospital_ontology = {k: v for k, v in otlg.items() if k.startswith('hospital')}

    # Add all informable slots to bspn_word, create lists holder for values
    processed['hospital'] = {}
    bspn_word.append('[hospital]')
    for slot, values in hospital_value_set.items():
        s_p = ontology.normlize_slot_names.get(slot, slot)
        if s_p in ontology.informable_slots['hospital']:
            bspn_word.append(s_p)
            processed['hospital'][s_p] = []

    # Add all words of values of informable slots to bspn_word
    for slot, values in hospital_value_set.items():
        s_p = ontology.normlize_slot_names.get(slot, slot)
        if s_p in ontology.informable_slots['hospital']:
            for v in values:
                _, v_p = clean_slot_values('hospital', slot, v)
                v_p = ' '.join([token.text for token in nlp(v_p)]).strip()
                processed['hospital'][s_p].append(v_p)
                for x in v_p.split():
                    if x not in bspn_word:
                        bspn_word.append(x)

    # Split domain-slots to domains and slots for "hospital"
    for domain_slot, values in hospital_ontology.items():
        domain, slot = domain_slot.split('-')
        if slot == 'price range':
            slot = 'pricerange'
        if slot == 'book stay':
            slot = 'stay'
        if slot == 'book day':
            slot = 'day'
        if slot == 'book people':
            slot = 'people'
        if slot == 'book time':
            slot = 'time'
        if slot == 'arrive by':
            slot = 'arrive'
        if slot == 'leave at' or slot == 'leaveat':
            slot = 'leave'

        if slot not in processed['hospital']:  # add all slots and words of values if not already in processed and bspn_word
            processed['hospital'][slot] = []
            bspn_word.append(slot)
        for v in values:
            _, v_p = clean_slot_values('hospital', slot, v)
            v_p = ' '.join([token.text for token in nlp(v_p)]).strip()
            if v_p not in processed['hospital'][slot]:
                processed['hospital'][slot].append(v_p)
                for x in v_p.split():
                    if x not in bspn_word:
                        bspn_word.append(x)

    # Save the processed values and words
    with open(value_set_path.replace('.json', '_processed_hospital.json'), 'w') as f:
        json.dump(processed, f, indent=2)  # save processed hospital json
    with open('data/multi-woz-processed/bspn_word_collection_hospital.json', 'w') as f:
        json.dump(bspn_word, f, indent=2)  # save bspn_word

    print('DB value set processed for hospital domain! ')
