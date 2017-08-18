@ECHO off

cd src
set /p ip="IP : (default=0.0.0.0) :"
set /p metaport="META PORT : (default=5006) :"
set /p innerport="INNER PORT : (default=5005) :"

IF /i "%ip%" == "" set ip="0.0.0.0"
IF /i "%metaport%" == "" set metaport="5006"
IF /i "%innerport%" == "" set innerport="5005"

venv\Scripts\Activate

python ./server.py --ip %ip% --meta_port %metaport% --inner_port %innerport%
PAUSE
