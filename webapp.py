from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from pydash import PyDash

DEBUG = True
SECRET_KEY = 'jfsjrgyugfuybv3848483854hhjfdhjfdsjh'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

pyDash = PyDash('dash_config.xml')

@app.before_request
def before_request():
	pass

'''
show the main dashboard
'''
@app.route("/",methods=['GET', 'POST'])
def show_dashboard():
	print "call show_dashboard"
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	global pyDash
	queries = pyDash.getQueriesName()
	return render_template('show_dashboard.html', queries=queries)

@app.route("/exec",methods=['GET', 'POST'])
def exec_query():
	if 'logged_in' not in session:
		print "not logged in: redirecto to login"
		return redirect(url_for('login'))
	loggedUser = session['logged_in']
	
	print "call exec_query"
	query = request.form['query_sel']
	print "query to execute: ",query
	global pyDash
	user = pyDash.validateUser(loggedUser['username'],loggedUser['password'])
	toExecute = pyDash.getQueryByName(query)
	entries,colNames = pyDash.executeQuery(query,user)
	queries = pyDash.getQueriesName()
	colNum= toExecute.selectNumber;
	print "Col to show: ",colNum
	return render_template('show_dashboard.html', entries=entries,queries=queries, colNum=range(colNum), colNames=colNames)
	    

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
			print "redirect to show_dashboard"
			return redirect(url_for('show_dashboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_dashboard'))

if __name__ == "__main__":
    app.run()
