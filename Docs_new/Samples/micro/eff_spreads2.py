from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting Trade-NBBO table, but you can use local files
trade_and_nbbo_df = taq.merge_trades_nbbo(datetime(2016,12,7), ['IBM'])

# getting Effective Spreads DataFrame using taqdaily instance
eff_spreads_df = taq.compute_effective_spreads(trade_and_nbbo_df=trade_and_nbbo_df)
eff_spreads_df