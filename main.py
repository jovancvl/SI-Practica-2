import sqlite3
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.utils
from flask import Flask
from flask import render_template
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import statsmodels
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)
pd.options.plotting.backend = "plotly"
pd.set_option("display.max_rows", None, "display.max_columns", None)

def setup():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('drop table if exists usuarios')
    cur.execute('drop table if exists emails')
    cur.execute('drop table if exists fechas')
    cur.execute('drop table if exists ips')
    cur.execute('drop table if exists web')
    con.commit()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS usuarios (name TEXT, telefono INTEGER, contrasena TEXT, provincia TEXT, permisos TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS emails (name TEXT, total INTEGER, phishing INTEGER, cliclados INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS fechas (name TEXT, fecha TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ips (name TEXT, ip TEXT)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS web (nombre TEXT, cookies INTEGER, aviso INTEGER, prot_datos INTEGER, creacion INTEGER)")
    con.commit()
    source = json.loads(open("users.json").read())
    users = source['usuarios']  # is list

    for u in users:
        name = list(u.keys())[0]  # is string
        values = u[name]  # is dict
        if values["telefono"] == "None":
            values["telefono"] = None

        if values["contrasena"] == "None":
            values["contrasena"] = None

        if values["provincia"] == "None":
            values["provincia"] = None

        if values["permisos"] == "None":
            values["permisos"] = None

        cur.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)",
                    (name, values["telefono"], values["contrasena"], values["provincia"], values["permisos"]))
        e = values["emails"]
        cur.execute("INSERT INTO emails VALUES (?, ?, ?, ?)", (name, e["total"], e["phishing"], e["cliclados"]))
        # print(len(values["fechas"]))
        # print(len(values["ips"]))
        for f in values["fechas"]:
            if f != "None":
                cur.execute("INSERT INTO fechas VALUES (?, ?)", (name, f))
        for ip in values["ips"]:
            # print(ip)
            if ip != "N" and ip != "o" and ip != "n" and ip != "e":
                cur.execute("INSERT INTO ips VALUES( ?, ?)", (name, ip))
        con.commit()

    web_source = json.loads(open("legal.json").read())
    webs = web_source["legal"]

    for w in webs:
        name = list(w.keys())[0]
        values = w[name]
        cur.execute("INSERT INTO web VALUES (?, ?, ?, ?, ?)",
                    (name, values["cookies"], values["aviso"], values["proteccion_de_datos"], values["creacion"]))
        con.commit()

    con.close()

@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'


@app.route('/usuarios_criticos/<x>')
def usuarios_criticos(x):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_users_critical = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])
    #print(df_users_critical)
    lista = []
    for t, c in zip(df_users_critical["total"], df_users_critical["cliclados"]):
        lista.append(c / t)
    df_users_critical["clickrate"] = lista
    df_users_critical.sort_values(by=["clickrate"], inplace=True, ascending=False)
    grafico = px.bar(df_users_critical.head(int(x)), x="nombre", y="clickrate")
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    con.close()
    return render_template('graph.html', graphJSON=graphJSON)

@app.route("/paginas_criticas/<x>")
def paginas_criticas(x):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM web")
    df_webs_critical = pd.DataFrame(cur.fetchall(), columns=["nombre", "cookies", "aviso", "proteccion_de_datos", "creacion"])
    points = []
    for c, a, p in zip(df_webs_critical["cookies"], df_webs_critical["aviso"], df_webs_critical["proteccion_de_datos"]):
        temp = c + a + p
        points.append(temp)
    df_webs_critical["puntos"] = points
    df_webs_critical.sort_values(by=["puntos"], inplace=True, ascending=True)
    grafico = px.bar(df_webs_critical.head(int(x)), x="nombre", y=["cookies", "aviso", "proteccion_de_datos"])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    con.close()
    return render_template('graph.html', graphJSON=graphJSON)

@app.route('/usuarios_criticos/masde50/<x>')
def usuarios_criticos_masde50(x):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_users_critical = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])
    #print(df_users_critical)
    lista = []
    for t, c in zip(df_users_critical["total"], df_users_critical["cliclados"]):
        lista.append(c / t)
    df_users_critical["clickrate"] = lista
    df_users_critical = df_users_critical[df_users_critical["clickrate"] > 0.5]
    df_users_critical.sort_values(by=["clickrate"], inplace=True, ascending=False)
    grafico = px.bar(df_users_critical.head(int(x)), x="nombre", y="clickrate")
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    con.close()
    return render_template('graph.html', graphJSON=graphJSON)

@app.route('/usuarios_criticos/menosde50/<x>')
def usuarios_criticos_menosde50(x):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_users_critical = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])
    #print(df_users_critical)
    lista = []
    for t, c in zip(df_users_critical["total"], df_users_critical["cliclados"]):
        lista.append(c / t)
    df_users_critical["clickrate"] = lista
    df_users_critical = df_users_critical[df_users_critical["clickrate"] < 0.5]
    df_users_critical.sort_values(by=["clickrate"], inplace=True, ascending=False)
    grafico = px.bar(df_users_critical.head(int(x)), x="nombre", y="clickrate")
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    con.close()
    return render_template('graph.html', graphJSON=graphJSON)

@app.route("/vulnerabilidades")
def vulnerabilidades():
    response = requests.get("https://cve.circl.lu/api/last")
    response = response.json()
    df_vulnerabilidades = pd.DataFrame(response)
    df_vulnerabilidades = df_vulnerabilidades.drop("capec", 1)
    df_vulnerabilidades = df_vulnerabilidades.head(10)
    #print(df_vulnerabilidades.columns)
    return render_template('table.html', tables=[df_vulnerabilidades.to_html(classes="data")], titles=df_vulnerabilidades.columns.values)

@app.route("/githubperfil/<username>")
def githubperfil(username):
    response = requests.get(f"https://api.github.com/users/{username}")
    response = response.json()
    return render_template('githubperfil.html', user=response)

@app.route("/regresionlineal")
def regresionlineal():
    source = json.loads(open("users_IA_clases.json").read())
    users_train = pd.DataFrame(source['usuarios'])
    users_train = users_train.drop("usuario", 1)
    users_train_x = users_train.drop("vulnerable", 1)
    users_train_y = users_train.drop(["emails_phishing_recibidos", "emails_phishing_clicados"], 1)
    #users_train = users_train.values
    #print(users_train_x)
    #print(users_train_y)
    source = json.loads(open("users_IA_predecir.json").read())
    users_test = pd.DataFrame(source['usuarios'])
    users_test = users_test.drop("usuario", 1)
    #users_test = users_test.values

    x_train, x_test, y_train, y_test = train_test_split(users_train_x, users_train_y, test_size=0.25)
    print(x_train)
    print(x_test)
    print(y_train)
    print(y_test)
    regr = MultinomialNB()
    regr.fit(x_train, y_train)
    #print(regr.coef_)
    pred = regr.predict(x_test)
    xy_test = x_test.copy()
    xy_test["vulnerable"] = pred.astype(str)
    #print(pred)

    # scatter plot for train
    #users_train["vulnerable"] = users_train["vulnerable"].astype(str)
    #grafico = px.scatter(xy_test, x="emails_phishing_recibidos", y="emails_phishing_clicados", color="vulnerable")

    # scatter plot for predecir
    pred = regr.predict(users_test)
    users_test["vulnerable"] = pred.astype(str)
    grafico = px.scatter(users_test, x="emails_phishing_recibidos", y="emails_phishing_clicados", color="vulnerable")

    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    return render_template("graph.html", graphJSON=graphJSON)

if __name__ == '__main__':
    setup()
    app.run(debug=True)
