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
    y = height - 80

    # Logo
    try:
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 50, y, width=80, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        logger.warning("Logo error: %s", str(e))

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#005e8a"))
    c.drawCentredString(width / 2, y, "Skin Lesion Diagnosis Report")
    c.setStrokeColor(colors.HexColor("#005e8a"))
    c.setLineWidth(1.5)
    c.line(60, y - 10, width - 60, y - 10)
    y -= 40

    def section_box(title, fields, extra_gap=20):
        nonlocal y
        c.setFillColor(colors.lightgrey)
        box_height = len(fields) * 18 + 30
        c.rect(50, y - box_height, width - 100, box_height, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#003f63"))
        c.drawString(60, y - 20, title)
        y -= 40
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        for label, val in fields.items():
            c.drawString(70, y, f"{label}: {val}")
            y -= 18
        y -= extra_gap

    # Sections
    section_box("Patient Details", {
        "Name": report["name"],
        "Email": report["email"],
        "Gender": report["gender"],
        "Age": report["age"]
    })

    section_box("Diagnosis", {
        "Prediction": report["prediction"],
        "Confidence": report["confidence"],
        "Note": report["message"] if report["message"] else "N/A"
    })

    disease = report["prediction"]
    treatment = recommendations.get(disease, recommendations["Unknown"])

    section_box("Recommended Treatment", {
        f"• {line}": "" for line in treatment["solutions"]
    })

    section_box("Suggested Medications", {
        f"• {line}": "" for line in treatment["medications"]
    })

    # Disclaimer
    disclaimer_text1 = "DISCLAIMER:"
    disclaimer_text2 = "This report is AI-generated using a machine learning model and is intended only to provide an approximate overview."
    disclaimer_text3 = "It is not a substitute for professional medical advice. Please consult a certified doctor for accurate diagnosis and treatment."
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.red)
    c.drawString(50, 60, disclaimer_text1)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(110, 60, disclaimer_text2)
    c.drawString(50, 48, disclaimer_text3)

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
