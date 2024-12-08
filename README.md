# **Recipe Analysis and Scoring App** 🍽  

### **Overview**  
This project is a **Streamlit-based application** for analyzing recipes, introducing a new scoring method, and examining the seasonality of ingredients. It was developed as part of our *Kit Big Data* course.  

---

## **Continuous Integration and Deployment** 🚀  

We implemented a **Continuous Integration (CI)** pipeline using **GitHub Actions**.  

- **CI Pipeline**:  
  - The pipeline performs linting checks with `flake8`.
  - Unit tests are executed using `pytest`.

### **Continuous Deployment (CD)**  

1. **Streamlit Cloud**:  
   - Initially, we attempted to deploy the app on **Streamlit Cloud**.  
   - However, the **volume of data** pulled during runtime was too large for the platform's resources.  

2. **Render Deployment**:  
   - We migrated to **Render** to handle deployment.  
   - You can view the app here: https://seasonal-cooking-buddy.onrender.com 
   - While the **home page** works as expected, the **RAM limit** on the free plan prevents loading additional pages that require more memory for the data processing.  

---

## **Instructions to Run the App Locally** 🛠  

Follow these steps to clone, configure, and run the app locally:

### **1. Clone the Repository**  
Clone the project repository to your local machine:  

```bash
git clone https://github.com/ramzinaji/analyse_cooking_app.git
cd your-repo-link
```

### **2. Install Dependencies with Poetry**  
install the project dependencies:

```bash
cd etude_app_cuisine
poetry install
```

Activate the Poetry environment:

```bash
poetry shell
```

### **3. Pull the Dataset**  
Run the LoadData.py script to download the necessary data into the data_loaded/ directory:

```bash
cd src
python LoadData.py
```

This script downloads the JSON datasets from Google Drive and places them in the appropriate folder.

### **4. Run the Application**  
Run the LoadData.py script to download the necessary data into the data_loaded/ directory:

```bash
streamlit run app_v3.py
```

The app will be available at http://localhost:8501 in your browser.

### **5. Logs** 📝  
Logs for the application are automatically generated and stored in the **`logs/`** directory.  
These logs include:

- **Application initialization messages**  
- **Errors or warnings during data processing**  
- **User interactions**  

---

### **Contributors** 👥  
- **ADIL Nawfal**  
- **ESKINAZI Etienne**  
- **MALAININE Mohamed Limame**  
- **NAJI Ramzi**  
