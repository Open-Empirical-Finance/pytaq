from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting Trade-NBBO table using taqdaily instance
trade_nbbo_df = taq.merge_trades_nbbo(datetime(2016,12,7), ['IBM'])
trade_nbbo_df