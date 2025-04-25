from flask import Flask,render_template,session,flash,redirect,request,send_from_directory,url_for
import pymysql
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import RandomOverSampler
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
import folium
import openpyxl

app=Flask(__name__)
app.config['SECRET_KEY'] = "crime"

#database connection

def data_base():
    db=pymysql.connect(host="localhost",user="root", password="root",database="crime_hotspot", port=3306)
    cur=db.cursor()
    return db,cur

#Index page
@app.route('/')
def index():
    return render_template('index.html')

#
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email']
        pwd=request.form['pwd']
        pno=request.form['pno']
        addr=request.form['addr']
        dob=request.form['dob']
        db,cur=data_base()
        sql="select * from user_registration where Email='%s' "%(email)
        cur.execute(sql)
        data=cur.fetchall()
        db.commit()
        print(data)
        if len(data)==0:
            sql = "insert into user_registration(Name,Email,Password,Phone,Address,DOB) values(%s,%s,%s,%s,%s,%s)"
            val=(name,email,pwd,pno,addr,dob)
            cur.execute(sql,val)
            db.commit()
            flash("User registered Successfully","success")
            return render_template("signin.html")
        else:
            flash("Details already Exists","warning")
            return render_template("signup.html")
        
    return render_template('signup.html')

# login form
@app.route('/signin', methods=['POST','GET'])
def signin():
    if request.method=='POST':
        useremail = request.form['email'] 
        password = request.form['pwd']
        db,cur=data_base()
        sql="select * from user_registration where Email='"+useremail+"' and Password='"+password+"'"
        cur.execute(sql)
        data=cur.fetchall()
        print(data)
        db.commit()
        if len(data)==0:
            flash("Invalid data entered","danger")
            return render_template('signin.html')
        else:

            flash("welcome ","success")
            return render_template('userdash.html',name=data[0][1])
         
    return render_template('signin.html')

@app.route('/viewdata')
def viewdata():

    df = pd.read_excel('dataset/crime_data_extended_entries.xlsx')
    return render_template('viewdata.html',col_name = df.columns,row_val = list(df.values.tolist()))

@app.route('/model_training', methods=['POST','GET'])
def model_training():
    if request.method == "POST":
        global df,x_train, x_test, y_train, y_test
        df = pd.read_excel('dataset/crime_data_extended_entries.xlsx')
        #Delete a unknown column
        df.drop("date",axis=1,inplace=True)
        df.drop("time_of_day",axis=1,inplace=True)
        df.drop("latitude",axis=1,inplace=True)
        df.drop("longitude",axis=1,inplace=True)
        le = LabelEncoder()
        col = df[['crime_type','location','victim_gender','perpetrator_gender','weapon','injury','weather','previous_activity']]
        for i in col:
            df[i]=le.fit_transform(df[i])
        x = df.drop(['crime_type'], axis = 1) 
        y = df['crime_type']
        Oversample = RandomOverSampler(random_state=72)
        x_sm, y_sm = Oversample.fit_resample(x[:25],y[:25])
        x_train, x_test, y_train, y_test = train_test_split(x_sm, y_sm, test_size = 0.3, random_state= 72) 
        model = request.form['algo']
        if model == "1":
            re = RandomForestClassifier(random_state=72,max_depth=9)
            re.fit(x_train,y_train)
            re_pred = re.predict(x_test)
            ac = accuracy_score(y_test,re_pred)
            
            flash('Accuracy of RandomForest : ',"success")
            return render_template('model_training.html',msg= str(ac))
        elif model == "2":
            de = DecisionTreeClassifier(max_depth=50,criterion="entropy",random_state=7,min_samples_split=2)
            de.fit(x_train,y_train)
            de_pred = de.predict(x_test)
            ac1 = accuracy_score(y_test,de_pred)
           
            flash('Accuracy of Decision Tree : ',"success")
            return render_template('model_training.html',msg= str(ac1))
        elif model == "3":
            gd = GradientBoostingClassifier(n_estimators=200,max_depth=5,min_samples_split=3)
            gd.fit(x_train,y_train)
            gd_pred = gd.predict(x_test)
            bc = accuracy_score(y_test,gd_pred)
            flash('Accuracy of GradientBoostingClassifier : ',"success") 
            return render_template('model_training.html',msg= str(bc))
        
    return render_template('model_training.html')


@app.route('/prediction', methods=['POST','GET'])
def prediction():
    if request.method=='POST':
        global df,x_train, x_test, y_train, y_test
      
        a = float(request.form['f1'])
        d = float(request.form['f4'])
        e = float(request.form['f5'])
        f = float(request.form['f6'])
        g = float(request.form['f7'])
        h = float(request.form['f8'])
        i = float(request.form['f9'])
        j = float(request.form['f10'])
        k = float(request.form['f11'])
        l = float(request.form['f12'])
        l = [[a,d,e,f,g,h,i,j,k,l]]
        de = DecisionTreeClassifier()
        de.fit(x_train,y_train)
        pred = de.predict(l)
        if pred == 0:
            msg = 'Robbery'
        elif pred == 1:
            msg = 'Embezzlement'
        elif pred == 2:
            msg = 'Burglary'
        elif pred == 3:
            msg = 'Vandalism'
        elif pred == 4:
            msg = 'Theft'
        elif pred == 5:
            msg = 'Assault'
        elif pred == 6:
            print('Forgery')
        elif pred == 7:
            msg ='Drug Offense'
        else:
            msg = 'Fraud'
        
        if a == 1:
            lat = 12.9255
            lag = 77.5468
            name = "Banashankari"
        if a == 2:
            lat = 12.9304
            lag = 77.6784
            name = "Bellandur"
        if a == 3:
            lat = 12.8452 
            lag = 77.6602
            name = "Electronic City"
        if a == 4:
            lat = 12.9121  
            lag = 77.6446
            name = "HSR layout"
        if a == 5:
            lat = 12.9784
            lag = 77.6408
            name = "Indiranagar"
        if a == 6:
            lat =  12.9308
            lag =  77.5838
            name = "jayanagar"
        if a == 7:
            lat = 12.9063
            lag = 77.5857
            name = "jp nagar"
        if a == 8:
            lat = 12.9855
            lag = 77.5269
            name = "Kamakshipalya"
        if a == 9:
            lat = 12.9352
            lag = 77.6245
            name = "Koramangala"
        if a == 10:
            lat = 12.9569
            lag = 77.7011
            name = "Marathahalli"
        if a == 11:
            lat = 12.9698
            lag = 77.7500
            name = "White Field"
        if a == 12:
            lat = 13.1155
            lag = 77.6070
            name = "White Field"
        
        m = folium.Map(location=[19,-12],zoom_start=2)
        folium.Marker([lat,lag],tooltip='click for more',popup=name).add_to(m)
        m = m._repr_html_()
        print(msg)
        return render_template('result.html',msg=msg, m=m)
    
    return render_template('prediction.html')


if __name__=='__main__':
    app.run(debug=True)
