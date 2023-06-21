from Inventory import views as inventoryUrl
from Products import views as productsUrl

from flask import Flask, render_template, request, session, redirect, url_for
import random
import smtplib
import datetime

DEVELOPMENT_ENV = True

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET', 'POST'])
def Home():
    if 'user' not in session:
        print(session)
        return redirect(url_for('login'))
    return render_template('home.html')



app.add_url_rule('/inventory', view_func = inventoryUrl.InventoryHome, methods=['GET', 'POST'])
app.add_url_rule('/inventory/DailyOrderReport', view_func = inventoryUrl.DailyOrderReport, methods=['GET', 'POST'])
app.add_url_rule('/inventory/ReadLatestInventory', view_func = inventoryUrl.ReadLatestInventory, methods=['GET', 'POST'])
app.add_url_rule('/inventory/InventoryChangeTab', view_func = inventoryUrl.InventoryChangeTab, methods=['GET', 'POST'])
app.add_url_rule('/inventory/UpdateInventory', view_func = inventoryUrl.UpdateInventory, methods=['GET', 'POST'])
app.add_url_rule('/inventory/AddInventoryM', view_func = inventoryUrl.AddInventoryM, methods=['GET', 'POST'])
app.add_url_rule('/inventory/InvtUpdateApprove', view_func = inventoryUrl.InvtUpdateApprove, methods=['GET', 'POST'])
app.add_url_rule('/inventory/DownloadDatabase', view_func = inventoryUrl.DownloadDatabase, methods=['POST'])
app.add_url_rule('/inventory/Downloadlogs', view_func = inventoryUrl.Downloadlogs, methods=['POST'])


app.add_url_rule('/product', view_func = productsUrl.ProductHome, methods=['GET', 'POST'])
app.add_url_rule('/productdb', view_func = productsUrl.ProductDB, methods=['GET', 'POST'])
app.add_url_rule('/productSearch', view_func = productsUrl.ProductSearch, methods=['GET', 'POST'])
app.add_url_rule('/product/<product_id>', view_func = productsUrl.ProductPage, methods=['GET', 'POST'])
app.add_url_rule('/product/Generate_productdb_OR_Polar', view_func = productsUrl.Generate_productdb_OR_Polar, methods=['GET', 'POST'])


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('Home'))
    
    if request.method == 'POST':
        if 'send_otp' in request.form:
            otp = generate_otp()
            msg_status, msg = send_otp_email(otp)
            if msg_status == 'ok':
                session['sent_otp'] = True
                session['otp'] = otp
                return render_template('login.html', message=msg, msg_status=msg_status)
            else:
                return render_template('login.html', message=msg, msg_status=msg_status)

        elif 'verify_otp' in request.form:
            if 'otp' in session:
                otp = request.form['otp']
                if otp == session['otp']:
                    session['user'] = True
                  #   session.permanent = True
                    app.permanent_session_lifetime = datetime.timedelta(minutes=120)
                    session.modified = True
                    session.pop('otp', None)
                    session.pop('sent_otp', None)
                    return redirect(url_for('Home'))
                else:
                    return render_template('login.html', message='Wrong OTP')
            else:
                return render_template('login.html', message='OTP verification failed.')
    
    return render_template('login.html')

def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp_email(otp):
   # =============================================================================
   # SET EMAIL LOGIN REQUIREMENTS
   # =============================================================================
   gmail_user = 'leatherworldauth@gmail.com'
   gmail_app_password = 'bvdapbhsduvqcgoj'

   # =============================================================================
   # SET THE INFO ABOUT THE SAID EMAIL
   # =============================================================================
   sent_from = gmail_user
   sent_to = ['leatherworld4@gmail.com']
   sent_subject = 'OTP for Ecommerce Management Site'
   sent_body = f"{otp} - OTP for Ecommerce Management"

   email_text = """\
   From: %s
   To: %s
   Subject: %s

   %s
   """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

   # =============================================================================
   # SEND EMAIL OR DIE TRYING!!!
   # Details: http://www.samlogic.net/articles/smtp-commands-reference.htm
   # =============================================================================

   try:
      server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
      server.ehlo()
      server.login(gmail_user, gmail_app_password)
      server.sendmail(sent_from, sent_to, email_text)
      server.close()

      return 'ok','OTP has been sent to registered email id'
   except Exception as exception:
      print("Error: %s!\n\n" % exception)
      return 'error','Error occuered while sending OTP'


if __name__ == "__main__":

   # try:
   app.run(debug=DEVELOPMENT_ENV, host='0.0.0.0')
   
   # except:
   # app.run(debug=DEVELOPMENT_ENV)