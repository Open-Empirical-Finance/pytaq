from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting Trade-NBBO and Official Complete NBBO tables, but you can use local files
trade_and_nbbo_df = taq.merge_trades_nbbo(datetime(2016,12,7), ['IBM'])
off_nbbo_df = taq.get_official_complete_nbbo(datetime(2016,12,7), ['IBM'])

# getting Realized Spreads and Price Impacts DataFrame using taqdaily instance
rs_pi_df = taq.compute_rs_and_pi(trade_and_nbbo_df=trade_and_nbbo_df, off_nbbo_df=off_nbbo_df)
rs_pi_df