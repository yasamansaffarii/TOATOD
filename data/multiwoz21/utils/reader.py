import logging
import json
import spacy
from utils import utils
from utils import ontology
from collections import OrderedDict
from utils.db_ops import MultiWozDB

import progressbar

class _ReaderBase(object):

    def __init__(self):
        self.train, self.dev, self.test = [], [], []
        self.vocab = None
        self.db = None
        self.set_stats = {}

    def _bucket_by_turn(self, encoded_data):
        turn_bucket = {}
        for dial in encoded_data:
            turn_len = len(dial)
            if turn_len not in turn_bucket:
                turn_bucket[turn_len] = []
            turn_bucket[turn_len].append(dial)
        del_l = []
        for k in turn_bucket:
            if k >= 5:
                del_l.append(k)
            logging.debug("bucket %d instance %d" % (k, len(turn_bucket[k])))
        return OrderedDict(sorted(turn_bucket.items(), key=lambda i: i[0]))

    def transpose_batch(self, batch):
        dial_batch = []
        turn_num = len(batch[0])
        for turn in range(turn_num):
            turn_l = {}
            for dial in batch:
                this_turn = dial[turn]
                for k in this_turn:
                    if k not in turn_l:
                        turn_l[k] = []
                    turn_l[k].append(this_turn[k])
            dial_batch.append(turn_l)
        return dial_batch

    def inverse_transpose_turn(self, turn_list):
        dialogs = {}
        turn_num = len(turn_list)
        dial_id = turn_list[0]['dial_id']
        dialogs[dial_id] = []
        for turn_idx in range(turn_num):
            dial_turn = {}
            turn = turn_list[turn_idx]
            for key, value in turn.items():
                if key == 'dial_id':
                    continue
                if key == 'pointer' and self.db is not None:
                    turn_domain = turn['turn_domain'][-1]
                    value = self.db.pointerBack(value, turn_domain)
                dial_turn[key] = value
            dialogs[dial_id].append(dial_turn)
        return dialogs

    def inverse_transpose_batch(self, turn_batch_list):
        dialogs = {}
        total_turn_num = len(turn_batch_list)
        for idx_in_batch, dial_id in enumerate(turn_batch_list[0]['dial_id']):
            dialogs[dial_id] = []
            for turn_n in range(total_turn_num):
                dial_turn = {}
                turn_batch = turn_batch_list[turn_n]
                for key, v_list in turn_batch.items():
                    if key == 'dial_id':
                        continue
                    value = v_list[idx_in_batch]
                    if key == 'pointer' and self.db is not None:
                        turn_domain = turn_batch['turn_domain'][idx_in_batch][-1]
                        value = self.db.pointerBack(value, turn_domain)
                    dial_turn[key] = value
                dialogs[dial_id].append(dial_turn)
        return dialogs

    def get_eval_data(self, set_name='dev'):
        name_to_set = {'train': self.train, 'test': self.test, 'dev': self.dev}
        dial = name_to_set[set_name]

        if set_name not in self.set_stats:
            self.set_stats[set_name] = {}
        num_turns = 0
        num_dials = len(dial)
        for d in dial:
            num_turns += len(d)

        self.set_stats[set_name]['num_turns'] = num_turns
        self.set_stats[set_name]['num_dials'] = num_dials

        return dial
    
    def get_nontranspose_data_iterator(self, all_batches):
        for i, batch in enumerate(all_batches):
            yield batch

    def get_data_iterator(self, all_batches):
        for i, batch in enumerate(all_batches):
            yield self.transpose_batch(batch)


class MultiWozReader(_ReaderBase):
    def __init__(self, tokenizer, cfg, data_mode='train'):
        super().__init__()
        self.data_mode = data_mode
        self.nlp = spacy.load('en_core_web_sm')
        self.cfg = cfg

        self.db = MultiWozDB(self.cfg.dbs)
        self.vocab_size = self._build_vocab()

        self.tokenizer = tokenizer

        self.domain_files = json.loads(open(self.cfg.domain_file_path, 'r').read())

        test_list = [l.strip().lower() for l in open(self.cfg.test_list, 'r').readlines()]
        dev_list = [l.strip().lower() for l in open(self.cfg.dev_list, 'r').readlines()]
        self.dev_files, self.test_files = {}, {}
        for fn in test_list:
            self.test_files[fn.replace('.json', '')] = 1
        for fn in dev_list:
            self.dev_files[fn.replace('.json', '')] = 1

        # for domain expanse aka. Cross domain
        self.exp_files = {}
        if 'hospital' not in cfg.exp_domains:
            raise ValueError('The configuration must include "hospital" domain.')
        fn_list = self.domain_files.get('hospital')
        if not fn_list:
            raise ValueError('[hospital] is an invalid experiment setting')
        for fn in fn_list:
            self.exp_files[fn.replace('.json', '')] = 1

        self._load_data()
        self.multi_acts_record = None

    def _build_vocab(self):
        self.vocab = utils.Vocab(self.cfg.vocab_size)
        vp = self.cfg.vocab_path_train
        self.vocab.load_vocab(vp)
        return self.vocab.vocab_size

    def _load_data(self, save_temp=False):
        print('Start tokenizing data...')
        self.data = json.loads(
            open(self.cfg.data_path+self.cfg.data_file, 'r', encoding='utf-8').read().lower())
        self.train, self.dev, self.test = [], [], []
        print('Start encoding data...')
        p = progressbar.ProgressBar(len(self.data))
        p.start()
        p_idx = 0
        for fn, dial in self.data.items():
            p.update(p_idx)
            p_idx += 1
            if '.json' in fn:
                fn = fn.replace('.json', '')
            if self.exp_files.get(fn):
                if self.dev_files.get(fn):
                    self.dev.append(self._get_encoded_data(fn, dial))
                elif self.test_files.get(fn):
                    self.test.append(self._get_encoded_data(fn, dial))
                else:
                    if self.data_mode == 'train':
                        self.train.append(self._get_encoded_data(fn, dial))
                    elif self.data_mode == 'test':
                        pass
                    else:
                        raise Exception('Wrong Reader Data Mode!!!')
        p.finish()

    def _get_encoded_data(self, fn, dial):
        encoded_dial = []
        for idx, t in enumerate(dial['log']):  # tokenize to list of ids
            enc = {}
            enc['dial_id'] = fn
            enc['user'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_u> ' +
                t['user'] + ' <eos_u>'))
            enc['usdx'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_u> ' +
                t['user'] + ' <eos_u>'))
            enc['resp'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_r> ' +
                t['resp'] + ' <eos_r>'))
            enc['nodelx_resp'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_r> ' +
                t['nodelx_resp'] + ' <eos_r>'))
            enc['bspn'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_b> ' +
                t['constraint'] + ' <eos_b>'))
            enc['bsdx'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_b> ' +
                t['cons_delex'] + ' <eos_b>'))
            enc['aspn'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_a> ' +
                t['sys_act'] + ' <eos_a>'))
            enc['dspn'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_d> ' +
                t['turn_domain'] + ' <eos_d>'))

            enc['pointer'] = [int(i) for i in t['pointer'].split(',')]
            enc['turn_domain'] = t['turn_domain'].split()
            enc['turn_num'] = t['turn_num']

            db_pointer = self.bspan_to_DBpointer(t['constraint'], t['turn_domain'].split())
            enc['db'] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(
                '<sos_db> ' + db_pointer + ' <eos_db>'))

            encoded_dial.append(enc)
        return encoded_dial

    def bspan_to_DBpointer(self, bspn, domain_list):
        if self.db is None:
            return bspn
        db_pointer = self.db.get_pointer(bspn, domain_list)
        return db_pointer

    def _load_temp_data(self, save_temp=False):
        pass
