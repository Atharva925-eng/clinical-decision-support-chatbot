# STEP 5️⃣ — Fetch Description, Medications, Diets

## Goal
Attach full medical data (description, medications, precautions, diet) to disease predictions.

## Implementation

### Two Functions Available

#### 1. `get_disease_data(disease)` - Simple Approach
Fetches description, medications, and diet directly from CSV datasets.

```python
def get_disease_data(disease):
    """
    Simple, direct approach to retrieve medical data.
    
    Returns: {
        'description': [...],
        'medications': [...],
        'diet': [...]
    }
    """
    data = {
        'description': [],
        'medications': [],
        'diet': []
    }
    
    # Fetch from datasets
    if not descriptions_df.empty:
        desc = descriptions_df[
            descriptions_df['disease'].str.lower() == disease.lower()
        ]['description'].values.tolist()
        data['description'] = desc
    
    if not medications_df.empty:
        meds = medications_df[
            medications_df['disease'].str.lower() == disease.lower()
        ]['medication'].values.tolist()
        data['medications'] = meds
    
    if not diet_df.empty:
        diets = diet_df[
            diet_df['disease'].str.lower() == disease.lower()
        ]['diet'].values.tolist()
        data['diet'] = diets
    
    return data
```

**Usage:**
```python
disease_data = get_disease_data("cold")
# Returns:
# {
#     'description': ['A common viral infection...'],
#     'medications': ['Aspirin', 'Ibuprofen', 'Cough syrup'],
#     'diet': ['Warm liquids', 'Vitamin C fruits']
# }
```

#### 2. `get_disease_details(disease_name)` - Extended Approach
Fetches description, medications, precautions, AND diet with structured format.

```python
def get_disease_details(disease_name):
    """
    Comprehensive approach with error handling and structured output.
    
    Returns: {
        'description': 'Full text...',
        'medications': [{'name': 'Drug', 'dosage': '...'}],
        'precautions': ['Do not...', 'Avoid...'],
        'diet': {
            'recommended': ['Fruits', 'Vegetables'],
            'avoid': ['Spicy', 'Fatty']
        }
    }
    """
```

**Usage:**
```python
disease_details = get_disease_details("cold")
# Returns structured data with dosage, precautions, and dietary categories
```

## Inside /predict Route

### Data Retrieval Loop
```python
# STEP 5: Build disease list and retrieve details
diseases_list = []
diseases_details = {}

for rank, (disease, score) in enumerate(top_diseases_ranked, 1):
    # Add to diseases list
    diseases_list.append({
        'rank': rank,
        'name': disease,
        'confidence': round(confidence, 2),
        'symptom_count': score
    })
    
    # Option 1: Using get_disease_details() (includes precautions)
    details = get_disease_details(disease)
    
    # Option 2: Using get_disease_data() (simpler)
    # data = get_disease_data(disease)
    
    diseases_details[disease] = details
```

## CSV Dataset Structure Required

### 1. `data/descriptions.csv`
```
disease, description
Cold, "A common viral infection affecting the upper respiratory tract..."
Flu, "Influenza is a contagious respiratory disease..."
```

### 2. `data/medications.csv`
```
disease, medication, dosage
Cold, Aspirin, "500mg every 6 hours"
Cold, Ibuprofen, "200mg every 4-6 hours"
Flu, Oseltamivir, "75mg twice daily for 5 days"
```

### 3. `data/diets.csv`
```
disease, recommended, avoid
Cold, "Warm liquids", "Dairy products"
Cold, "Vitamin C fruits", "Spicy foods"
Flu, "Broths", "Heavy foods"
```

### 4. `data/symptoms.csv`
```
symptom, disease
fever, Cold
fever, Flu
fever, Malaria
cough, Cold
cough, Flu
sore throat, Cold
sore throat, Pharyngitis
```

### 5. `data/precautions.csv`
```
disease, precaution
Cold, "Wash hands frequently"
Cold, "Avoid contact with others"
Cold, "Stay hydrated"
Flu, "Get vaccinated annually"
Flu, "Avoid crowded places"
```

## Response Format

The `/predict` endpoint returns all disease data:

```json
{
  "success": true,
  "received_symptoms": "fever, cough",
  "matched_symptoms": ["fever", "cough"],
  "diseases": [
    {
      "rank": 1,
      "name": "Cold",
      "confidence": 1.0,
      "symptom_count": 2
    }
  ],
  "reasoning": "Based on the provided symptoms (fever, cough), the analysis indicates Cold...",
  "description": "A common viral infection affecting the upper respiratory tract...",
  "medications": [
    {
      "name": "Aspirin",
      "dosage": "500mg every 6 hours"
    },
    {
      "name": "Ibuprofen",
      "dosage": "200mg every 4-6 hours"
    }
  ],
  "precautions": [
    "Wash hands frequently",
    "Avoid contact with others",
    "Stay hydrated"
  ],
  "diet": {
    "recommended": [
      "Warm liquids",
      "Vitamin C fruits"
    ],
    "avoid": [
      "Dairy products",
      "Spicy foods"
    ]
  }
}
```

## API Endpoint
**POST** `/predict`

**Request:**
```json
{
  "symptoms": "fever, cough, sore throat"
}
```

**Response:** Complete analysis with medications, precautions, and diet recommendations.

## Key Features

✅ **Two fetching approaches** - Simple or detailed  
✅ **Case-insensitive matching** - Works with any capitalization  
✅ **Error handling** - Gracefully handles missing data  
✅ **Duplicate removal** - Unique medications and precautions  
✅ **Top 3 diseases** - Returns only ranked results  
✅ **Confidence scoring** - Shows symptom overlap percentage  
✅ **Structured diet data** - Recommended vs. avoid separation  
✅ **Dosage information** - Includes medication dosages  

## Testing

Use the browser's Developer Tools (F12) → Console to see detailed logs:

```
🔍 Extracting Symptoms...
✅ Matched symptoms: ['fever', 'cough']

🔗 Mapping Symptoms to Diseases...
📊 Disease Scores:
  Cold: 2 symptom(s)

🎯 Ranking Diseases...
🏥 Retrieving Disease Details...
  ✅ Description found for Cold
  ✅ 2 medication(s) found
  ✅ 3 precaution(s) found
  ✅ Diet recommendations found

✅ ANALYSIS COMPLETE
```

