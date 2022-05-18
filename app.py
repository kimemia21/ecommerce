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


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    cursor = None
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code  and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM product WHERE code=%s and category=%s", _code)
            row = cursor.fetchone()

            itemArray = {
                row['code']: {'name': row['name'], 'code': row['code'], 'quantity': _quantity, 'price': row['price'],
                              'image': row['image'], 'total_price': _quantity * row['price']}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row['code'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['code'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * row['price']
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * row['price']

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
            output = redirect(url_for('.products'))


        else:
            return 'Error while adding item to cart'
    finally:
        return output
        cursor.close()
        conn.close()





@app.route('/')
def products():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM product")
        rows = cursor.fetchall()


    except Exception as e:
        print(e)
    finally:
        output = render_template('products.html', products=rows)
        return output



@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


def array_merge( first_array , second_array ):
 if isinstance( first_array , list ) and isinstance( second_array , list ):
  return first_array + second_array
 elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
  return dict( list( first_array.items() ) + list( second_array.items() ) )
 elif isinstance( first_array , set ) and isinstance( second_array , set ):
  return first_array.union( second_array )
 return False



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