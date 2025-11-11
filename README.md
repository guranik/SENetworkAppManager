# SENetworkAppManager
Network System of speech extraction .Net+Python based on manual TCP realization (System.Net.Sockets)
Setup instructions. In PowerSHell:

git clone https://github.com/guranik/SENetworkAppManager

cd SENetworkAppManager

PowerShell -ExecutionPolicy Bypass -File setup_senetworkappmanager.ps1

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

venv\Scripts\activate

python split_audio.py
