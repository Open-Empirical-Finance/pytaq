from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting Effective Spreads DataFrame using taqdaily instance
eff_spreads_df = taq.compute_effective_spreads(datetime(2016,12,7), ['IBM'])
eff_spreads_df