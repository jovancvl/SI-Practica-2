import sqlite3
import json
import numpy as np
import pandas as pd
import plotly.express as px
from flask import Flask

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
cur.execute("CREATE TABLE IF NOT EXISTS usuarios (name TEXT, telefono INTEGER, contrasena TEXT, provincia TEXT, permisos TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS emails (name TEXT, total INTEGER, phishing INTEGER, cliclados INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS fechas (name TEXT, fecha TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS ips (name TEXT, ip TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS web (nombre TEXT, cookies INTEGER, aviso INTEGER, prot_datos INTEGER, creacion INTEGER)")
con.commit()

def practica1():
    source = json.loads(open("users.json").read())
    users = source['usuarios'] # is list

    for u in users:
        name = list(u.keys())[0] # is string
        values = u[name] # is dict
        if values["telefono"] == "None":
            values["telefono"] = None

        if values["contrasena"] == "None":
            values["contrasena"] = None

        if values["provincia"] == "None":
            values["provincia"] = None

        if values["permisos"] == "None":
            values["permisos"] = None

        cur.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)", (name, values["telefono"], values["contrasena"], values["provincia"], values["permisos"]))
        e = values["emails"]
        cur.execute("INSERT INTO emails VALUES (?, ?, ?, ?)", (name, e["total"], e["phishing"], e["cliclados"]))
        #print(len(values["fechas"]))
        #print(len(values["ips"]))
        for f in values["fechas"]:
            if f != "None":
                cur.execute("INSERT INTO fechas VALUES (?, ?)", (name, f))
        for ip in values["ips"]:
            #print(ip)
            if ip != "N" and ip != "o" and ip != "n" and ip != "e":
                cur.execute("INSERT INTO ips VALUES( ?, ?)", (name, ip))
        con.commit()

    web_source = json.loads(open("legal.json").read())
    webs = web_source["legal"]

    for w in webs:
        name = list(w.keys())[0]
        values = w[name]
        cur.execute("INSERT INTO web VALUES (?, ?, ?, ?, ?)", (name, values["cookies"], values["aviso"], values["proteccion_de_datos"], values["creacion"]))
        con.commit()

    #pr1ej2()
    #pr1ej3()
    #pr1ej4()
    con.close()

def pr1ej2():
    print("EJERCICIO 2\n")

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    cur.execute("SELECT * FROM usuarios")
    users = cur.fetchall() # is list
    df_users = pd.DataFrame(users, columns=["nombre", "telefono", "contrasena", "provincia", "permisos"])
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_emails = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])
    cur.execute("SELECT * FROM fechas")
    fechas = cur.fetchall()
    df_fechas = pd.DataFrame(fechas, columns=["nombre", "fecha"])
    cur.execute("SELECT * FROM ips")
    ips = cur.fetchall()
    df_ips = pd.DataFrame(ips, columns=["nombre", "ip"])

    cur.execute("SELECT * FROM web")
    webs = cur.fetchall()
    df_webs = pd.DataFrame(webs, columns=["nombre", "cookies", "aviso", "proteccion_de_datos", "creacion"])
    print(df_webs)

    print("\ndescribe users\n")
    print(df_users.describe(include='all'))
    print("\ndescribe emails\n")
    print(df_emails.describe(include='all'))
    print("\ndescribe fechas\n")
    print(df_fechas.describe(include='all'))
    print("\ndescribe ips\n")
    print(df_ips.describe(include='all'))

    print("\ndescribe fechas en funcion del nombre\n")
    print(df_fechas.groupby("nombre")["nombre"].count().describe(include='all'))

    print("\ndescribe ips en funcion del nombre\n")
    print(df_ips.groupby("nombre")["nombre"].count().describe(include='all'))

def pr1ej3():
    print("\nEJERCICIO 3\n")

    cur.execute("SELECT * FROM usuarios")
    users = cur.fetchall()  # is list
    df_users = pd.DataFrame(users, columns=["nombre", "telefono", "contrasena", "provincia", "permisos"])
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_emails = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])

    df_users_zero = df_users.loc[df_users["permisos"] == "0"]
    df_users_one = df_users.loc[df_users["permisos"] == "1"]
    df_users_less200 = df_emails.loc[df_emails["total"] < 200]
    df_users_more200 = df_emails.loc[df_emails["total"] >= 200]

    df_users_zeroless200 = pd.merge(df_users_zero, df_users_less200, how="inner", on="nombre")
    df_users_zeromore200 = pd.merge(df_users_zero, df_users_more200, how="inner", on="nombre")
    df_users_oneless200 = pd.merge(df_users_one, df_users_less200, how="inner", on="nombre")
    df_users_onemore200 = pd.merge(df_users_one, df_users_more200, how="inner", on="nombre")

    print("\n0 | <200 mean: " + str(df_users_zeroless200["phishing"].mean()))
    print("\n0 | <200 median: " + str(df_users_zeroless200["phishing"].median()))
    print("\n0 | <200 variance: " + str(df_users_zeroless200["phishing"].var()))
    print("\n0 | <200 describe:")
    print(df_users_zeroless200["phishing"].describe())

    print("\n0 | >200 mean: " + str(df_users_zeromore200["phishing"].mean()))
    print("\n0 | >200 median: " + str(df_users_zeromore200["phishing"].median()))
    print("\n0 | >200 variance: " + str(df_users_zeromore200["phishing"].var()))
    print("\n0 | >200 describe:")
    print(df_users_zeromore200["phishing"].describe())

    print("\n1 | <200 mean: " + str(df_users_oneless200["phishing"].mean()))
    print("\n1 | <200 median: " + str(df_users_oneless200["phishing"].median()))
    print("\n1 | <200 variance: " + str(df_users_oneless200["phishing"].var()))
    print("\n1 | <200 describe:")
    print(df_users_oneless200["phishing"].describe())

    print("\n1 | >200 mean: " + str(df_users_onemore200["phishing"].mean()))
    print("\n1 | >200 median: " + str(df_users_onemore200["phishing"].median()))
    print("\n1 | >200 variance: " + str(df_users_onemore200["phishing"].var()))
    print("\n1 | >200 describe:")
    print(df_users_onemore200["phishing"].describe())

def pr1ej4():
    print("\nEJERCICIO 4\n")

    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    df_emails = pd.DataFrame(emails, columns=["nombre", "total", "phishing", "cliclados"])
    cur.execute("SELECT * FROM web")
    webs = cur.fetchall()
    df_webs = pd.DataFrame(webs, columns=["nombre", "cookies", "aviso", "proteccion_de_datos", "creacion"])

    df_users_critical = df_emails.copy()
    lista = []
    for t, c in zip(df_users_critical["total"], df_users_critical["cliclados"]):
        lista.append(c/t)
    df_users_critical["clickrate"] = lista
    df_users_critical.sort_values(by=["clickrate"], inplace=True, ascending=False)
    grafico = px.bar(df_users_critical.head(10), x="nombre", y="clickrate")
    #grafico.show()
    #print(df_users_critical.head(10))

    df_webs_critical = df_webs.copy()
    points = []
    for c, a, p in zip(df_webs_critical["cookies"], df_webs_critical["aviso"], df_webs_critical["proteccion_de_datos"]) :
        temp = c + a + p
        points.append(temp)
    df_webs_critical["puntos"] = points
    df_webs_critical.sort_values(by=["puntos"], inplace=True, ascending=True)
    grafico = px.bar(df_webs_critical.head(5), x="nombre", y=["cookies", "aviso", "proteccion_de_datos"])
    #grafico.show()


    df_webs_cumplen = df_webs_critical.loc[df_webs_critical["puntos"] == 3]
    df_webs_nocumplen = df_webs_critical.loc[df_webs_critical["puntos"] != 3]
    df_webs_cumplen = df_webs_cumplen["creacion"].value_counts()
    df_webs_nocumplen = df_webs_nocumplen["creacion"].value_counts()
    grafico = px.bar(df_webs_cumplen, title="paginas que cumplen los criterios")
    #grafico.show()
    grafico = px.bar(df_webs_nocumplen, title="paginas que no cumplen los criterios")
    #grafico.show()


    #input("press key to end run")

    con.close()

@app.route('/')
def hello_world():
   return '<p>Hello, World!</p>'


if __name__ == '__main__':
    practica1()
    app.run(debug=True)

