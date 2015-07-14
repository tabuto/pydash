from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack,jsonify
from pydash import PyDash

DEBUG = True
SECRET_KEY = 'jfsjrgyugfuybv3848483854hhjfdhjfdsjh'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#app.run(host= '10.5.62.79')

pyDash = PyDash('dash_config.xml')

@app.before_request
def before_request():
	pass
	#if 'logged_in' not in session:
	#	print "not logged in: redirecto to login"
	#	#return redirect(url_for('login'))
	#	return render_template('login.html', error=None)

'''
show the main dashboard
'''
@app.route("/charts",methods=['GET', 'POST'])
def show_charts():
	#print "call show_charts"
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	global pyDash
	return render_template('show_charts.html')

'''
show the main dashboard
'''
@app.route("/",methods=['GET', 'POST'])
def show_dashboard():
	#print "call show_dashboard"
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	global pyDash
	queries = pyDash.getQueries()
	return render_template('show_dashboard.html', queries=queries)
@app.route("/exec_chart",methods=['GET', 'POST'])
def exec_chart():
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	loggedUser = session['logged_in']
	global pyDash
	charts = pyDash.getChartBoard(loggedUser)
	result = {}
	#result['labels']=["January","February","March","April","May","June"]
	#result['data'] = [203,256,299,351,405,547]
	result['charts']=charts
	return jsonify(result)


@app.route("/exec",methods=['GET', 'POST'])
def exec_query():
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	loggedUser = session['logged_in']
	
	#print "call exec_query"
	query = request.form['query_sel']
	#print "query to execute: ",query
	global pyDash 
	user = pyDash.validateUser(loggedUser['username'],loggedUser['password'])
	toExecute = pyDash.getQueryByName(query)
	parnum = toExecute.parnum
	values=None
	if parnum>0:
		values=()
		for p in toExecute.parmap:
			toAdd=request.form[p.name]
			values=values+(toAdd,)
		#print 'par vals: ',filter(None,values)
	entries,colNames = pyDash.executeQuery(query,values,user)
	
	queries = pyDash.getQueries()
	colNum= toExecute.selectNumber;
	#print "Col to show: ",colNum
	return render_template('show_dashboard.html', entries=entries,queries=queries, colNum=range(colNum), colNames=colNames, params=toExecute.parmap)
	    

'''
show login page
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
	global pyDash
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		loggedUser = pyDash.validateUser(username,password)
		if not loggedUser:
			error = 'Invalid login'
		else:
			print "Valid login: ",username
			session['logged_in'] = loggedUser.serialize()
			#flash('You were logged in')
			#print "redirect to show_dashboard"
			return redirect(url_for('show_dashboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_dashboard'))

if __name__ == "__main__":
    app.run()
