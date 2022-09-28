from pytaq import TaqDaily
import saspy

# connecting to SAS session
db = saspy.SASsession(cfgname='default')

# creating TaqDaily object
taq = TaqDaily(method='saspy', db=db)