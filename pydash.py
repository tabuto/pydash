from bs4 import BeautifulSoup as Soup
from bs4 import CData
import os
import re

try:
	import sqlite3 as lite
except ImportError:
	print "Sqlite3 required to execute Sqlite queries"


try:
	import MySQLdb as mdb
except ImportError:
	print "MySQLdb required to execute MySQL queries"

try:
	import cx_Oracle
except ImportError:
	print "cxOracle required to execute oracle queries"
	

class Param:
	def __init__(self, pos =0,name="",paramType="",combovalues=[],description=""):
		self.position = pos
		self.name = name
		self.paramType=paramType
		self.combovalues=combovalues
		self.description=description
	def serialize(self):
		return {
			'position': self.position, 
			'name': self.name,
			'paramType': self.paramType,
			'combovalues':self.combovalues,
			'description':self.description,
			}
	def __str__(self):
		return str(self.position)+") "+str(self.name)+" ("+str(self.paramType)+") "+" values: "+str(self.combovalues)


class User:
	def __init__(self, username="",password="", datasources=()):
		self.username=username
		self.password=password
		self.datasources = datasources
	def getUsername(self):
		return self.username
	def getPassword(self):
		return self.password
	def getDatasources(self):
		return self.datasources
	def serialize(self):
		return {
			'username': self.username, 
			'password': self.password,
			'datasources': self.datasources,
			}
	def __str__(self):
		return str(self.username)+" ("+str(self.datasources)+") "

class Query: 
	def __init__(self, query="", parmap=(),target="",parnum=0,name = "", selectNumber=1, description=""):
		self.query = query
		self.parmap = parmap
		self.target = target
		self.parnum = parnum
		self.name = name
		self.selectNumber=selectNumber
		self.description=description
		
		
	def serialize(self):
		return {
			'query': self.query, 
			'parmap': self.parmap,
			'target': self.target,
			'parnum': self.parnum,
			'name': self.name,
			'selectNumber': self.selectNumber
			}
	def __str__(self):
		return str(self.name)+" ("+str(self.target)+") "+str(self.query)


class PyDash:
	def __init__(self, conf_file=""):
		self.db_conn_dict = {}
		self.queries_dict = {}
		self.users_dict = {}
		self.chartboards = [];
		self.appName=""
		
		handler = open(conf_file).read()
		soup = Soup(handler,'xml')

		'''
		load env variable  from config file
		'''
		env = soup.find('env')
		
		orahome = env.find('ora_home').string
		ldlibpath = env.find('ld_library_path').string
		self.appName= env.find('appName').string

		os.putenv('ORACLE_HOME', orahome)
		os.putenv('LD_LIBRARY_PATH',ldlibpath)
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
			query_ =  q.find('sql').string
			
			params=()
			name_ = q.attrs['name']
			target_ = q.attrs['ds']
			paramNum = q.attrs['params'] if 'params' in q.attrs else None
			_desc = q.attrs['description'] if 'description' in q.attrs else ""
			select_number = int(q.attrs['selects']) if 'selects' in q.attrs else 1
			
			if paramNum:
				k=1;
				parameters = q.find('params')
				for p in parameters.findAll('param'): 
					_p_name=p.attrs['name']
					_p_type=p.attrs['paramtype']
					_p_desc=p.attrs['description']
					_combo_vals =p.attrs['vals'] if 'vals' in p.attrs else ''
					toAdd=Param(k,_p_name,_p_type,_combo_vals.split(','),_p_desc )
					params=params+(toAdd,)
					k=k+1
					#print toAdd,'from xml: ',_combo_vals
			
			qry = Query(query = query_,parmap=params,target = target_,parnum=paramNum,name = name_,selectNumber=select_number,description=_desc)
			#print qry
			self.queries_dict[name_] = qry
		'''
		load users from xml file
		'''
		users = soup.find('users')
		for u in users.findAll('user'):
			
			username = u.find("username").string
			pswd = u.find("password").string
			dslist = ();
			datasourceslist = u.findAll("ds")
			for d in datasourceslist:
				dslist = dslist+(d.string,)
				 

			user = User(username,pswd,dslist)
			self.users_dict[username] = user
		'''
		load chartboards from xml file
		'''
		chartsb=soup.find('chartboards')
		
		for c in chartsb.findAll('chartboard'):
			toadd={}
			_user = c.find("user").string
			_type=c.find("type").string
			_querydata=c.find("querydata").string
			_title = c.find("title").string
			
			toadd['user']=_user
			toadd['type']=_type
			toadd['querydata']=_querydata
			toadd['title']=_title
			toadd['inverted']=True if 'inverted' in c.attrs else False
			self.chartboards.append(toadd)
			

	def getSQLiteConn(self,ds):
		return lite.connect(ds['host'])
	def getMySQLConn(self,ds):
		return mdb.connect(ds['host'],ds['user'],ds['password'],ds['service'],int(ds['port']));
	def getOracleConn(self, ds):
		conn = ds['user']+'/'+ds['password']+'@'+ds['host']+':'+ds['port']+'/'+ds['service']
		#print conn
		return cx_Oracle.connect(conn)

	'''
	Restituisce l'elenco dei nomi delle query presenti
	nel file di configurazione
	'''
	def getQueriesName(self):
		return self.queries_dict.keys()
	
	def getQueries(self):
		return self.queries_dict.values()
	
	def getQueryByName(self, name):
		return self.queries_dict.get(name)
	
	
	
	'''
	Esegue la query dato il nome della query nel datasource 
	configurato nel file di configurazione
	'''
	def executeQuery(self,queryname,values=None, user=None):
		q = self.queries_dict[queryname]
		if user and self.validateUser(user.getUsername(),user.getPassword()):
			if q.target not in self.users_dict[user.getUsername()].getDatasources():
				raise Exception("User does not have permission to execute this query"); 
		
		
		ds = self.db_conn_dict[q.target]
		con = None
		if ds['type'] == 'SQLITE':
			con = self.getSQLiteConn(ds)
		elif ds['type'] == 'MYSQL':
			con = self.getMySQLConn(ds)
		elif ds['type'] == 'ORACLE':
			con = self.getOracleConn(ds)
		
		cur = con.cursor()
		normalized_query = q.query[1: len(q.query)-1 ] 
		
		if values and q.parnum>0:
			#print 'execute parameter query'
			cur.execute(normalized_query,values)
		else:
			#print 'execute NON parameter query'
			cur.execute(normalized_query)
		#print normalized_query
		#print values
		rows = cur.fetchall()
		names = [description[0] for description in cur.description]
		return rows,names
	
	def validateUser(self, username, pswd):		
		if username in self.users_dict and self.users_dict[username].getPassword()==pswd:
			return self.users_dict[username]
		else:
			return None 
	
	def getChartBoard(self,user):
		result = []
		for chart in self.chartboards:
			toAdd={}
			if  user['username'] == chart['user']:
				toAdd['type']=	chart['type']
				row,cols = self.executeQuery(chart['querydata'])
				#print chart['title'],chart['inverted']
				if chart['inverted']:
					#print 'invert query data...'
					lbl = ();
					dt=();
					for r in row:
						lbl=lbl+(r[0],)
						dt=dt+(r[1],)
					toAdd['labels']=lbl
					toAdd['data']=dt	
				else:
					#print 'NOT INVERT query data...'
					toAdd['labels']=cols
					toAdd['data']=row[0]
				toAdd['title']=chart['title']
				result.append(toAdd)
		#print result
		return result
				
		'''
		chartboards = [];
		chart1 = {'type':'LINE','labels':['Before','After'],'data':[25,60],'title':'Example1' }
		chartboards.append(chart1)
		chart2 = {'type':'LINE','labels':['Before','After'],'data':[40,10],'title':'Example2' }
		chartboards.append(chart2)
		chart3 = {'type':'LINE','labels':['Jen','feb','mar','apr'],'data':[40,10,23,34],'title':'Example3' }
		chartboards.append(chart3)
		return chartboards
		'''
		
		

