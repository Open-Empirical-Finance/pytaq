from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting nbbo table and quote table, but you can use local files
nbbo_df = taq.get_nbbo_table(datetime(2016,12,7), ['IBM'])
quote_df = taq.get_quote_table(datetime(2016,12,7), ['IBM'])

# getting official complete NBBO table using taqdaily instance
off_nbbo_df = taq.get_official_complete_nbbo(nbbo_df=nbbo_df, quote_df=quote_df)
off_nbbo_df