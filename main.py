import sqlite3
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.utils
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
pd.options.plotting.backend = "plotly"

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
    print(df_users_critical)
    lista = []
    for t, c in zip(df_users_critical["total"], df_users_critical["cliclados"]):
        lista.append(c / t)
    df_users_critical["clickrate"] = lista
    df_users_critical.sort_values(by=["clickrate"], inplace=True, ascending=False)
    grafico = px.bar(df_users_critical.head(int(x)), x="nombre", y="clickrate")
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(grafico, cls=a)
    con.close()
    return render_template('hello.html', graphJSON=graphJSON)

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
    return render_template('hello.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(debug=True)
