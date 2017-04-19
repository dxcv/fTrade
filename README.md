# fTrade
Trade Tools and Utilities

## Folder Structure
+ AssetMgmt
  + DataCenter - CSV files containing financial data.
  + Python
    + fQuant - Python scripts for quant analysis.
    + fTrade - Python scripts for trade.
      + ctaStrategy
      + dataRecorder
      + gateway
        + ctpGateway
      + language
      + riskManager

## Environment Setup
+ OS: Windows 10 64-bit
+ Python2.7 32-bit: Anaconda2-4.0.0-Windows-x86.exe (PyQt4)
+ MongoDB Windows 64-bit 2008 R2+: mongodb-win32-x86_64-2008plus-ssl-3.4.3-signed.msi
+ Python Packages:
  + pymongo: pip install pymongo
  + QDarkStyleSheet: pip install qdarkstyle
  + wheel: pip install wheel
  + talib: pip install TA_Lib-0.4.10-cp27-cp27m-win32.whl
+ MongoDB as Windows Service: http://jingyan.baidu.com/article/6b97984dbeef881ca2b0bf3e.html
  + Register MongoDB Service
    +  mongod -dbpath "D:\MongoDB\Server\3.4\Data\db" -logpath "D:\MongoDB\Server\3.4\Data\log\MongoDB.log" -install -serviceName "MongoDB"
  + Start MongoDB Service
    +  net start mongodb
  + Stop MongoDB Service
    +  net stop mongodb
  + Un-register MongoDB Service
    +  mongod -dbpath "D:\MongoDB\Server\3.4\Data\db" -logpath "D:\MongoDB\Server\3.4\Data\log\MongoDB.log" -remove -serviceName "MongoDB"
+ VC++ VS2013 Runtime: https://www.microsoft.com/en-gb/download/details.aspx?id=40784
+ CTP Account: Register at http://simnow.com.cn/
+ CTP Config: Update ctpGateway\CTP_connect.json with your
  + account
  + password
  + broker id
  + trade server address
  + market server address
