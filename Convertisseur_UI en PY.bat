set folder=D:\Python\RS232-balances
set infile=Balances.ui



set outfile=%infile:.ui=_UI.py%
set sep=\

"C:\Python27\python.exe" "C:\Python27\Lib\site-packages\PyQt4\uic\pyuic.py" -x "%folder%%sep%%infile%" -o "%folder%%sep%%outfile%"
::explorer %folder%
::pause