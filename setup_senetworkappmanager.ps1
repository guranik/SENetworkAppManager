python -m venv venv
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

if (-Not (Test-Path "$env:USERPROFILE\.cache\torch\hub\snakers4_silero-vad_master")) {
    git clone https://github.com/snakers4/silero-vad "$env:USERPROFILE\.cache\torch\hub\snakers4_silero-vad_master"
}

New-Item -ItemType Directory -Force -Path input,segments | Out-Null
