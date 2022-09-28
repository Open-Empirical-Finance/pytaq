from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting trade table using taqdaily instance
trade_df = taq.get_trade_table(datetime(2016,12,7), ['IBM'])
trade_df