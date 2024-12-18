import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Regression coefficients (as provided)
COEFFICIENTS = {
    'v1age01': 0.8310039, 'male': -1.63956, 'black': -1.673291, 'married': -2.825288,
    'diabts02': -2.289035, 'sbp3': -1.305727, 'cursmk01': -2.011954, 'cig2': -1.501812,
    'cr_high': -3.541667, 'clvh01': -2.295403, 'abnormal_abi': -1.638849, 'plaque03': -1.094031,
    'low_plt': -1.479228, 'prevhf01': -1.531617, 'prvchd05': -3.172856, 'stroke': -2.141647,
    'act3': -1.061541, 'insurance': -1.171212, 'p_afat3': -0.6661506
}
STANDARD_ERRORS = {
    'v1age01': 0.02, 'male': 0.10, 'black': 0.12, 'married': 0.15,
    'diabts02': 0.20, 'sbp3': 0.18, 'cursmk01': 0.19, 'cig2': 0.21,
    'cr_high': 0.25, 'clvh01': 0.22, 'abnormal_abi': 0.20, 'plaque03': 0.18,
    'low_plt': 0.19, 'prevhf01': 0.22, 'prvchd05': 0.30, 'stroke': 0.25,
    'act3': 0.15, 'insurance': 0.18, 'p_afat3': 0.10
}
INTERCEPT = 34.58353

# Yes/No question labels
YES_NO_QUESTIONS = {
    'male': "Are you a man?",
    'black': "Are you Black?",
    'married': "Are you married?",  # Reversed direction
    'act3': "Do you do less than 1 hour of physical activity a week?",
    'insurance': "Do you have insurance coverage?",  # Reversed direction
    'p_afat3': "Do you eat a lot of animal products?",
    'diabts02': "Do you have diabetes?",
    'sbp3': "Is your blood pressure elevated?",
    'cursmk01': "Do you currently smoke?",
    'cig2': "Have you smoked for over ten years?",
    'cr_high': "Do you have kidney failure?",
    'stroke': "Have you ever had a stroke?",
    'clvh01': "Do you have a history of left ventricular hypertrophy?",
    'abnormal_abi': "Do you have peripheral vascular disease?",
    'plaque03': "Do you have plaque buildup in your arteries?",
    'low_plt': "Do you have a low platelet count?",
    'prevhf01': "Do you have a history of heart failure?",
    'prvchd05': "Have you had a heart attack or an operation to open up your heart's arteries?"
}

# Prediction function with confidence intervals
def predict_with_ci(inputs, z_value=1.96):
    """Calculate the predicted ageD and its confidence interval."""
    # Calculate the prediction
    prediction = INTERCEPT + sum(COEFFICIENTS[var] * inputs.get(var, 0) for var in COEFFICIENTS)
    
    # Calculate the variance of the prediction
    variance = sum((inputs.get(var, 0) ** 2) * (STANDARD_ERRORS[var] ** 2) for var in COEFFICIENTS)
    std_error = variance ** 0.5  # Standard error
    
    # Calculate confidence intervals
    lower_bound = prediction - z_value * std_error
    upper_bound = prediction + z_value * std_error
    
    return round(prediction, 1), round(lower_bound, 1), round(upper_bound, 1)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Lifespan Prediction Calculator</title>
</head>
<body>
    <h1>Lifespan Prediction Calculator</h1>
    <h2>If you are unsure of any response, answer no</h2>
    <h3>No data is saved from this website</h3>
    <form method="POST">
        <label for="v1age01">What is your age?</label>
        <input type="number" step="any" name="v1age01" required><br><br>

        {% for var, question in questions.items() %}
        <label for="{{ var }}">{{ question }}</label>
        <select name="{{ var }}">
            <option value="1">Yes</option>
            <option value="0" selected>No</option>
        </select><br><br>
        {% endfor %}
        
        <button type="submit">Predict</button>
    </form>
    {% if prediction is not none %}
        <h2>Predicted age at time of death: {{ prediction }}</h2>
        <h3>95% Confidence Interval: [{{ lower_bound }} - {{ upper_bound }}]</h3>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def calculator():
    prediction, lower_bound, upper_bound = None, None, None
    if request.method == 'POST':
        try:
            # Parse input values (age as float, yes/no as integers, default to 0 if missing)
            inputs = {'v1age01': float(request.form.get('v1age01', 0))}
            for var in YES_NO_QUESTIONS.keys():
                value = int(request.form.get(var, 0))
                # Reverse direction for married and insurance variables
                if var in ['married', 'insurance']:
                    value = 1 - value  # Flip 1 to 0 and 0 to 1
                inputs[var] = value
            
            # Call predict_with_ci with inputs
            prediction, lower_bound, upper_bound = predict_with_ci(inputs)
        except ValueError as e:
            print("Error:", e)  # Print the error to debug
            prediction = "Error: Please enter valid inputs."
    return render_template_string(
        HTML_TEMPLATE,
        prediction=prediction,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        questions=YES_NO_QUESTIONS
    )

if __name__ == '__main__':
    # Use PORT from environment variables or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
