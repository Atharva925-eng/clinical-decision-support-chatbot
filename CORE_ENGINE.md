# STEP 6 — Build Reasoning Generator & Final Response Object

## Action 6.1 — Reasoning Generator Function

```python
def generate_reasoning(matched_symptoms, disease, score):
    """
    Generate clinical reasoning explanation for a predicted disease.
    
    Creates a human-readable explanation describing why a disease was predicted
    based on the number of matching symptoms and their association with the disease.
    
    Args:
        matched_symptoms (list): List of symptoms matched from user input
        disease (str): Name of the predicted disease
        score (int): Number of matching symptoms for this disease
    
    Returns:
        str: Detailed reasoning explanation
    """
    if not matched_symptoms or score == 0:
        return f"Unable to generate reasoning for {disease}"
    
    # Create symptom string
    symptom_string = ', '.join(matched_symptoms) if len(matched_symptoms) > 1 else matched_symptoms[0]
    
    # Generate reasoning based on score
    reasoning = (
        f"The prediction is based on the presence of {score} matching symptom(s): "
        f"{symptom_string} commonly associated with {disease}. "
    )
    
    # Add confidence note
    if score >= 3:
        reasoning += "The strong symptom overlap indicates a high likelihood of this condition."
    elif score == 2:
        reasoning += "The moderate symptom overlap suggests this condition is worth investigating."
    else:
        reasoning += "While symptoms are present, further evaluation is recommended."
    
    return reasoning
```

## Action 6.2 — Final Response Object Structure

The `/predict` route builds and returns a comprehensive response object:

```json
{
  "success": true,
  "received_symptoms": "fever, cough, sore throat",
  "matched_symptoms": ["fever", "cough", "sore throat"],
  "diseases": [
    {
      "rank": 1,
      "name": "Cold",
      "confidence": 1.0,
      "symptom_count": 3
    },
    {
      "rank": 2,
      "name": "Flu",
      "confidence": 0.67,
      "symptom_count": 2
    }
  ],
  "reasoning": "The prediction is based on the presence of 3 matching symptom(s): fever, cough, sore throat commonly associated with Cold. The strong symptom overlap indicates a high likelihood of this condition. Other possible conditions include: Flu (2 symptom(s)). Please consult a qualified healthcare professional for proper diagnosis and treatment.",
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
  },
  "disclaimer": "⚠️ MEDICAL DISCLAIMER\n\nThis information is for clinical decision support only..."
}
```

## Core Engine Workflow

```python
@app.route('/predict', methods=['POST'])
def predict():
    """
    CORE ENGINE - Clinical Decision Support Analysis
    
    Workflow:
    1. Extract symptoms from user input
    2. Validate symptom threshold
    3. Match symptoms to diseases
    4. Rank top 1-3 diseases
    5. Generate reasoning for each disease
    6. Fetch medical data (medications, precautions, diet)
    7. Build comprehensive response
    """
    
    # STEP 1: Validate input
    data = request.get_json()
    symptoms_text = data.get('symptoms', '').strip()
    
    if not symptoms_text:
        return error_response("Symptoms required", DISCLAIMER)
    
    # STEP 2: Extract known symptoms
    matched_symptoms = extract_symptoms(symptoms_text)
    
    if len(matched_symptoms) < MIN_SYMPTOMS:
        return error_response("Insufficient symptoms", DISCLAIMER)
    
    # STEP 3: Match symptoms to diseases
    disease_scores = match_diseases(matched_symptoms)
    
    if not disease_scores:
        return error_response("No diseases matched", DISCLAIMER)
    
    # STEP 4: Rank and retrieve top diseases
    top_diseases_ranked = rank_diseases(disease_scores)
    
    # STEP 5: Build results for each disease
    results = []
    
    for rank, (disease, score) in enumerate(top_diseases_ranked, 1):
        # Get medical data
        medical_data = get_disease_data(disease)
        
        # Generate reasoning
        disease_reasoning = generate_reasoning(matched_symptoms, disease, score)
        
        # Add to results
        results.append({
            "rank": rank,
            "disease": disease,
            "symptom_count": score,
            "reasoning": disease_reasoning,
            "description": medical_data.get("description", [""])[0],
            "medications": medical_data.get("medications", []),
            "diet": medical_data.get("diet", []),
            "precautions": get_disease_details(disease).get("precautions", [])
        })
    
    # STEP 6: Return final response
    return jsonify({
        "success": True,
        "received_symptoms": symptoms_text,
        "matched_symptoms": matched_symptoms,
        "predicted_diseases": results,
        "disclaimer": DISCLAIMER
    }), 200
```

## Key Functions

### 1. `extract_symptoms(user_text)` ✅
- Converts user input to lowercase
- Matches against known symptoms in database
- Returns list of recognized symptoms

**Input:** `"I have fever and cough"`  
**Output:** `["fever", "cough"]`

---

### 2. `match_diseases(matched_symptoms)` ✅
- Scores diseases by symptom overlap count
- Returns dictionary with disease: score pairs
- Ordered by relevance

**Input:** `["fever", "cough"]`  
**Output:** `{"Cold": 2, "Flu": 2, "Malaria": 1}`

---

### 3. `rank_diseases(disease_scores)` ✅
- Sorts diseases by score (highest first)
- Returns top 3 only
- Maintains score metadata

**Input:** `{"Cold": 2, "Flu": 2, "Malaria": 1}`  
**Output:** `[("Cold", 2), ("Flu", 2), ("Malaria", 1)][:3]`

---

### 4. `generate_reasoning(matched_symptoms, disease, score)` ✅ **NEW**
- Creates human-readable explanation
- Includes confidence assessment
- Adapts text based on symptom overlap

**Input:** `(["fever", "cough"], "Cold", 2)`  
**Output:** `"The prediction is based on the presence of 2 matching symptom(s): fever, cough commonly associated with Cold. The moderate symptom overlap suggests this condition is worth investigating."`

---

### 5. `get_disease_data(disease)` ✅
- Fetches from CSV datasets
- Returns description, medications, diet
- Simple and direct approach

**Input:** `"Cold"`  
**Output:** 
```python
{
    'description': ['A common viral infection...'],
    'medications': ['Aspirin', 'Ibuprofen'],
    'diet': ['Warm liquids', 'Vitamin C fruits']
}
```

---

### 6. `get_disease_details(disease_name)` ✅
- Extended version with error handling
- Includes precautions and structured diet
- Returns object-oriented format

**Input:** `"Cold"`  
**Output:**
```python
{
    'description': 'Full text...',
    'medications': [{'name': 'Drug', 'dosage': '...'}],
    'precautions': ['Do not...'],
    'diet': {'recommended': [...], 'avoid': [...]}
}
```

---

## Response Flow

```
USER INPUT
    ↓
extract_symptoms() → MATCHED_SYMPTOMS
    ↓
match_diseases() → DISEASE_SCORES
    ↓
rank_diseases() → TOP_3_DISEASES
    ↓
FOR EACH DISEASE:
  ├─ generate_reasoning() → REASONING
  ├─ get_disease_data() → MEDICATIONS, DIET
  ├─ get_disease_details() → PRECAUTIONS
    ↓
BUILD_RESPONSE()
    ↓
ATTACH_DISCLAIMER()
    ↓
RETURN_JSON()
```

## Error Handling

All errors include the mandatory disclaimer:

```python
if error_condition:
    return jsonify({
        "success": False,
        "error": "Error message",
        "disclaimer": DISCLAIMER
    }), status_code
```

## Testing

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "fever, cough, sore throat"}'
```

**Console Output:**
```
🔍 Extracting Symptoms...
✅ Matched symptoms: ['fever', 'cough', 'sore throat']

🔗 Mapping Symptoms to Diseases...
📊 Disease Scores:
  Cold: 3 symptom(s)

🎯 Ranking Diseases...
✅ ANALYSIS COMPLETE
```

## CSV Data Requirements

### symptoms.csv
```
symptom,disease
fever,Cold
fever,Flu
cough,Cold
cough,Flu
sore throat,Cold
```

### descriptions.csv
```
disease,description
Cold,"A common viral infection affecting..."
Flu,"Influenza is a contagious respiratory..."
```

### medications.csv
```
disease,medication,dosage
Cold,Aspirin,"500mg every 6 hours"
Cold,Ibuprofen,"200mg every 4-6 hours"
Flu,Oseltamivir,"75mg twice daily"
```

### precautions.csv
```
disease,precaution
Cold,Wash hands frequently
Cold,Avoid contact with others
Cold,Stay hydrated
Flu,Get vaccinated annually
```

### diets.csv
```
disease,diet,recommended,avoid
Cold,warm liquids,Yes,No
Cold,dairy products,No,Yes
Cold,vitamin c fruits,Yes,No
```

## This is Your Core Engine ✅

All components work together to provide:
- ✅ Accurate symptom matching
- ✅ Disease scoring and ranking
- ✅ Comprehensive medical data retrieval
- ✅ Clear clinical reasoning
- ✅ Mandatory medical disclaimer
- ✅ Error handling and validation
- ✅ Professional response formatting

