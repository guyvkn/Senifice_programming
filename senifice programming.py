import sys
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QLineEdit,QLabel,QCalendarWidget,QMessageBox
from dateutil.parser import parse as parse_date
from sklearn import linear_model
from yahoo_finance import Share

'''In Yahoo-finance api the user can get results from 70's,
In our software the defult start date is the MIN_DATE, and the newer result we ask for today date'''
Min_Date = datetime(2016,04,18)

Max_Date = datetime(2017,04,18)

'''Predict the value of the stock after X days'''
Sale_After = 7


'''Singelton function, we need only one Object of list that contains dictionary for each day,close gate'''
def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

'''Create the list object, this class override the Singleton class, we need only one instance of list'''
@singleton
class ExtractedItems(object):
    '''The list will contains dict, with date and close gate of the each date'''
    data = list()
    Cost = 0
    Profit = 0


'''Crating a list object'''
extracted_items = ExtractedItems()

'''This class will connect to the Yhaoo API and get the data for the input comany name'''
class Extract_Data():
    '''TYPE:company_name- String
       start_date- DateTime
       end_date- DateTime
       '''
    def __init__(self,company_name,start_date,end_date):
        self.extracted_items = ExtractedItems()

        self.start = start_date
        self.end = end_date
        #Connect to Yahoo_api, with the company name:
        '''Crating a Yhaoo API object that get as input string of company name'''
        self.company = Share(company_name)
        self.number = 0
        '''Dictionary with two keys, Day- date of the close gate , Close_gate - value of the close gate'''
        self.dict={'Day':'',
                   'Close_gate':''}
        #Run Connect_api function:
        self.Connect_api()

    def Connect_api(self):
        '''We call get_historical function, the input of this function is two dates as string type, this is the reason
           that we using strftime('%Y-%m-%d').
           Date will contains the result of that call'''
        data = self.company.get_historical(self.start.strftime('%Y-%m-%d'), self.end.strftime('%Y-%m-%d'))
        for day in reversed(data):
            '''for each tuple we save it as dict type and append it to our list'''
            Adj = float(day.get('Adj_Close'))
            date = int(self.number)

            self.number = self.number+1

            temp = self.dict.copy()
            temp['Day'] = date
            temp['Close_gate'] = Adj
            self.extracted_items.data.append(temp)
            #After runing this class with the constructor and Connect_api, the list contains the result of the company gates

'''This class using SKlearn to do the linear regression on the data that Extract_Data class collect'''
class Regression():
    '''TYPE:
            company_name- String,
            Buy_Date - Datetime,
            amount - int'''
    def __init__(self,comapny_name,Buy_Date,amount):
        self.extracted_items = ExtractedItems()
        #We using Pandas peckage to show the graph result with the linear line 
        self.data_frame = pd.DataFrame(self.extracted_items.data)
        self.X = self.data_frame['Day'].values
        self.Y = self.data_frame['Close_gate'].values
        '''X and Y will represent the axis of the graph'''
        self.company = comapny_name
        self.number_of_days = self.X.size
        self.Buy_Date = Buy_Date
        self.amount = amount
        #Run Creat_regression function:
        self.Creat_regression()


    def Creat_regression(self):
        '''This function donig the regression on the data, reshape,fit,LinearRegression - '''
        #http://scikit-learn.org/stable/modules/classes.html
        X = self.X.reshape(self.number_of_days, 1)
        Y = self.Y.reshape(self.number_of_days, 1)
        self.regression = linear_model.LinearRegression()
        self.regression.fit(X, Y)

        '''This gap is the numbre of the days between the day that the user buy the stocks and max date that is today''' 
        differents = self.Buy_Date - Max_Date

        self.gate_before = self.regression.predict(self.number_of_days + differents.days)
        self.gate_after = self.regression.predict(self.number_of_days + differents.days + Sale_After)

        Before = self.amount/self.gate_before

        After = Before * self.gate_after

        self.extracted_items.Cost = self.regression.predict(self.number_of_days + differents.days)

        self.extracted_items.Profit = After


        #Run Create_graph function:
        self.Create_graph(X,Y)
    '''This function is the function that print for the user the graph with the result'''
    def Create_graph(self,X,Y):
        plt.scatter(X, Y, color='black',s=2)
        plt.xlabel('Date')
        plt.ylabel('Gate')
        plt.title(self.company+' results')
        plt.plot(X, self.regression.predict(X), color='blue', linewidth=2)
        plt.xticks(self.data_frame['Day'].values)
        plt.yticks(self.data_frame['Close_gate'].values,size=5)
        plt.show()


class GUI():
    def __init__(self,app):
        self.app = app
        self.var = 1

        self.initUI()


    def initUI(self):
        #Input text boxes
        self.text_company = QLineEdit(self.app)
        self.text_company.move(120, 100)

        self.cal = QCalendarWidget(self.app)
        self.cal.hide()
        self.cal.move(120, 180)

        self.lbl = QLabel('\t\t',self.app)
        self.lbl.hide()
        self.lbl.move(120, 350)

        self.text_amount = QLineEdit(self.app)
        self.text_amount.hide()
        self.text_amount.move(120, 140)

        #Lables
        self.company = QLabel('Comapny', self.app)
        self.company.move(30, 100)

        self.buy_label = QLabel('Buy date', self.app)
        self.buy_label.move(30, 180)
        self.buy_label.hide()

        self.amount = QLabel('Amount', self.app)
        self.amount.hide()
        self.amount.move(30, 140)


        #Buttons
        self.quit = QPushButton('Quit button', self.app)
        self.quit.resize(self.quit.sizeHint())
        self.quit.move(630, 428)



        self.Enter = QPushButton('Enter', self.app)
        self.Enter.resize(self.Enter.sizeHint())
        self.Enter.move(300, 100)


        #General
        self.LED = QPixmap("Logo.PNG")
        self.pic = QLabel(self.app)
        self.pic.setPixmap(self.LED)
        self.pic.show()

        #self.submit.clicked.connect(self.Push_Submit)
        self.Enter.clicked.connect(self.get_input)

        self.quit.clicked.connect(QCoreApplication.instance().quit)


        #Franme
        self.app.setGeometry(400, 180, 700, 450)
        self.app.setWindowTitle('SCE')
        self.app.setWindowIcon(QIcon('icon.png'))
        self.app.show()

    def get_input(self):
        if self.var==1:
                if len(self.text_company.text())==0:
                    QMessageBox.warning(self.app,'Error!!', 'must type a name')
                else:
                    self.text_company.setText(self.text_company.text().upper())
                    self.text_company.setText(self.text_company.text().upper())
                    self.text_company.setDisabled(True)
                    self.text_amount.show()
                    self.amount.show()
                    self.var = self.var + 1
                    self.Enter.move(300, 140)
        elif self.var==2:
            try:
                if int(self.text_amount.text())<=0:
                    QMessageBox.warning(self.app,'Error!!', 'Must be more then zero')
                else:
                    self.text_amount.setText(self.text_amount.text())
                    self.text_amount.setDisabled(True)
                    #self.cal.H()
                    self.lbl.show()
                    self.var = self.var + 1
                    self.Enter.move(300, 350)
                    self.Enter.setText('Show Calender..')
                    self.Enter.resize(self.Enter.sizeHint())
            except:
                QMessageBox.warning(self.app, 'Error!!', 'Must be an integer number')
        elif self.var == 3:
            self.cal.show()

            self.Enter.setText('Select date..')
            self.Enter.resize(self.Enter.sizeHint())

            self.cal.clicked[QtCore.QDate].connect(self.showDate)



    def showDate(self, date):
        date_var_date = parse_date(date.toString(), fuzzy=True)
        date_var = date_var_date.strftime("%d-%b-%Y")
        today = datetime.today()
        self.lbl.setText(date_var)
        self.lbl.move(120,180)
        self.buy_label.show()
        if date_var_date < today:
            QMessageBox.warning(self.app, 'Error!!', 'Date must be future')
        else:
            self.cal.hide()
            self.Enter.hide()
            self.Data(date_var_date)

    def Data(self,date_var_date):
        Extract_Data(self.text_company.text(), Min_Date, Max_Date)
        Regression(str(self.company), date_var_date, int(self.text_amount.text()))

        self.text_Cost = QLineEdit(self.app)
        self.text_Cost.move(300, 220)
        self.cost = QLabel('The value of th stock at the day that you want to buy ', self.app)
        self.cost.resize(self.cost.sizeHint())
        self.cost.move(30, 220)

        self.text_profit = QLineEdit(self.app)
        self.text_profit.move(300, 260)
        self.profit = QLabel('Your amount after a week from the buy date', self.app)
        self.profit.resize(self.profit.sizeHint())
        self.profit.move(30, 260)


        self.text_Cost.show()
        self.cost.show()
        self.text_profit.show()
        self.profit.show()
        self.text_Cost.setText(str(extracted_items.Cost[0][0]))
        self.text_profit.setText(str(extracted_items.Profit[0][0]))

class main():
    def __init__(self):
        app = QApplication(sys.argv)
        w = QWidget()
        ex = GUI(w)
        sys.exit(app.exec_())
main()

















