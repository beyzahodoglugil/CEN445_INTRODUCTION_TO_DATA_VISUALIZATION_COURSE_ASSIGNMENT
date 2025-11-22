# 1. repo'yu clone et
git clone <repo-url>
cd CEN445_Dashboard

# 2. sanal ortam oluştur
py -3.12 -m venv .venv

# 3. aktif et
.\.venv\Scripts\Activate.ps1   # PowerShell (VS Code)

# 4. paketleri yükle
pip install -r requirements.txt

# 5. çalıştır
python -m streamlit run app.py
# veya çift tıkla run_dashboard.bat


git clone <repo-url>
cd CEN445_Dashboard
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
