from pytaq import TaqDaily
import wrds

# connecting to WRDS database, use your username instead of 'username', then enter password
db = wrds.Connection(wrds_username='username')

# creating TaqDaily object
taq = TaqDaily(method='PostgreSQL', db=db)