from bs4 import BeautifulSoup as Soup
import sqlite3 as lite

db_conn_dict = {};
queries_dict = {}
filename = "dash_config.xml"
handler = open(filename).read()
soup = Soup(handler)

dss = soup.find('datasources')

class User:
	def __init__(self, username="",password=""):
		self.username=username
		self.password=password
	def getUser(self):
		return self.username
	def getPassword(self):
		return self.password

class Query: 
	def __init__(self, query="", parmap=(),target="",parnum=0,name = ""):
		self.query = query
		self.parmap = parmap
		self.target = target
		self.parnum = parnum
		self.name = name
	def __str__(self):
		return str(self.name)+" ("+str(self.target)+") "+str(self.query)


class PyDash:
	def __init__(self, conf_file=""):
		self.db_conn_dict = {}
		self.queries_dict = {}
		self.users_dict = {}
		
		handler = open(conf_file).read()
		soup = Soup(handler)

		dss = soup.find('datasources')
		'''
		load datasources from config file
		'''
		for ds in dss.findAll('datasource'):
			dbtype = ds.find("type").string
			name= ds.find("name").string
			host= ds.find("host").string if ds.find("host")!=None else "";
			driver=ds.find("driver").string if ds.find("driver")!=None else "";
			port= ds.find("port").string if ds.find("port")!=None else "";
			user= ds.find("user").string if ds.find("user")!=None else "";
			password=ds.find("password").string if ds.find("password")!=None else "";
			service= ds.find("service").string if ds.find("service")!=None else "";
			sid= ds.find("sid").string if ds.find("sid")!=None else "";
			self.db_conn_dict[name] = {'type':dbtype,'host':host,'driver':driver,'port':port,'user':user,'password':password,'service':service,'sid':sid };
		
		'''
		load queries from xml file
		'''
		queries = soup.find('queries')
		for q in queries.findAll('query'):
			#add Query to queries dict
			query_ =  q.string
			name_ = q.attrs['name']
			target_ = q.attrs['ds']
			params = q.attrs['params'] if 'params' in q.attrs else None
			qry = Query(query = query_,parmap=(),target = target_,parnum=params,name = name_)
			self.queries_dict[name_] = qry
		'''
		load users from xml file
		'''
		users = soup.find('users')
		for u in users.findAll('user'):
			username = u.find("username").string
			pswd = u.find("password").string
			user = User(username,pswd)
			self.users_dict[username] = user

	def getSQLiteConn(self,ds):
		return lite.connect(ds['host'])
		

	'''
	Restituisce l'elenco dei nomi delle query presenti
	nel file di configurazione
	'''
	def getQueries(self):
		return self.queries_dict.keys()

	'''
	Esegue la query dato il nome della query nel datasource 
	configurato nel file di configurazione
	'''
	def executeQuery(self,queryname):
		
		q = self.queries_dict[queryname]
		ds = self.db_conn_dict[q.target]
		con = None
		if ds['type'] == 'SQLITE':
			con = self.getSQLiteConn(ds)
		
		cur = con.cursor()
		normalized_query = q.query[1: len(q.query)-1 ] 
		print "executed query: "+ normalized_query
		cur.execute(normalized_query)
		rows = cur.fetchall()
		return rows
	
	def validateUser(self, username, pswd):		
		if username in self.users_dict and self.users_dict[username].getPassword()==pswd:
			return True
		else:
			return False 


		






for ds in dss.findAll('datasource'):
	dbtype = ds.find("type").string
	name= ds.find("name").string
	host= ds.find("host").string if ds.find("host")!=None else "";
	driver=ds.find("driver").string if ds.find("driver")!=None else "";
	port= ds.find("port").string if ds.find("port")!=None else "";
	user= ds.find("user").string if ds.find("user")!=None else "";
	password=ds.find("password").string if ds.find("password")!=None else "";
	service= ds.find("service").string if ds.find("service")!=None else "";
	sid= ds.find("sid").string if ds.find("sid")!=None else "";
	db_conn_dict[name] = {'type':dbtype,'host':host,'driver':driver,'port':port,'user':user,'password':password,'service':service,'sid':sid };


queries = soup.find('queries')
for q in queries.findAll('query'):
	#add Query to queries dict
	query_ =  q.string
	name_ = q.attrs['name']
	target_ = q.attrs['ds']
	params = q.attrs['params'] if 'params' in q.attrs else None
	qry = Query(query = query_,parmap=(),target = target_,parnum=params,name = name_)
	queries_dict[name_] = qry
	print "query add: "+name_


def getSQLiteConn(ds):
	return lite.connect(ds['host'])
	

'''
Restituisce l'elenco dei nomi delle query presenti
nel file di configurazione
'''
def getQueries():
	return queries_dict.keys()

'''
Esegue la query dato il nome della query nel datasource 
configurato nel file di configurazione
'''
def executeQuery(queryname):
	
	q = queries_dict[queryname]
	ds = db_conn_dict[q.target]
	con = None
	if ds['type'] == 'SQLITE':
		con = getSQLiteConn(ds)
	
	cur = con.cursor()
	normalized_query = q.query[1: len(q.query)-1 ] 
	print "executed query: "+ normalized_query
	cur.execute(normalized_query)
	rows = cur.fetchall()
	return rows
	

#-----------------------------------------------
# TEST

print "Datasources"
for k,v in db_conn_dict.items():
	print k
	print v
print "Queries: "+str(len(queries_dict.items()))
for k,v in queries_dict.items():
	print k

print getQueries()
print executeQuery("S_ALL")

pyDash = PyDash('dash_config.xml')

print pyDash.validateUser('developer','developer11');
