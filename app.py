"""
Clinical Decision-Support Chatbot - Flask Application
Loads medical datasets and provides API endpoints for symptom analysis
"""

import os
import ast
import pandas as pd
from flask import Flask, render_template, request, jsonify

# ============================================
# Initialize Flask App
# ============================================

app = Flask(__name__)

# ============================================
# MANDATORY DISCLAIMER (Always Include)
# ============================================

DISCLAIMER = """
⚠️ MEDICAL DISCLAIMER

This information is for clinical decision support only and is NOT a final medical diagnosis. 

The results provided by this chatbot are based on symptom matching algorithms and should NEVER be used as a substitute for professional medical advice, diagnosis, or treatment.

IMPORTANT:
• Always consult with a qualified healthcare professional for proper diagnosis
• In case of medical emergency, call emergency services immediately
• Self-diagnosis based on this tool may delay critical treatment
• Individual medical conditions require personalized clinical assessment
• This tool does not account for patient-specific factors, medical history, or comorbidities

By using this tool, you acknowledge that you understand these limitations and assume full responsibility for any decisions made based on its output.
"""

# ============================================
# Load Datasets at Startup
# ============================================

def load_datasets():
    """
    Load all medical datasets from CSV files at application startup.
    Datasets are loaded once and stored as global variables for efficient access.
    
    Returns:
        dict: Dictionary containing all loaded dataframes
    """
    try:
        datasets = {}
        data_dir = 'data'
        
        # Define all dataset files to load
        dataset_files = {
            'symptoms': 'symptoms.csv',
            'medications': 'medications.csv',
            'precautions': 'precautions.csv',
            'descriptions': 'descriptions.csv',
            'diet': 'diets.csv'
        }
        
        print("=" * 50)
        print("Loading Medical Datasets...")
        print("=" * 50)
        
        for dataset_name, filename in dataset_files.items():
            filepath = os.path.join(data_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    datasets[dataset_name] = df
                    print(f"✅ {dataset_name.upper()}: Loaded ({len(df)} rows, {len(df.columns)} columns)")
                except Exception as e:
                    print(f"⚠️  {dataset_name.upper()}: Error loading - {str(e)}")
                    datasets[dataset_name] = pd.DataFrame()
            else:
                print(f"⚠️  {dataset_name.upper()}: File not found at {filepath}")
                datasets[dataset_name] = pd.DataFrame()
        
        print("=" * 50)
        print("Dataset Loading Complete")
        print("=" * 50)
        
        return datasets
    
    except Exception as e:
        print(f"❌ Critical Error Loading Datasets: {str(e)}")
        # Return empty dataframes as fallback
        return {
            'symptoms': pd.DataFrame(),
            'medications': pd.DataFrame(),
            'precautions': pd.DataFrame(),
            'descriptions': pd.DataFrame(),
            'diet': pd.DataFrame()
        }


# Load datasets at application startup (runs once when app starts)
print("\n🚀 Application Starting...\n")
DATASETS = load_datasets()

# Store individual dataframe references for easy access in routes
symptoms_df = DATASETS['symptoms']
medications_df = DATASETS['medications']
precautions_df = DATASETS['precautions']
descriptions_df = DATASETS['descriptions']
diet_df = DATASETS['diet']

# ============================================
# Symptom Matching and Disease Mapping Logic
# ============================================

def extract_symptoms(user_text):
    """
    Extract known symptoms from user's free-text input.
    
    Converts user input to lowercase and matches against known symptoms
    in the symptoms dataset. Returns a list of matched symptoms.
    
    Args:
        user_text (str): User's free-text symptom description
        
    Returns:
        list: List of matched symptoms found in the user's text
    """
    if symptoms_df.empty:
        print("⚠️  Symptoms dataset is empty")
        return []
    
    try:
        # Convert user input to lowercase for case-insensitive matching
        user_text_lower = user_text.lower()
        
        # Get all unique symptoms from dataset
        # The CSV has columns: Disease, Symptom_1, Symptom_2, Symptom_3, Symptom_4
        symptom_columns = [col for col in symptoms_df.columns if col.startswith('Symptom')]
        
        # Collect all unique symptoms from symptom columns
        known_symptoms = set()
        for col in symptom_columns:
            symptoms_list = symptoms_df[col].dropna().str.lower().str.strip().unique()
            known_symptoms.update(symptoms_list)
        
        known_symptoms = list(known_symptoms)
        
        print(f"\n🔍 Extracting Symptoms...")
        print(f"User input: {user_text}")
        print(f"Known symptoms in database: {len(known_symptoms)}")
        
        # Find symptoms present in user's text
        matched_symptoms = []
        for symptom in known_symptoms:
            if symptom and symptom in user_text_lower:
                matched_symptoms.append(symptom)
        
        print(f"✅ Matched symptoms: {matched_symptoms}")
        print(f"Total matches: {len(matched_symptoms)}")
        
        return matched_symptoms
    
    except Exception as e:
        print(f"❌ Error in extract_symptoms: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def match_diseases(matched_symptoms):
    """
    Map matched symptoms to diseases based on symptom-disease relationships.
    
    Scores diseases by counting how many of the matched symptoms are
    associated with each disease. Higher scores indicate more symptom overlap.
    
    Args:
        matched_symptoms (list): List of symptoms to match
        
    Returns:
        dict: Dictionary with disease names as keys and symptom count as values
    """
    if symptoms_df.empty or not matched_symptoms:
        print("⚠️  No symptoms to match or symptoms dataset is empty")
        return {}
    
    try:
        disease_scores = {}
        
        print(f"\n🔗 Mapping Symptoms to Diseases...")
        print(f"Processing {len(matched_symptoms)} matched symptoms")
        
        # Get symptom columns
        symptom_columns = [col for col in symptoms_df.columns if col.startswith('Symptom')]
        
        for symptom in matched_symptoms:
            # Find all UNIQUE diseases that have this symptom
            matching_diseases = set()  # Use set to avoid duplicates
            
            for idx, row in symptoms_df.iterrows():
                row_symptoms = []
                for col in symptom_columns:
                    symptom_val = row[col]
                    if symptom_val and isinstance(symptom_val, str):
                        row_symptoms.append(symptom_val.lower().strip())
                
                if symptom in row_symptoms:
                    matching_diseases.add(row['Disease'])  # Add to set (no duplicates)
            
            print(f"  Symptom '{symptom}' → {len(matching_diseases)} disease(s)")
            
            # Increment score for each unique disease
            for disease in matching_diseases:
                if disease not in disease_scores:
                    disease_scores[disease] = 0
                disease_scores[disease] += 1
        
        # Sort diseases by score (highest first)
        sorted_diseases = dict(
            sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        )
        
        print(f"\n📊 Disease Scores (by matched symptom count):")
        for disease, score in sorted_diseases.items():
            print(f"  {disease}: {score} matched symptom(s)")
        
        return sorted_diseases
    
    except Exception as e:
        print(f"❌ Error in match_diseases: {str(e)}")
        return {}


def rank_diseases(disease_scores):
    """
    Rank diseases by symptom overlap and return top 1-3 results.
    
    Sorts diseases in descending order by symptom count (score).
    Returns only the top 3 diseases with highest symptom overlap.
    
    Args:
        disease_scores (dict): Dictionary with disease names as keys and 
                              symptom counts as values
    
    Returns:
        list: List of tuples (disease_name, symptom_count) for top 3 diseases
    """
    if not disease_scores:
        return []
    
    try:
        # Sort diseases by symptom count (value) in descending order
        ranked = sorted(
            disease_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        print(f"\n🎯 Ranking Diseases...")
        print(f"Total diseases matched: {len(ranked)}")
        print(f"Top 3 diseases:")
        
        # Return only top 3
        top_3 = ranked[:3]
        
        for rank, (disease, score) in enumerate(top_3, 1):
            print(f"  {rank}. {disease} ({score} symptoms)")
        
        return top_3
    
    except Exception as e:
        print(f"❌ Error in rank_diseases: {str(e)}")
        return []


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
    try:
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
    
    except Exception as e:
        print(f"❌ Error generating reasoning: {str(e)}")
        return f"Analysis indicates possible {disease}"



def get_disease_data(disease):
    """
    Fetch all medical data for a disease from loaded datasets.
    
    Simple, direct approach to retrieve description, medications, and diet
    recommendations for a given disease from the CSV datasets.
    
    Args:
        disease (str): Name of the disease to fetch data for
    
    Returns:
        dict: Dictionary containing:
            - description: List of description strings
            - medications: List of medication names
            - diet: List of diet recommendations
    """
    try:
        data = {
            'description': [],
            'medications': [],
            'diet': []
        }
        
        # Fetch description from descriptions_df
        if not descriptions_df.empty:
            desc = descriptions_df[
                descriptions_df['Disease'].str.lower() == disease.lower()
            ]['Description'].values.tolist()
            data['description'] = desc
        
        # Fetch medications from medications_df
        if not medications_df.empty:
            meds = medications_df[
                medications_df['Disease'].str.lower() == disease.lower()
            ]['Medication'].values.tolist()
            data['medications'] = meds
        
        # Fetch diet from diet_df
        if not diet_df.empty:
            diets = diet_df[
                diet_df['Disease'].str.lower() == disease.lower()
            ]['Diet'].values.tolist()
            data['diet'] = diets
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {disease}: {str(e)}")
        return {
            'description': [],
            'medications': [],
            'diet': []
        }


def parse_string_list(string_value):
    """
    Parse string representation of a list into an actual Python list.
    Handles formats like "['item1', 'item2']" or "['item1']"
    
    Args:
        string_value (str): String representation of a list
        
    Returns:
        list: Parsed list, or empty list if parsing fails
    """
    if not string_value or not isinstance(string_value, str):
        return []
    
    try:
        parsed = ast.literal_eval(string_value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed]
        return []
    except (ValueError, SyntaxError):
        return []


def get_disease_details(disease_name):
    """
    
    Fetches description, medications, precautions, and diet recommendations
    for the given disease from the loaded datasets.
    
    Args:
        disease_name (str): Name of the disease
        
    Returns:
        dict: Dictionary containing disease details (description, medications, 
              precautions, diet)
    """
    details = {
        'description': 'No description available',
        'medications': [],
        'precautions': [],
        'diet': {'recommended': [], 'avoid': []}
    }
    
    try:
        # Get disease description - Column is 'Disease' and 'Description' (capital)
        if not descriptions_df.empty:
            desc_row = descriptions_df[
                descriptions_df['Disease'].str.lower() == disease_name.lower()
            ]
            if not desc_row.empty:
                details['description'] = desc_row.iloc[0]['Description']
                print(f"  ✅ Description found for {disease_name}")
        
        # Get medications - Column is 'Medication' (capital M)
        if not medications_df.empty:
            med_rows = medications_df[
                medications_df['Disease'].str.lower() == disease_name.lower()
            ]
            if not med_rows.empty:
                medications = []
                for _, row in med_rows.iterrows():
                    # Parse the Medication column which contains string list representation
                    med_value = row.get('Medication', '[]')
                    parsed_meds = parse_string_list(med_value)
                    
                    # Create structured medication objects
                    for med_name in parsed_meds:
                        med = {
                            'name': med_name,
                            'dosage': 'As prescribed by healthcare provider'
                        }
                        medications.append(med)
                
                details['medications'] = medications
                print(f"  ✅ {len(medications)} medication(s) found")
        
        # Get precautions - Column is 'Precaution' (capital)
        if not precautions_df.empty:
            prec_rows = precautions_df[
                precautions_df['Disease'].str.lower() == disease_name.lower()
            ]
            if not prec_rows.empty:
                precautions = prec_rows['Precaution'].tolist()
                details['precautions'] = precautions
                print(f"  ✅ {len(precautions)} precaution(s) found")
        
        # Get diet recommendations - Column is 'Diet' and contains string list representation
        if not diet_df.empty:
            diet_rows = diet_df[
                diet_df['Disease'].str.lower() == disease_name.lower()
            ]
            if not diet_rows.empty:
                recommended = []
                avoid = []
                
                # Parse the Diet column which contains string list representation
                for _, row in diet_rows.iterrows():
                    diet_value = row.get('Diet', '[]')
                    parsed_diets = parse_string_list(diet_value)
                    recommended.extend(parsed_diets)
                
                details['diet'] = {
                    'recommended': recommended,
                    'avoid': avoid
                }
                print(f"  ✅ Diet recommendations found ({len(recommended)} items)")
        
        return details
    
    except Exception as e:
        print(f"  ❌ Error getting details for {disease_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return details



@app.route('/')
def index():
    """
    Render the main application page (index.html)
    """
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint to analyze patient symptoms using symptom matching and disease ranking.
    
    Workflow:
    1. Extract known symptoms from user's free-text input
    2. Validate minimum symptom threshold (at least 2 symptoms required)
    3. Match symptoms to diseases and score by symptom overlap
    4. Rank diseases and return top 1-3 results
    5. Retrieve detailed disease information (medications, precautions, diet)
    6. Return comprehensive analysis results
    
    Expected JSON payload:
    {
        "symptoms": "fever, cough, sore throat"
    }
    
    Returns:
        JSON response with predicted diseases, medications, precautions, and diet
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False,
                "disclaimer": DISCLAIMER
            }), 400
        
        symptoms_text = data.get('symptoms', '').strip()
        
        # Validate symptoms input
        if not symptoms_text:
            return jsonify({
                "error": "Symptoms field is required and cannot be empty",
                "success": False,
                "disclaimer": DISCLAIMER
            }), 400
        
        print(f"\n{'='*60}")
        print(f"📋 ANALYSIS REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"User Input: {symptoms_text}\n")
        
        # STEP 1: Extract symptoms from free-text input
        matched_symptoms = extract_symptoms(symptoms_text)
        
        # STEP 2: Validate minimum symptom threshold
        MIN_SYMPTOMS = 1  # Require at least 1 known symptom
        if len(matched_symptoms) < MIN_SYMPTOMS:
            print(f"\n⚠️  Insufficient symptoms detected")
            print(f"Required: {MIN_SYMPTOMS}, Found: {len(matched_symptoms)}")
            
            return jsonify({
                "success": False,
                "error": f"Insufficient symptoms. Please provide at least {MIN_SYMPTOMS} known medical symptom(s). You entered: {symptoms_text}",
                "received_symptoms": symptoms_text,
                "matched_symptoms": matched_symptoms,
                "diseases": [],
                "reasoning": f"Analysis requires at least {MIN_SYMPTOMS} known symptom(s) to proceed.",
                "description": "Unable to analyze - insufficient symptom data",
                "medications": [],
                "precautions": [],
                "diet": {"recommended": [], "avoid": []},
                "disclaimer": DISCLAIMER
            }), 400
        
        print(f"✅ Symptom validation passed ({len(matched_symptoms)} symptoms found)\n")
        
        # STEP 3: Match symptoms to diseases and score
        disease_scores = match_diseases(matched_symptoms)
        
        if not disease_scores:
            print("\n⚠️  No diseases matched to symptoms")
            return jsonify({
                "success": False,
                "error": "No diseases could be matched to the provided symptoms.",
                "received_symptoms": symptoms_text,
                "matched_symptoms": matched_symptoms,
                "diseases": [],
                "reasoning": "While symptoms were recognized, no disease associations exist in the database.",
                "description": "Analysis incomplete - no disease mapping available",
                "medications": [],
                "precautions": [],
                "diet": {"recommended": [], "avoid": []},
                "disclaimer": DISCLAIMER
            }), 400
        
        # STEP 4: Rank diseases and get top 1-3
        top_diseases_ranked = rank_diseases(disease_scores)
        
        if not top_diseases_ranked:
            return jsonify({
                "success": False,
                "error": "Unable to rank diseases.",
                "received_symptoms": symptoms_text,
                "matched_symptoms": matched_symptoms,
                "diseases": [],
                "reasoning": "Disease ranking failed.",
                "description": "Analysis incomplete - ranking error",
                "medications": [],
                "precautions": [],
                "diet": {"recommended": [], "avoid": []},
                "disclaimer": DISCLAIMER
            }), 500
        
        # STEP 5: Build disease list with confidence scores and retrieve details
        diseases_list = []
        diseases_details = {}
        
        print(f"\n🏥 Retrieving Disease Details...")
        
        for rank, (disease, score) in enumerate(top_diseases_ranked, 1):
            # Calculate confidence as a percentage of matched symptoms found
            # Score = number of matched symptoms associated with this disease
            # Confidence = (matched symptom count for this disease) / (total matched symptoms)
            # This gives us a value between 0 and 1
            confidence = score / len(matched_symptoms) if matched_symptoms else 0
            
            # Cap confidence at 1.0 (shouldn't exceed all matched symptoms)
            confidence = min(confidence, 1.0)
            
            diseases_list.append({
                'rank': rank,
                'name': disease,
                'confidence': round(confidence, 2),
                'symptom_count': score
            })
            
            # Get detailed information for this disease
            # Option 1: Using get_disease_details() (more detailed with precautions)
            details = get_disease_details(disease)
            
            # Option 2: Using get_disease_data() (simpler, direct approach)
            # simple_data = get_disease_data(disease)
            # Returns: {'description': [...], 'medications': [...], 'diet': [...]}
            
            diseases_details[disease] = details
        
        # Use top disease for reasoning and description
        top_disease = diseases_list[0]['name'] if diseases_list else None
        top_details = diseases_details.get(top_disease, {})
        
        # Generate reasoning using the reasoning generator function
        top_score = diseases_list[0]['symptom_count'] if diseases_list else 0
        reasoning = generate_reasoning(matched_symptoms, top_disease, top_score)
        
        # Add additional context if multiple diseases found
        if len(diseases_list) > 1:
            other_diseases = [f"{d['name']} ({d['symptom_count']} symptom(s))" for d in diseases_list[1:]]
            reasoning += f" Other possible conditions include: {', '.join(other_diseases)}."
        
        reasoning += " Please consult a qualified healthcare professional for proper diagnosis and treatment."
        
        # Collect all unique medications and precautions from top diseases only
        all_medications = []
        all_precautions = []
        all_diets = {'recommended': set(), 'avoid': set()}
        
        for disease, score in top_diseases_ranked:
            details = diseases_details.get(disease, {})
            all_medications.extend(details.get('medications', []))
            all_precautions.extend(details.get('precautions', []))
            
            diet = details.get('diet', {})
            if diet.get('recommended'):
                all_diets['recommended'].update(diet['recommended'])
            if diet.get('avoid'):
                all_diets['avoid'].update(diet['avoid'])
        
        # Remove duplicates while preserving order
        seen_meds = set()
        unique_meds = []
        for med in all_medications:
            med_key = med.get('name', '')
            if med_key not in seen_meds:
                seen_meds.add(med_key)
                unique_meds.append(med)
        
        response = {
            "success": True,
            "received_symptoms": symptoms_text,
            "matched_symptoms": matched_symptoms,
            "diseases": diseases_list,
            "reasoning": reasoning,
            "description": top_details.get('description', 'No description available'),
            "medications": unique_meds,
            "precautions": list(dict.fromkeys(all_precautions)),  # Remove duplicates
            "diet": {
                'recommended': list(all_diets['recommended']),
                'avoid': list(all_diets['avoid'])
            },
            "disclaimer": DISCLAIMER
        }
        
        print(f"\n{'='*60}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Top diseases identified: {len(diseases_list)}")
        print(f"Medications recommended: {len(unique_meds)}")
        print(f"Precautions: {len(all_precautions)}")
        print(f"\n")
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"❌ Error in predict route: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False,
            "disclaimer": DISCLAIMER
        }), 500


@app.route('/api/datasets', methods=['GET'])
def get_datasets_info():
    """
    Debug endpoint to check loaded datasets status.
    Returns information about each loaded dataset.
    """
    return jsonify({
        "symptoms": {
            "rows": len(symptoms_df),
            "columns": list(symptoms_df.columns) if not symptoms_df.empty else []
        },
        "medications": {
            "rows": len(medications_df),
            "columns": list(medications_df.columns) if not medications_df.empty else []
        },
        "precautions": {
            "rows": len(precautions_df),
            "columns": list(precautions_df.columns) if not precautions_df.empty else []
        },
        "descriptions": {
            "rows": len(descriptions_df),
            "columns": list(descriptions_df.columns) if not descriptions_df.empty else []
        },
        "diet": {
            "rows": len(diet_df),
            "columns": list(diet_df.columns) if not diet_df.empty else []
        },
        "disclaimer": DISCLAIMER
    }), 200


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - endpoint not found"""
    return jsonify({
        "error": "Endpoint not found",
        "status": 404,
        "disclaimer": DISCLAIMER
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors - internal server error"""
    return jsonify({
        "error": "Internal server error",
        "status": 500,
        "disclaimer": DISCLAIMER
    }), 500


# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🏥 Clinical Decision-Support Chatbot")
    print("=" * 50)
    print("Server starting on http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    
    app.run(debug=True)
