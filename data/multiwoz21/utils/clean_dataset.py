# -*- coding: utf-8 -*-
import re
from utils import ontology

def my_clean_text(text):
    text = re.sub(r'([a-zT]+)\.([a-z])', r'\1 . \2', text)   # 'abc.xyz' -> 'abc . xyz'
    text = re.sub(r'(\w+)\.\.? ', r'\1 . ', text)   # if 'abc. ' -> 'abc . '
    return text


def clean_text(text):
    text = text.strip()
    text = text.lower()
    text = text.replace(u"’", "'")
    text = text.replace(u"‘", "'")
    text = text.replace(';', ',')
    text = text.replace('"', ' ')
    text = text.replace('/', ' and ')
    text = text.replace("don't", "do n't")
    text = clean_time(text)
    baddata = { r'c\.b (\d), (\d) ([a-z])\.([a-z])': r'cb\1\2\3\4',
                'c.b. 1 7 db.y': 'cb17dy',
                'c.b.1 7 db.y': 'cb17dy',
                'c.b 25, 9 a.q': 'cb259aq',
                'isc.b 25, 9 a.q': 'is cb259aq',
                'c.b2, 1 u.f': 'cb21uf',
                'c.b 1,2 q.a':'cb12qa',
                '0-122-336-5664': '01223365664',
                'postcodecb21rs': 'postcode cb21rs',
                r'i\.db': 'id',
                ' i db ': 'id',
                'Telephone:01223358966': 'Telephone: 01223358966',
                'depature': 'departure',
                'depearting': 'departing',
                '-type': ' type',
                r"b[\s]?&[\s]?b": "bed and breakfast",
                "b and b": "bed and breakfast",
                r"guesthouse[s]?": "guest house",
                r"swimmingpool[s]?": "swimming pool",
                "wo n\'t": "will not",
                " \'db ": " would ",
                " \'m ": " am ",
                " \'re' ": " are ",
                " \'ll' ": " will ",
                " \'ve ": " have ",
                r'^\'': '',
                r'\'$': '',
              }
    for tmpl, good in baddata.items():
        text = re.sub(tmpl, good, text)

    text = re.sub(r'([a-zT]+)\.([a-z])', r'\1 . \2', text)   # 'abc.xyz' -> 'abc . xyz'
    text = re.sub(r'(\w+)\.\.? ', r'\1 . ', text)   # if 'abc. ' -> 'abc . '

    with open('utils/mapping.pair', 'r') as fin:
        for line in fin.readlines():
            fromx, tox = line.replace('\n', '').split('\t')
            text = ' ' + text + ' '
            text = text.replace(' ' + fromx + ' ', ' ' + tox + ' ')[1:-1]

    return text


def clean_time(utter):
    utter = re.sub(r'(\d+) ([ap]\.?m)', lambda x: x.group(1) + x.group(2), utter)   # 9 am -> 9am
    utter = re.sub(r'((?<!\d)\d:\d+)(am)?', r'0\1', utter)
    utter = re.sub(r'((?<!\d)\d)am', r'0\1:00', utter)
    utter = re.sub(r'((?<!\d)\d)pm', lambda x: str(int(x.group(1))+12)+':00', utter)
    utter = re.sub(r'(\d+)(:\d+)pm', lambda x: str(int(x.group(1))+12)+x.group(2), utter)
    utter = re.sub(r'(\d+)a\.?m',r'\1', utter)
    return utter


def clean_slot_values(domain, slot, value):
    value = clean_text(value)
    if not value:
        value = ''
    elif value == 'not mentioned':
        value = ''
    
    # Specific cleaning for the 'hospital' domain
    if domain == 'hospital':
        if slot == 'name':
            if value == 'addenbrookes hospital':
                value = 'addenbrookes'
        elif slot == 'department':
            if value == 'childrens hospital':
                value = 'children hospital'
        elif slot == 'id':
            if value == '12345':
                value = 'h12345'
    
    # Normalize slot names if applicable
    if ontology.normlize_slot_names.get(slot):
        slot = ontology.normlize_slot_names[slot]
    return slot, value
