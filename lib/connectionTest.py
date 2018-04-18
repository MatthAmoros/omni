from sourceFactory import SourceFactory
import pyodbc  #For MS SQL connection, via odbc

print "PyODBC drivers : "
print str(pyodbc.drivers())

src = SourceFactory('DB', "../cfg/connectionString.sql")
src.loadClientConfiguration(202481600137230)
