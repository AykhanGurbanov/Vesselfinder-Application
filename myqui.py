from PyQt5 import uic
import requests as rq
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt



class MyQui(QMainWindow):

    def __init__(self, parent=None):
        super(MyQui, self).__init__(parent)
        uic.loadUi('Data_Calculation2tablecharm.ui', self)
        self.show()
        self.Vericek.clicked.connect(self.ara)
        self.Hesapson.clicked.connect(self.hesapla)
        self.pushButton_2.clicked.connect(self.grafik)
        self.horizontalLayout_1=QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")
        self.figure=plt.figure()
        self.canvas=FigureCanvas(self.figure)
        self.horizontalLayout_1.addWidget(self.canvas)


    def ara(self):
        Ship_Flag = ('AZ', 'TR', 'RU','CN','AL')
        if self.comboBox.currentText() == "Azerbaijan":
            Ship_Flag = Ship_Flag[0]
        if self.comboBox.currentText() == "Turkey":
            Ship_Flag=Ship_Flag[1]
        if self.comboBox.currentText() == "Russian":
            Ship_Flag=Ship_Flag[2]
        if self.comboBox.currentText() == "China":
            Ship_Flag=Ship_Flag[3]
        if self.comboBox.currentText() == "Albania":
            Ship_Flag=Ship_Flag[4]
        Ship_type=[4,6,3,403,401]
        if self.Gemituru.currentText() == "All Cargo Vessels":
            Ship_type = Ship_type[0]
        if self.Gemituru.currentText() == "Container Ship":
            Ship_type = Ship_type[3]
        if self.Gemituru.currentText() == "All Tankers":
            Ship_type = Ship_type[1]
        if self.Gemituru.currentText() == "All Passenger":
            Ship_type = Ship_type[2]
        if self.Gemituru.currentText() == "Bulk Carrier":
            Ship_type = Ship_type[4]
        Ship_length = self.Uzunlukmin.text()
        Ship_gross_t = self.GrossTon.text()
        Ship_gross_t2 = self.maxgross.text()
        Ship_dwt2 = self.maxdwt.text()
        Ship_Dwt = self.Dwtmin.text()
        Ship_length2 = self.maxuzun.text()
        header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        a=[]
        for i in range(2):
            url = f'https://www.vesselfinder.com/tr/vessels?page={i+1}&type={Ship_type}&flag={Ship_Flag}&minLength={Ship_length}&maxLength={Ship_length2}&minGT={Ship_gross_t}&maxGT={Ship_gross_t2}&minDW={Ship_Dwt}&maxDW={Ship_dwt2}'
            tablo = rq.get(url, headers=header)
            a.append(pd.read_html(tablo.text))
        p=a[0]+a[1]
        # data = {'Gemi': p[0].Gemi, 'Insaa': p[0].İnşa, 'Gross Tonaj': p[0].GT, 'DWT': p[0].DWT,'Olcu': p[0]["Ölçü (m)"]}
        df=pd.concat([p[0], p[1]], ignore_index=True)
        self.tblsonuc.clear()
        a = df.iloc[:, 4].str.split(' ', expand=True)
        df['Uzunluk'] = a[0]
        df['Genislik'] = a[2]
        for i in range(6):
            df.iloc[:, i + 1] = df.iloc[:, i + 1].replace('-', 0)
            df.iloc[:, i + 1] = df.iloc[:, i + 1].fillna(value=0)
        self.tblsonuc.setHorizontalHeaderLabels(
            ("Gemi adi", "Üretim yılı", "Dwt", "Gross Tonaj", "Uzunluk", "Genislik"))
        for i in range(len(df["Gemi"])):
            self.tblsonuc.setItem(i, 0, QTableWidgetItem(str(df.iloc[i, 0])))
            self.tblsonuc.setItem(i, 1, QTableWidgetItem(str(df.iloc[i, 1])))
            self.tblsonuc.setItem(i, 2, QTableWidgetItem(str(df.iloc[i, 2])))
            self.tblsonuc.setItem(i, 3, QTableWidgetItem(str(df.iloc[i, 3])))
            self.tblsonuc.setItem(i, 4, QTableWidgetItem(str(df.iloc[i, 5])))
            self.tblsonuc.setItem(i, 5, QTableWidgetItem(str(df.iloc[i, 6])))
        return df

    def hesapla(self):
        df = self.ara()
        try:
            for i in range(6):
                df.iloc[:, i + 1] = df.iloc[:, i + 1].replace('-', 0)
                df.iloc[:, i + 1] = df.iloc[:, i + 1].fillna(value=0)
            df['Uzunluk'] = df['Uzunluk'].astype('int64')
            df['Genislik'] = df['Genislik'].astype('int64')
            df['DWT'] = df['DWT'].astype('int64')
            df["GT"] = df["GT"].astype('int64')
            Deplasman_amprik = df['DWT'].mean() / ((0.775 * df['DWT'].mean()) / (df['DWT'].mean() + 250))
            V_hiz = ((((df['Uzunluk'].mean()) / (Deplasman_amprik ** (1 / 3))) - 3.333) / 1.666) * (
                    (df['Uzunluk'].mean()) ** (1 / 2))
            Rho = 1.025
            T = df['Genislik'].mean() / 2.5
            D = 1.5 * T
            Cb = Deplasman_amprik / (df['Uzunluk'].mean() * df['Genislik'].mean() * T * Rho)
            Cb_amprik = 1.12 - (0.5 * (V_hiz / (df['Uzunluk'].mean() ** (1 / 2))))
            Pb = 0.001 * (df['DWT'].mean() ** (2 / 3)) * (V_hiz ** 3)
            self.Sonucson.setHorizontalHeaderLabels(("Deplasman (ton)", "Gemi Hizi(knot)", "Draft(m)", "Derinlik(m)","Cb katsayisi", "Cb amprik", "Pb (kW)","Uzunluk","Genislik","DWT"))
            self.Sonucson.setItem(0, 0, QTableWidgetItem(str(Deplasman_amprik))),self.Sonucson.setItem(0, 1,QTableWidgetItem(str(V_hiz)))
            self.Sonucson.setItem(0, 2, QTableWidgetItem(str(T))),self.Sonucson.setItem(0, 3, QTableWidgetItem(str(D))),self.Sonucson.setItem(0, 4, QTableWidgetItem(str(Cb)))
            self.Sonucson.setItem(0, 5, QTableWidgetItem(str(Cb_amprik))), self.Sonucson.setItem(0, 6, QTableWidgetItem(str(Pb))),self.Sonucson.setItem(0, 7, QTableWidgetItem(str(df['Uzunluk'].mean())))
            self.Sonucson.setItem(0, 8, QTableWidgetItem(str(df['Genislik'].mean()))),self.Sonucson.setItem(0, 9, QTableWidgetItem(str(df['DWT'].mean())))
            self.statusbar.showMessage("Veri hesabi basrili", 20000)
        except Exception as error:
            self.statusbar.showMessage("Veri hesabi hatali islem === " + str(error))

    def grafik(self):
        df = self.ara()
        df['DWT'] = df['DWT'].astype('int64')
        df['Genislik'] = df['Genislik'].astype('int64')
        df['GT']=df['GT'].astype('int64')
        df['Uzunluk']=df['Uzunluk'].astype('int64')
        if self.SecX.currentText() == "Genislik":
            x = df['Genislik']
        if self.SecX.currentText() == "Uzunluk":
            x = df['Uzunluk']
        if self.SecX.currentText() == "Dwt":
            x = df['DWT']
        if self.SecX.currentText() == "Gross Tonaj":
            x = df['GT']
        try:
            self.figure.clear()
            # plt.scatter(x, y)
            plt.hist(x,bins=50,edgecolor='black')
            # plt.hist(y,bins=50,edgecolor='green')
            # plt.legend(["Dwt&Gross Tonaj"])
            # plt.plot(df['Gross Tonaj'],df['Uzunluk'])
            # plt.legend(["Gross&Uzunluk"])
            # plt.xlabel("DWT")
            # plt.ylabel("Genislik")
            self.canvas.draw()
        except Exception as error:
            self.statusbar.showMessage("Grafik Cizimi Hatali === " + str(error))


def main():
    app = QApplication([])
    window = MyQui()
    app.exec_()


if __name__ == '__main__':
    main()
