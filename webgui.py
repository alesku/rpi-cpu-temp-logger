#!/usr/bin/env python
#-*-coding: utf-8-*-

import sqlite3
import sys
import cgi
import cgitb

dbname = '/var/www/cpuTemp_Database.db'

# Print the HTTP header
def printHTTPheader():
	print "Content-type: text/html; charset=utf-8\n\n"
	
# Print the HTML had section. Arguments are the page title and 
# the table for the chart
def printHTMLHead(title, table):
	print "<head>"
	print "    <title>"
	print title
	print "    </title>"
	
	print_gpath_script(table)
	
	print "</head>"
	
# Get data from the Database. If an interval is passed, return a list of
# records from the Database
def get_data(interval):
	myConnection = sqlite3.connect(dbname)
	myCursor = myConnection.cursor()
	
	if interval == None:
		myCursor.execute('SELECT * FROM temps')
	else:
		myCursor.execute('SELECT timestamp, temp FROM temps WHERE timestamp > datetime("now", "-{0} hours")'.format(interval))
	
	rows = myCursor.fetchall()
	myConnection.close()
	
	return rows
	
# Convert rows from Database intoa JavaScript Table
def create_table(rows):
	chart_table=""
	
	for row in rows[:-1]:
		rowstr = "[new Date('{0}'), {1}],\n".format(row[0], str(row[1]))
		chart_table += rowstr
	
	row = rows[-1]
	rowstr = "[new Date('{0}'), {1}]\n".format(row[0], str(row[1]))
	chart_table += rowstr
	
	return chart_table
	
# Print the JavaScript to generate the Chart. Pass the table generated
# from the Database
def print_graph_script(table):
	chart_code = ""
	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
	<script type="text/javascript">
		google.charts.load('current', {'packages': ['corechart'], 'language': 'de'});
		google.charts.setOnLoadCallback(drawChart);
		
		function drawChart(){
			var data = new google.visualization.DataTable();
			data.addColumn('datetime', 'Date');
			data.addColumn('number', 'CPU Temperature');
			data.addRows([%s]);
			
			var options ={
				titlePosition: 'in',
				legend: 'top',
				colors: ['blue'],
				chartArea: {right: 5, left: 50, bottom: 50, top: 20},
				vAxis: {
					title: "Temperature in °C"
				},
				hAxis: {
					title: "Date"
				}
			};
			
			var chart = new google.visualiation.LineChart(document.getElementById('chart_div'));
			chart.draw(data, options);
		};
	</script>
	print chart_code % (table)
	
# Print the div that contains the graph
def show_graph():
	print '<div id="chart_div" style="width: 100%"; height: 500px;"></div>'
	
# Connect to the db and show some stats. Argument option is the number of hours 
def show_stats(option): 
 
	conn=sqlite3.connect(dbname) 
	curs=conn.cursor() 
 
	print "<hr>" 
    
	if option is None: 
		option = str(24) 

	curs.execute("SELECT timestamp,max(temp) FROM temps WHERE timestamp>datetime('now','-{0} hour')".format(option))
	rowmax=curs.fetchone() 
	rowstrmax="<font color='red'>{0}</font>°C, &nbsp&nbsp{1}".format(str(rowmax[1]),str(rowmax[0])) 
	print "Maximum temperature: "
	print rowstrmax 
	print "<p>"

	curs.execute("SELECT avg(temp) FROM temps WHERE timestamp>datetime('now','-{0} hour')".format(option))
	rowavg=curs.fetchone() 
	print "Average temperature:&nbsp&nbsp&nbsp" 
	print "<b>%.2f</b>" % rowavg+"°C for last {0} hours." .format(option)
	print "<p>"
        
	curs.execute("SELECT timestamp,min(temp) FROM temps WHERE timestamp>datetime('now','-{0} hour')".format(option))
	rowmin=curs.fetchone() 
	rowstrmin="<font color='blue'>{0}</font>°C, &nbsp&nbsp&nbsp{1}".format(str(rowmin[1]),str(rowmin[0])) 
	print "Minumum temperature: "
	print rowstrmin
   
	conn.close()
    
def print_time_selector(option):
 
	print """<form action="/cgi-bin/webgui.py" method="POST"> 
		Show the temperature logs for   
		<select name="timeinterval">""" 

	if option is not None: 

		if option == "6": 
			print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>" 
		else: 
			print "<option value=\"6\">the last 6 hours</option>" 

 
		if option == "12": 
			print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>" 
		else: 
			print "<option value=\"12\">the last 12 hours</option>" 
            
		if option == "24": 
			print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>" 
		else: 
			print "<option value=\"24\">the last 24 hours</option>" 
        
		if option == "168": 
			print "<option value=\"168\" selected=\"selected\">the last week</option>" 
		else: 
			print "<option value=\"168\">the last week</option>" 
            
		if option == "720":
			print "<option value=\"720\" selected=\"selected\">the last month</option>" 
		else: 
			print "<option value=\"720\">the last month</option>" 
            
		if option == "8544":
			print "<option value=\"8544\" selected=\"selected\">the last year</option>" 
		else: 
			print "<option value=\"8544\">the last year</option>" 
 
	else: 
		print """<option value="6">                     the last 6 hours</option>
				<option value="12">                    the last 12 hours</option>
				<option value="24" selected="selected">the last 24 hours</option>
				<option value="168">                   the last week</option>
				<option value="720">                   the last month</option>
				<option value="8544">                  the last year</option>
		"""
 
	print """ </select> 
		<input type="submit" value="Display"> 
	</form>""" 
    
# Check that the option is valid and not an SQL injection 
def validate_input(option_str): 
    
	# check that the option string represents a number 
	if option_str.isalnum(): 
        
		# check that the option is within a specific range 
		if int(option_str) > 0 and int(option_str) <= 8544:
			return option_str 
		else: 
			return None 
	else:  
		return None 
        
#return the option passed to the script 
def get_option(): 
	form=cgi.FieldStorage() 
	if "timeinterval" in form: 
		option = form["timeinterval"].value 
		return validate_input (option) 
	else: 
		return None 

# Main function: this is where the program starts  
def main(): 

	# get options that may have been passed to this script 
	option=get_option() 

	if option is None: 
		option = str(24) 
 
	# get data from the database 
	records=get_data(option) 
 
	# print the HTTP header 
	printHTTPheader() 
 
	if len(records) != 0: 
		# convert the data into a table 
		table=create_table(records) 
	else: 
		print "No data found" 
		return 
 
	# Start printing the page 
	print "<html>" 
	# Print the head section including the table used by the javascript for the chart.
	printHTMLHead("Raspberry Pi Temperature Logger", table) 

	# print the page body 
	print "<body>" 
	print "<h2>Raspberry Pi Temperature Logger</h2>"
	print "<hr>" 
	print_time_selector(option) 
	show_graph() 
	show_stats(option) 
	print "</body>" 
	print "</html>" 

	sys.stdout.flush() 

if __name__=="__main__": 
	main()
