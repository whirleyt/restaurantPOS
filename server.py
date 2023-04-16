
"""
Columbia's COMS W4111.001 Introduction to Databases RestaurantPOS
"""
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, session

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "tjw2154"
DATABASE_PASSWRD = "6104"
DATABASE_HOST = "34.28.53.86"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"
app.secret_key = '6104'

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if 'loggedin' in session and session['loggedin']== True:
        return redirect(url_for('index'))
    if request.method == "POST":
      username=request.form['username']
      password=request.form['password']
      arr= username.split(" ")
      first= arr[0]
      last= arr[1]
      select_employee_query = "SELECT e.firstName, e.lastName, e.employeeID FROM Employee e WHERE e.firstName='"+first+"' and e.lastName='"+last+"';"
      cursor = g.conn.execute(text(select_employee_query))
      user = []
      for result in cursor:
        user.append(result)
      cursor.close()
      g.conn.commit()
      if(user[0][2] != int(password)):
        error = dict(error=True)
        session['loggedin']= False
        return render_template("user_login.html", **error)
      else:
        session['loggedin']= True
        session['employeeID'] = user[0][2]
        session['firstName'] = user[0][0]
        session['lastName'] = user[0][1]
        return redirect(url_for('index'))
    error = dict(error=False)
    return render_template("user_login.html", **error)

@app.route('/logout/')
def logout():
   session.pop('loggedin', None)
   session.pop('employeeID', None)
   session.pop('firstName', None)
   session.pop('lastName', None)
   return redirect(url_for('login'))

@app.route('/')
def default():
    return redirect(url_for('login'))

@app.route('/tables/', methods=['POST', 'GET'])
def index():
    # print(request.args)
    if 'loggedin' in session and session['loggedin']== True:
        select_query = "SELECT t.tableID, t.section_ID, t.guestCount FROM Tables t;"
        cursor = g.conn.execute(text(select_query))
        tables = []
        for result in cursor:
            tables.append(result)
        cursor.close()
        context = dict(data=tables)
        return render_template("index.html", **context)
    else:
        return redirect(url_for('login'))

@app.route('/order/<id>/list/')
def order(id):
    if 'loggedin' in session and session['loggedin']== True:
        select_order_query = "SELECT mi.name, mi.price, oi.table_ID, oi.orderID FROM MenuItem mi JOIN OrderItems oi ON oi.menu_item_ID=mi.menuItemID AND oi.table_ID="+id+";"
        cursor1 = g.conn.execute(text(select_order_query))
        order = []
        for result in cursor1:
            order.append(result)
        cursor1.close()
        select_total_query = "SELECT SUM(mi.price) AS OrderTotal FROM MenuItem mi JOIN OrderItems oi ON oi.menu_item_ID=mi.menuItemID AND oi.table_ID="+id+";"
        cursor2 = g.conn.execute(text(select_total_query))
        order_total= [];
        for result in cursor2:
            order_total.append(result)
        cursor2.close()
        url=[]
        url.append(id)
        order_context = dict(data=order)
        
        total_context = dict(total=order_total)
        url_id= dict(urlid=url)
        return render_template("order.html", **order_context, **total_context, **url_id)
    else:
        return redirect(url_for('login'))

@app.route('/order/<id>/<menuItemTypeId>/list/')
def menuItems(id, menuItemTypeId):
    if 'loggedin' in session and session['loggedin']== True:
        select_menu_item_query = "SELECT mi.name, mi.menuItemID, mi.description FROM MenuItem mi WHERE mi.type_ID="+menuItemTypeId+";"
        cursor1 = g.conn.execute(text(select_menu_item_query))
        menuItems = []
        for result in cursor1:
            menuItems.append(result)
        cursor1.close()
        menu_item_context = dict(menuItem=menuItems)
        select_order_query = "SELECT mi.name, mi.price, oi.table_ID, oi.orderID FROM MenuItem mi JOIN OrderItems oi ON oi.menu_item_ID=mi.menuItemID AND oi.table_ID="+id+";"
        cursor2 = g.conn.execute(text(select_order_query))
        order = []
        for result in cursor2:
            order.append(result)
        cursor2.close()
        select_total_query = "SELECT SUM(mi.price) AS OrderTotal FROM MenuItem mi JOIN OrderItems oi ON oi.menu_item_ID=mi.menuItemID AND oi.table_ID="+id+";"
        cursor3 = g.conn.execute(text(select_total_query))
        order_total= [];
        for result in cursor3:
            order_total.append(result)
        url=[]
        url.append(id)
        url_id= dict(urlid=url);
        cursor3.close()
        order_context = dict(data=order)
        total_context = dict(total=order_total)
        return render_template("order.html", **menu_item_context, **order_context, **total_context, **url_id)
    else:
        return redirect(url_for('login'))

@app.route('/order/<id>/add/', methods=['POST'])
def add(id):
    table_ID=request.form['table_ID']
    menu_item_ID=request.form['menu_item_ID']
    params = {}
    params["table_ID"]= table_ID
    params["menu_item_ID"]= menu_item_ID
    params["name"]= 'Tara'
    g.conn.execute(text('INSERT INTO OrderItems (menu_item_ID, table_ID, createdBy) VALUES (:menu_item_ID, :table_ID, :name)'), params)
    g.conn.commit()
    return redirect(url_for('order', id=table_ID))

@app.route('/order/delete/', methods=['POST'])
def delete():
    table_ID=request.form['table_ID']
    orderID=request.form['orderID']
    params = {}
    params["table_ID"]= table_ID
    params["orderID"]= orderID
    g.conn.execute(text('DELETE FROM OrderItems WHERE orderID=:orderID'), params)
    g.conn.commit()
    print(table_ID)
    return redirect(url_for('order', id=table_ID))

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
run()

