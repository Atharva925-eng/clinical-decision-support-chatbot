# Clinical Decision Support Chatbot

A chatbot application designed to provide clinical decision support by analyzing user symptoms and predicting potential diseases with medications, precautions, and diet recommendations.

## Features

✅ **Symptom Analysis** - Extracts known symptoms from free-text user input  
✅ **Disease Prediction** - Matches symptoms to diseases using intelligent scoring  
✅ **Disease Ranking** - Returns top 1-3 diseases by confidence score  
✅ **Medical Details** - Provides medications, precautions, and diet recommendations  
✅ **Clinical Reasoning** - Generates adaptive explanations for predictions  
✅ **Medical Disclaimer** - Mandatory disclaimers on every response  
✅ **Responsive UI** - Professional healthcare interface  

## Project Structure

- `/data` - Dataset files (symptoms, descriptions, medications, precautions, diets)
- `/static` - Static files (CSS, JavaScript, assets)
- `/templates` - HTML templates
- `app.py` - Flask application entry point
- `requirements.txt` - Python dependencies

## Setup

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The application will start on **http://127.0.0.1:5000**

---

## Testing the Chatbot

### **Option 1: Web Browser (Recommended)**

1. Start the server: `python app.py`
2. Open: **http://127.0.0.1:5000**
3. Enter symptoms in the textarea
4. Click "Analyze Symptoms" to get results

### **Option 2: Using cURL (Terminal)**

#### **Test Case 1: Fever & Cough (Cold/Flu)**
```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"symptoms": "fever cough sore throat body aches fatigue"}'
```

**Expected Result:** Influenza or Cold with confidence scores

#### **Test Case 2: Skin Rash & Itching (Fungal Infection)**
```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"symptoms": "itching skin rash nodal skin eruptions dischromic patches"}'
```

**Expected Result:** Fungal infection with 90%+ confidence

#### **Test Case 3: Heartburn & Stomach Pain (GERD)**
```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"symptoms": "acidity heartburn stomach pain burning sensation"}'
```

**Expected Result:** GERD with treatment recommendations

#### **Test Case 4: Allergic Reaction**
```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"symptoms": "sneezing watery eyes runny nose itching throat"}'
```

**Expected Result:** Allergy with antihistamine recommendations

#### **Test Case 5: Weight Gain & Fatigue (Thyroid)**
```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"symptoms": "weight gain fatigue cold sensitivity hair loss"}'
```

**Expected Result:** Hypothyroidism with hormone replacement info

---

## Example Input Formats

### **Format 1: Comma-Separated**
```
fever, cough, sore throat, body aches
```

### **Format 2: Space-Separated**
```
fever cough sore throat body aches
```

### **Format 3: Natural Language**
```
I have a fever, I'm coughing a lot, and my throat hurts
```

All formats are supported! The chatbot extracts known symptoms automatically.

---

## Sample API Response

```json
{
  "success": true,
  "received_symptoms": "fever cough sore throat",
  "matched_symptoms": ["fever", "cough", "sore throat"],
  "diseases": [
    {
      "rank": 1,
      "name": "Influenza",
      "confidence": 0.98,
      "symptom_count": 3
    },
    {
      "rank": 2,
      "name": "Cold",
      "confidence": 0.87,
      "symptom_count": 2
    }
  ],
  "reasoning": "The prediction is based on 3 matching symptom(s): fever, cough, sore throat. The strong symptom overlap indicates high likelihood.",
  "description": "Influenza (flu) is a contagious respiratory illness...",
  "medications": [
    {"name": "Oseltamivir", "dosage": "75mg twice daily"},
    {"name": "Acetaminophen", "dosage": "650mg every 6 hours"}
  ],
  "precautions": [
    "Get adequate rest",
    "Stay hydrated",
    "Avoid close contact with others"
  ],
  "diet": {
    "recommended": ["Warm liquids", "Honey", "Ginger tea"],
    "avoid": ["Dairy", "Spicy foods", "Cold drinks"]
  },
  "disclaimer": "⚠️ MEDICAL DISCLAIMER - This is for clinical decision support only..."
}
```

---

## Error Handling

### **Empty Input**
```
(Leave blank and click submit)
```
**Response:** "Please enter at least one symptom"

### **Unrecognized Symptoms**
```
xyzabc random nonsense
```
**Response:** "Please provide more symptoms for accurate analysis"

### **Insufficient Matched Symptoms**
```
headache
```
**Response:** May show results but with lower confidence or suggest more symptoms

---

## Supported Diseases

The chatbot can diagnose over 40 diseases including:
- Fungal infection, Allergy, GERD, Chronic cholestasis
- Hypothyroidism, Hyperthyroidism, Arthritis, Vertigo
- Acne, Bronchial asthma, Pneumonia, Malaria
- And 30+ more conditions in the database

---

## Technologies Used

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Data:** Pandas, CSV files
- **Medical Data:** 5 datasets (symptoms, medications, precautions, descriptions, diets)

---

## Medical Disclaimer

⚠️ **IMPORTANT:** This chatbot is for **clinical decision support only** and is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

- Always consult with a qualified healthcare professional
- In medical emergencies, call emergency services immediately
- This tool does not account for individual patient factors or medical history

By using this application, you acknowledge these limitations and assume full responsibility for any decisions made based on its output.
