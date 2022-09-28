from datetime import datetime
from pytaq import TaqDaily
import saspy

# connecting to SAS session
db = saspy.SASsession(cfgname='default')
taq = TaqDaily(method='saspy', db=db)

# getting symbols available for nbbo table
nbbo_symbols = taq.get_nbbo_symbols(datetime(2016,12,7))