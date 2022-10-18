from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting quoted spreads and depth table using taqdaily instance
spreads_df = taq.compute_spreads(datetime(2016,12,7), ['IBM'])
spreads_df