import logging
import time
import os

class Config:
    def __init__(self, data_prefix):
        # Initialize with the data directory prefix
        self.data_prefix = data_prefix
        self._multiwoz_hospital_init()

    def _multiwoz_hospital_init(self):
        # Define the paths for vocabulary, data, and lists
        self.vocab_path_train = self.data_prefix + '/multi-woz-processed/vocab'
        self.data_path = self.data_prefix + '/multi-woz-processed/'
        self.data_file = 'data_for_damd.json'
        self.dev_list = self.data_prefix + '/valListFile.txt'
        self.test_list = self.data_prefix + '/testListFile.txt'

        # Focus only on the hospital domain database
        self.dbs = {
            'hospital': self.data_prefix + '/db/hospital_db_processed.json'
        }

        # Specify the domain file path
        self.domain_file_path = self.data_prefix + '/multi-woz-processed/domain_files.json'

        # Set experiment domains to hospital only
        self.exp_domains = ['hospital']

        # Configuration options for dialog state tracking
        self.enable_aspn = True  # Enable action span
        self.use_pvaspn = False  # Do not use policy vector action span
        self.enable_bspn = True  # Enable belief state span
        self.bspn_mode = 'bspn'  # Set mode to 'bspn' or 'bsdx'
        self.enable_dspn = False # Disable dialog state prediction network
        self.enable_dst = False  # Disable dialog state tracking

        # Limit maximum context length and vocabulary size
        self.max_context_length = 900
        self.vocab_size = 3000
