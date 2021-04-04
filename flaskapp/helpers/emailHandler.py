import smtplib

def sendMail(message, address):
    app_email = "Deliverytoday1220@gmail.com"
    app_password = "Deliverytoday12/20$"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(app_email, app_password)
    server.sendmail(app_email, address, message)
    print("Message sent")
