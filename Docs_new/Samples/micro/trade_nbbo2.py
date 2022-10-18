from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting trade table and Official Complete NBBO table, but you can use local files
trade_df = taq.get_trade_table(datetime(2016,12,7), ['IBM'])
off_nbbo_df = taq.get_official_complete_nbbo(datetime(2016,12,7), ['IBM'])

# getting Trade-NBBO table using taqdaily instance
trade_nbbo_df = taq.merge_trades_nbbo(trade_df=trade_df, off_nbbo_df=off_nbbo_df)
trade_nbbo_df