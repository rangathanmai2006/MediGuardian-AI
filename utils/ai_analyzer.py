import os
import time
import json
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_report(report_text):
    prompt = f"""
You are MediGuardian AI, an intelligent healthcare assistant.

Analyze the following medical report.

Medical Report:
{report_text}



Detailed Exercise Guide:

Generate exactly 5 exercises suitable for the patient's medical condition.

Write the entire response in clear and simple English and in a very detailed explanation.

Do not use markdown.

Return ONLY valid JSON.

For every exercise provide:

- Exercise Name
- Duration
- Sets
- Repetitions
- Difficulty
- Benefits
- Precautions
- Step by Step Instructions
--------------------------------

High Protein Recipes

Generate exactly 5 healthy high-protein recipes suitable for the patient's medical condition.

Write the entire response in clear and simple English and give a very detailed explanation .

Do not use markdown.

Return ONLY valid JSON.
For every recipe provide:

- Recipe Name
- Protein
- Calories
- Ingredients
- Preparation Steps
- Best Time To Eat
- Benefits

The response must be suitable for Indian food habits.

Prefer homemade Indian recipes whenever possible.

Return ONLY valid JSON.

Generate a personalized report based ONLY on the uploaded report.


JSON Structure:

{{
    "report_type": "",
    "health_score": 0,
    "priority": "",
    "doctor_visit": "",
    "confidence": "",

    "summary": "",

    "key_findings": [],

    "diet_recommendations": [],

    "exercise_recommendations": [],

    "detailed_exercises": [
        {{
            "name": "",
            "duration": "",
            "sets": "",
            "reps": "",
            "difficulty": "",
            "benefits": "",
            "precautions": "",
            "steps": []
        }}
    ],

    "protein_recipes": [
        {{
            "name": "",
            "protein": "",
            "calories": "",
            "ingredients": [],
            "steps": [],
            "time": "",
            "benefits": ""
        }}
    ],

    "lifestyle_tips": [],

    "water_intake": "",

    "sleep_recommendation": "",

    "follow_up": "",

    "condition_name": "",

    "image_keywords": [],

    "video_topics": [],

    "cards":[
        {{
            "id":"",
            "title":"",
            "icon":"",
            "description":"",
            "theme":"",
            "content":{{}}
        }}
    ]
}}



Rules:

1. Detect the report type automatically.

2. Generate between 5 and 8 useful cards.

3. Every report should have DIFFERENT cards.

Examples:

Blood Report:
- Diet Plan
- Blood Sugar
- Iron Foods
- Lifestyle
- Doctor Questions

MRI:
- MRI Findings
- Brain Anatomy
- Treatment
- Recovery Tips
- Doctor Questions

Heart Report:
- ECG Findings
- Heart Healthy Diet
- Exercise
- Medicines
- Doctor Questions

Kidney Report:
- Kidney Diet
- Water Intake
- Lifestyle
- Foods to Avoid
- Doctor Questions

Liver Report:
- Liver Care
- Healthy Diet
- Lifestyle
- Medicines
- Doctor Questions

Each card MUST contain:

id
title
icon
description
theme
content

Theme should be one of:

green
blue
orange
red
purple

Use simple language.

Never diagnose.

Always say:

"This MAY indicate..."

Provide safe and practical advice.

Recommend Indian homemade food whenever appropriate.

Also provide:

Diet Recommendations:
- 5 healthy diet recommendations.

Exercise Recommendations:
- 5 safe exercise recommendations.

Lifestyle Tips:
- 5 healthy lifestyle tips.

Water Intake:
- Recommended daily water intake.

Sleep Recommendation:
- Recommended sleep duration.

Follow Up:
- Suggest whether a follow-up doctor visit or test is needed.

Condition Name:
- Mention the main health condition or body system involved.

Image Keywords:
- Provide exactly 3 medical image keywords.

Example:
Heart
Kidney
Blood Cells

Video Topics:
- Provide exactly 3 educational video topics.

Example:
Understanding Blood Test
Heart Healthy Diet
How to Manage Diabetes
Return ONLY valid JSON.
"""
    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt
            )

            text = response.text.strip()

            # Remove markdown if Gemini returns it
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()

            print("\n========== AI RESPONSE ==========\n")
            print(text)
            print("\n===============================\n")

            return json.loads(text)

        except Exception as e:

            last_error = e

            print(f"\nAttempt {attempt + 1} failed.")
            print(e)

            if attempt < 2:
                wait = (attempt + 1) * 3
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)

    raise Exception(last_error)