import json, random

class MultiWozDB(object):
    def __init__(self, db_paths):
        """Initialize the database by loading the hospital data."""
        self.dbs = {}
        with open(db_paths['hospital'], 'r') as f:
            self.dbs['hospital'] = json.loads(f.read().lower())

    def query_jsons(self, constraints):
        """
        Returns a list of entities for the 'hospital' domain based on belief state annotations.
        
        Args:
            constraints (dict): The constraints specified for querying the hospital database.
        
        Returns:
            list: A list of matched entities satisfying the constraints.
        """
        # If department is specified, search for matching entries
        if constraints.get('department'):
            for entry in self.dbs['hospital']:
                if entry.get('department') == constraints['department']:
                    return [entry]
        # If no department constraint is given, return an empty list
        return []

if __name__ == '__main__':
    # Define the path to the hospital database
    db_paths = {
        'hospital': 'db/hospital_db_processed.json'
    }
    # Initialize the MultiWozDB with the hospital path
    multiwoz_db = MultiWozDB(db_paths)
    
    # Example query to find hospitals with a specific department
    result = multiwoz_db.query_jsons({'department': 'radiology'})
    print(result)
