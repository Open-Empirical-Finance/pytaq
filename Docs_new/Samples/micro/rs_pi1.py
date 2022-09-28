from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting Realized Spreads and Price Impacts DataFrame using taqdaily instance
rs_pi_df = taq.compute_rs_and_pi(datetime(2016,12,7), ['IBM'])
rs_pi_df