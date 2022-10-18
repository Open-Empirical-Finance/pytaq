from datetime import datetime
from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username'
db = wrds.Connection(wrds_username='username')
taq = TaqDaily(method='PostgreSQL', db=db)

# getting official complete NBBO table using taqdaily instance
off_nbbo_df = taq.get_official_complete_nbbo(datetime(2016,12,7), ['IBM'])
off_nbbo_df