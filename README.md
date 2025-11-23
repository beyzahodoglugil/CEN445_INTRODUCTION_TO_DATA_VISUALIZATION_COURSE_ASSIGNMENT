# 📊 Mental Health & Lifestyle Interactive Dashboard
**CEN445 – Introduction to Data Visualization**  
**Project Submission – 23/11/2025 23:59**

This project presents an interactive data visualization dashboard built using **Python** and **Streamlit**. The dashboard explores associations between lifestyle factors (sleep, physical activity, screen time) and several mental health indicators.

The dataset contains over **2,000 rows** and multiple numerical and categorical attributes, making it suitable for multi-dimensional exploratory visual analysis.

---

## 📁 Project Structure

CEN445_Dashboard/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│ └── Mental_Health_Lifestyle_CLEAN.csv
│
└── plots/ (optional – if saving PNGs)


---

## 🧠 Dataset Description  
The dataset includes lifestyle and mental health–related variables such as:

- Sleep Hours  
- Screen Time per Day (Hours)  
- Exercise Level (Low / Moderate / High)  
- Stress Level (Low / Moderate / High)  
- Happiness Score  
- Age, Gender, Country  

The dataset was cleaned and preprocessed before being used in the dashboard (handling missing values, normalizing formats, validating data types).

**Preprocessing was completed by:**  
➡️ Furkan Çoban

---

## 🔍 Project Goal
The main goal of the project is to design an interactive dashboard that allows users to:

- Explore relationships between lifestyle habits and mental health indicators  
- Compare multiple numerical variables simultaneously  
- Gain insight through well-designed, high-contrast visualizations  
- Interact with the data via filters, sliders, dropdowns and dynamic chart settings  

---

## 📈 Visualizations Included (Total: 9)

## 👥 Team Members & Contributions

### **1st Member – Naciye Beyza Hodoğlugil - 2021555029**
Beyza implemented three visualizations and prepared the written project report. Her visualizations include:
- **Scatter Plot**  
  - Zoom and pan  
  - Hover tooltips (age, stress level, sleep hours)  
  - Gender-based color encoding  
- **Treemap**  
  - Hover explanations for each category  
  - Diet-type filter  
  - Mental health type selection  
- **Box Plot**  
  - Dropdown-based age-range filtering  
  - Hover display of mean/median values

---

### **2nd Member – Furkan Çoban - 2022555460**
Furkan handled the full preprocessing pipeline and integrated all team members' visualizations into the unified `app.py` file. His implemented visualizations are:
- **Parallel Coordinates Plot**  
  - Hover highlight  
  - Stress-level color encoding  
  - Multi-axis filtering  
- **Sunburst Chart**  
  - Zoom in/out  
  - Hover-based hierarchical detail display  
- **Bar Chart**  
  - Country selection dropdown  
  - Detailed hover information

---

### **3rd Member – Nadire Şeker - 2020556058**
Nadire implemented three visualizations and prepared the project README file. Her visualizations include:
- **Scatter Matrix**  
  - Sleep, screen time, and happiness comparison  
  - Stress-level color coding  
  - Exercise-level symbol differentiation  
  - Hover tooltips  
- **Heatmap**  
  - Screen-time bin slider  
  - Exercise level vs. average happiness  
  - Viridis color scale  
- **Violin Plot**  
  - Happiness distribution by exercise level  
  - Gender filter  
  - Box + point representation

---

## 🚀 How to Run the Dashboard

### **1. Clone the repository**
git clone <repo-url>
cd CEN445_Dashboard

### **2. Create virtual environment (Python 3.12 recommended)** 
py -3.12 -m venv .venv

### **3. Activate the environment**
Windows PowerShell
.\.venv\Scripts\Activate.ps1

### **4. Install required packages**
pip install -r requirements.txt

### **5. Run the application**
python -m streamlit run app.py

### **6. The dashboard will open automatically in your browser at:
👉 http://localhost:8501

---

## 🧩 Technologies Used
- Python 3.12
- Streamlit
- Pandas
- NumPy
- Plotly Express
- Seaborn / Matplotlib (optional)

---

## 📎 Repository Link
https://github.com/beyzahodoglugil/CEN445_INTRODUCTION_TO_DATA_VISUALIZATION_COURSE_ASSIGNMENT 

---

## 📄 License
This project is developed for academic purposes as part of CEN445 – Introduction to Data Visualization.