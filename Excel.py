import win32com.client
import datetime


def Excel_write_relatif(data, sens_deplacement, save_continu, del_cell, auto_read):

    flag_excel = False

    xl = win32com.client.Dispatch("Excel.Application")
    wb = xl.ActiveWorkbook
    ws = xl.ActiveSheet
    ad = xl.ActiveCell.GetAddress()

    if del_cell or ws.Range(ad).Value == None :
        if auto_read:
            ws.Range(ad).Value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.Range(ad).Offset(1, 2).Value = data
        else:
            ws.Range(ad).Value = data
        print 'data'
    elif not del_cell and ws.Range(ad).Value != None :
        flag_excel = True
        print 'del_cell'

    try :
        if not auto_read:
            if "bas" in sens_deplacement.lower() : ws.Range(ad).Offset(2,1).Select()
            if "droite" in sens_deplacement.lower() : ws.Range(ad).Offset(1,2).Select()
            if "haut" in sens_deplacement.lower() : ws.Range(ad).Offset(0,1).Select()
            if "gauche" in sens_deplacement.lower() : ws.Range(ad).Offset(1,0).Select()
        else:
            ws.Range(ad).Offset(2,1).Select()
    except: pass

    if save_continu : wb.Save()

    return flag_excel, ad

def Excel_write_absolu():

    xl = win32com.client.Dispatch("Excel.Application")

    wb = excel.ActiveWorkbook
    sheet = book.ActiveSheet
    sheet.Range("A1").Value = "Hello World!"
    ##sheet = None
    ##book = None
    ##excel.Quit()
    ##excel = None


if __name__ == '__main__':
    Excel_write_relatif('-100','gauche',False,True)