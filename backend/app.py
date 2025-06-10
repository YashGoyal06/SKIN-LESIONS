from flask import Flask, render_template, request, redirect, url_for, session, send_file
import tensorflow as tf
import numpy as np
from PIL import Image
import pickle
import io
import os
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = "e3f6f40bb8b2471b9f07c4025d845be9"

MODEL_PATH = "skin_lesion_model.h5"
HISTORY_PATH = "training_history.pkl"
PLOT_PATH = "/tmp/static/training_plot.png"
LOGO_PATH = "static/logo.jpg"
IMG_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.30

label_map = {
    0: "Melanoma",
    1: "Melanocytic nevus",
    2: "Basal cell carcinoma",
    3: "Actinic keratosis",
    4: "Benign keratosis",
    5: "Dermatofibroma",
    6: "Vascular lesion",
    7: "Squamous cell carcinoma"
}

recommendations = {
    "Melanoma": {
        "solutions": [
            "Consult a dermatologist immediately.",
            "Surgical removal is typically required.",
            "Regular follow-up and screening for metastasis."
        ],
        "medications": ["Interferon alfa-2b", "Vemurafenib", "Dacarbazine"]
    },
    "Melanocytic nevus": {
        "solutions": [
            "Usually benign and requires no treatment.",
            "Monitor for any change in shape or color."
        ],
        "medications": ["No medication necessary unless changes occur."]
    },
    "Basal cell carcinoma": {
        "solutions": [
            "Surgical excision or Mohs surgery.",
            "Topical treatments if superficial.",
            "Radiation in select cases."
        ],
        "medications": ["Imiquimod cream", "Fluorouracil cream", "Vismodegib"]
    },
    "Actinic keratosis": {
        "solutions": [
            "Cryotherapy or topical treatments.",
            "Avoid prolonged sun exposure.",
            "Use of sunscreen regularly."
        ],
        "medications": ["Fluorouracil", "Imiquimod", "Diclofenac gel"]
    },
    "Benign keratosis": {
        "solutions": [
            "Generally harmless and often left untreated.",
            "Can be removed for cosmetic reasons."
        ],
        "medications": ["No medication required unless infected."]
    },
    "Dermatofibroma": {
        "solutions": [
            "Benign skin growth, no treatment needed.",
            "Surgical removal if painful or for cosmetic reasons."
        ],
        "medications": ["No medication needed."]
    },
    "Vascular lesion": {
        "solutions": [
            "Treatment depends on type (e.g., hemangioma).",
            "Laser therapy is commonly used.",
            "Observation if no complications."
        ],
        "medications": ["Beta-blockers (e.g., propranolol for hemangioma)"]
    },
    "Squamous cell carcinoma": {
        "solutions": [
            "Surgical removal is standard.",
            "Follow-up for recurrence or metastasis.",
            "Avoid sun exposure and use sunscreen."
        ],
        "medications": ["Fluorouracil", "Cisplatin", "Imiquimod"]
    },
    "Low confidence": {
        "solutions": [
            "The image is not confidently classified.",
            "Please upload a clearer image or consult a doctor."
        ],
        "medications": ["Not available due to low confidence."]
    },
    "Unknown": {
        "solutions": ["No specific guidance available."],
        "medications": ["N/A"]
    }
}

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Model
try:
    logger.info("Loading model from %s", MODEL_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    logger.error("Failed to load model: %s", str(e))
    raise

# Plot training history
if os.path.exists(HISTORY_PATH):
    try:
        with open(HISTORY_PATH, "rb") as f:
            history_dict = pickle.load(f)
        if "accuracy" in history_dict and "val_accuracy" in history_dict:
            os.makedirs("/tmp/static", exist_ok=True)
            plt.plot(history_dict['accuracy'], label='Train Accuracy')
            plt.plot(history_dict['val_accuracy'], label='Val Accuracy')
            plt.xlabel('Epochs')
            plt.ylabel('Accuracy')
            plt.title('Training History')
            plt.legend()
            plt.grid(True)
            plt.savefig(PLOT_PATH)
            plt.close()
            logger.info("Training plot saved at %s", PLOT_PATH)
    except Exception as e:
        logger.error("Training history load error: %s", str(e))

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = tf.keras.utils.img_to_array(image)
    return np.expand_dims(image_array, axis=0) / 255.0

def generate_pdf(report, filepath):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 60

    # Background
    c.setFillColor(colors.Color(0.98, 0.98, 0.99, alpha=1))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Header background
    c.setFillColor(colors.Color(0.94, 0.96, 0.98, alpha=1))
    c.rect(0, height-120, width, 120, fill=1, stroke=0)

    # Logo from root directory - square JPG format
    try:
        logo_path = "./logo.jpg"  # Changed to JPG format
        if os.path.exists(logo_path):
            # Square logo container - no circular mask since logo is square
            c.setFillColor(colors.white)
            c.rect(65, y-25, 50, 50, fill=1, stroke=1)  # Square container
            c.setStrokeColor(colors.Color(0.7, 0.7, 0.7, alpha=1))
            c.setLineWidth(1)
            c.rect(65, y-25, 50, 50, fill=0, stroke=1)  # Square border
            c.drawImage(logo_path, 67, y-23, width=46, height=46, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        logger.warning("Logo error: %s", str(e))

    # Professional title
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.Color(0.2, 0.2, 0.2, alpha=1))
    c.drawCentredString(width / 2, y + 5, "Medical Diagnosis Report")
    
    # Subtitle
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.Color(0.5, 0.5, 0.5, alpha=1))
    c.drawCentredString(width / 2, y - 15, "Dermatological Analysis")
    
    # Professional line
    c.setStrokeColor(colors.Color(0.8, 0.8, 0.8, alpha=1))
    c.setLineWidth(1)
    c.line(80, y - 35, width - 80, y - 35)
    
    y -= 80

    def professional_section_box(title, fields, extra_gap=20):
        nonlocal y
        
        box_height = len(fields) * 20 + 40
        
        # Main box with subtle shadow
        c.setFillColor(colors.Color(0.96, 0.96, 0.96, alpha=0.3))
        c.rect(42, y - box_height - 2, width - 84, box_height, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.rect(40, y - box_height, width - 80, box_height, fill=1, stroke=1)
        c.setStrokeColor(colors.Color(0.9, 0.9, 0.9, alpha=1))
        
        # Title bar
        c.setFillColor(colors.Color(0.95, 0.95, 0.95, alpha=1))
        c.rect(40, y - 30, width - 80, 30, fill=1, stroke=0)
        
        # Title
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.Color(0.3, 0.3, 0.3, alpha=1))
        c.drawString(55, y - 20, title)
        
        y -= 45
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.Color(0.2, 0.2, 0.2, alpha=1))
        
        for label, val in fields.items():
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.Color(0.4, 0.4, 0.4, alpha=1))
            c.drawString(55, y, f"{label}:")
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.Color(0.2, 0.2, 0.2, alpha=1))
            c.drawString(150, y, str(val))
            y -= 20
        
        y -= extra_gap

    # Sections
    professional_section_box("Patient Information", {
        "Name": report["name"],
        "Email": report["email"],
        "Gender": report["gender"],
        "Age": f"{report['age']} years"
    })

    confidence_val = float(report["confidence"].replace('%', ''))
    confidence_text = f"{report['confidence']} ({'High' if confidence_val > 85 else 'Moderate' if confidence_val > 70 else 'Low'} Confidence)"
    
    professional_section_box("Diagnostic Results", {
        "Condition": report["prediction"],
        "Confidence": confidence_text,
        "Notes": report["message"] if report["message"] else "No additional notes"
    })

    disease = report["prediction"]
    treatment = recommendations.get(disease, recommendations["Unknown"])

    professional_section_box("Treatment Recommendations", {
        f"{i+1}. {line}": "" for i, line in enumerate(treatment["solutions"])
    })

    professional_section_box("Medication Guidelines", {
        f"{i+1}. {line}": "" for i, line in enumerate(treatment["medications"])
    })

    # Professional disclaimer
    c.setFillColor(colors.Color(0.98, 0.98, 0.98, alpha=1))
    c.rect(40, 40, width - 80, 70, fill=1, stroke=1)
    c.setStrokeColor(colors.Color(0.9, 0.9, 0.9, alpha=1))
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.Color(0.4, 0.4, 0.4, alpha=1))
    c.drawString(50, 95, "Medical Disclaimer")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.Color(0.3, 0.3, 0.3, alpha=1))
    disclaimer_lines = [
        "This report is generated using AI technology for preliminary assessment purposes only.",
        "Results should not replace professional medical consultation and diagnosis.",
        "Please consult a qualified healthcare provider for comprehensive medical evaluation."
    ]
    
    for i, line in enumerate(disclaimer_lines):
        c.drawString(50, 80 - (i * 10), line)

    c.save()


@app.route("/form")
def form():
    return render_template("form.html", history_plot="/training_plot.png")

@app.route("/training_plot.png")
def training_plot():
    return send_file(PLOT_PATH, mimetype="image/png")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "image" not in request.files:
            raise ValueError("No image uploaded.")
        image = request.files["image"].read()
        img_array = preprocess_image(image)
        prediction = model.predict(img_array)[0]
        predicted_index = int(np.argmax(prediction))
        confidence = float(prediction[predicted_index])
        label = label_map.get(predicted_index, "Unknown") if confidence >= CONFIDENCE_THRESHOLD else "Low confidence"
        msg = "⚠ This image is not confidently recognized. Please upload a clearer image." if confidence < CONFIDENCE_THRESHOLD else ""

        report = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "gender": request.form.get("gender"),
            "age": request.form.get("age"),
            "prediction": label,
            "confidence": f"{confidence * 100:.2f}%",
            "message": msg
        }
        session["report"] = report
        return redirect(url_for("result"))
    except Exception as e:
        return render_template("form.html", history_plot="/training_plot.png", result={
            "prediction": "Error", "confidence": "N/A", "message": str(e)
        })

@app.route("/result")
def result():
    report = session.get("report", {})
    return render_template("result.html", **report)

@app.route("/download-report")
def download_report():
    report = session.get("report", {})
    if not report:
        return redirect(url_for("form"))
    os.makedirs("/tmp/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filepath = f"/tmp/reports/report_{timestamp}.pdf"
    generate_pdf(report, filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
