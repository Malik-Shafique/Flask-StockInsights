from flask import Flask, render_template, request
from forms import ContactForm
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from flask_sqlalchemy import SQLAlchemy

from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.error

#

app = Flask(__name__)
app.secret_key = 'development key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

import pandas as pd
df=pd.read_excel('/home/malik01/mysite/data/Account Jan-Dec 15, 2019.xlsx')
df = df.iloc[6:2764,:6]
df.columns=["Date","Description","Scrip","Debit","Credit","Balance"]


def createList():
     # create scrip list
    #scList=[]
    #num= 0
    #for item in df['Scrip']:
       # if item not in scList:
           # if df['Type'].iat[num] != "?":
                #scList.append(item)
        #num +=1
    #return scList
    scList = df[df['Type']!='?']['Scrip'].unique()
    return scList
@app.route('/', methods=['post', 'get'])
def main():

    form = ContactForm()

    message = ''
    scList = []
    if request.method == 'POST':
        #x = request.form.get('username')  # access the data inside
        password = request.form.get('password')
        scrip = request.form.get('scripname')



        #Populate different columns
        df['Nos']=0
        df['Price']=0.0
        df['Value']=0.0
        df['Type']="?"

        num=0

        for item in df['Description']:
            if "Buy" in item or "Sell" in item:
                s_item = item.split()
                df['Scrip'].iat[num]= s_item[2]
                df['Nos'].iat[num]= s_item[3]
                df['Price'].iat[num]= s_item[5]
                df['Value'].iat[num]= df['Nos'].iat[num] * df['Price'].iat[num]
                df['Type'].iat[num]= s_item[1]
            num +=1
        if len(df['Scrip'])<2700:
            return "<b> Dataframe not Created Successfully </b>"

        if  password == 'pass':


            scList = scrip_summary(scrip)
            message = "OK" #str(result[lgt-2])
            #df = df.to_html()
        else:
            message = "Wrong Passpword"
            return render_template('hello.html', message=message,form=form)
           # message = "Wrong username or password"

    return render_template('hello.html', message = scList,form=form)


    #return render_template('hello.html', message = [df.head().to_html(classes='data')],form=form)  #message = message.to_html()
#


@app.route('/scsumm/<string:scrip>')
def scSumm(scrip="Engro"):

    filDf = df[df['Scrip'] == scrip]
    sns.scatterplot(x= 'Price', y ='Value' , hue='Type', data = filDf)
    figfile = io.BytesIO()
    plt.savefig(figfile, format = 'png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    plt.close()
    scsumm = scrip_summary(scrip)
    return render_template('scsumm.html', message = scsumm, plot_url = figdata_png )


@app.route('/current')
def current():

    scList = createList()
    currDict = {}
    curr = []
    for comp in scList:
        try:
            with urlopen('https://dps.psx.com.pk/company/'+comp) as response:
                      html = response.read()
            bs = BeautifulSoup (html,'html.parser')
            namelist = bs.find('div',{'class':'quote__close'})
            curP = namelist.get_text().strip('Rs.')
                    #print(comp,curP)
            curP = float(curP.replace(',',''))
            curr.append(curP)
            currDict[comp] = curP
        except urllib.error.HTTPError:
            curr.append(0)

    return render_template('current.html',message = currDict)

@app.route('/sclist')
def scList():

    scList = createList()
    return render_template('sclist.html',message = scList)

@app.route('/positions')
def positions():

    nos_tot = pd.Series([], name = "nos_tot")
    #tab = User.query.all()   #for selecting all rows from User
    sum_type = df.groupby(["Type","Scrip"])["Nos"].sum()

    df_pos = pd.read_sql_table("sh_position",db.engine)

    num = 0
    for sym in df_pos['symbol']:
        try:
            tot = int(df_pos[df_pos['symbol']==sym]['nos'])+sum_type['Buy'][sym] - sum_type['Sell'][sym]
            nos_tot[num]=tot

        except KeyError:
            tot = int(df_pos[df_pos['symbol']==sym]['nos'])
            nos_tot[num]=tot
        num+=1
        #pass

        df_pos['nos_curr']=nos_tot

    return render_template('positions.html', df = df_pos)

def scrip_summary(scrip):
    scrip = scrip.upper()
    num=0
    numBTot=0
    valBTot=0

    numSTot=0
    valSTot=0
    scList = []

    for item in df['Scrip']:
        if item == scrip:
            scList.append(df.iloc[num,0:2])
            if df['Type'].iat[num]=="Buy":
                numBTot += df['Nos'].iat[num]
                valBTot += df['Value'].iat[num]
            if df['Type'].iat[num]=="Sell":
                numSTot += df['Nos'].iat[num]
                valSTot += df['Value'].iat[num]
        num +=1
    #comp_total(numBTot,valBTot,numSTot,valSTot)
    #scList = ["pakistan","ok","dear"]
    scList.append("Total Scrips Bought:"+str(numBTot)+"for"+str(valBTot))
    scList.append("Average Buy:"+str(valBTot/numBTot))
    scList.append("Total Scrips Sold:"+str(numSTot)+"for"+str(valSTot))
    if numSTot != 0 :
        scList.append("Average Sell:"+str(valSTot/numSTot))
    return scList
#print("Enter Scrip name: ")
#scrip_summary(scrip)



if __name__ == "__main__":
    app.run()