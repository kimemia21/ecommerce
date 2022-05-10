from flask import *
from flaskext.mysql import MySQL
import pymysql
from werkzeug.utils import secure_filename
import os


app= Flask(__name__)
app.secret_key="arandomstringofCharacters"
mysql= MySQL()
UPLOAD_PATH="static/uploads/cart"
ALLOWED_EXTENSIONS ={'jpg','jpeg','png'}
app.config['UPLOAD_FOLDER']=UPLOAD_PATH #this config was to be used to make sure that the image name is correct in the db

#mysql configarations
app.config['MYSQL_DATABASE_USER']="root"
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='testingdb'
app.config['MYSQL_DATABASE_HOST']='localhost'
mysql.init_app(app)

@app.route('/')
def products():
    try:
        conn=mysql.connect()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute( 'Select * from product' )
        rows=cursor.fetchall()
        output=render_template('products.html',products=rows)
    except Exception as e:
        print(e)
    finally:
        rows = cursor.fetchall()
        return output
        cursor.close()
        conn.close()



@app.route('/fillDb',methods=['POST','GET'])
def fillDb():
    if request.method =='POST':
        code=request.form['code']
        name=str(request.form['name'])
        image=request.files['image']
        imageFileName=secure_filename(image.filename)
        category=str(request.form['category'])
        price=request.form['price']
        discount=request.form['discount']
        if code ==''or name =='' or image ==''or category =='' or price =='' or discount =='':
            msg='make sure that all fields are all entered'
            return render_template("addImage.html",message=msg)
        else:
            conne=mydb()
            cur=conne.cursor()
            sql='insert into product (code,name,image,category,price,discount) values(%s,%s,%s,%s,%s,%s)'
            cur.execute(sql,(code,name,imageFileName,category,price,discount))
            conne.commit()
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],imageFileName))

            if cur.rowcount == +1:
                return render_template('addImage.html',msg='added succesfully')
            else:
                return render_template('addImage.html',msg='something went wrong')
    else:
        return render_template('addImage.html',msg='wrong request method')



def mydb():
    return pymysql.connect(user='root',password='',host='localhost',database='testingdb')




if __name__ =='__main__':
    app.run(debug=True)