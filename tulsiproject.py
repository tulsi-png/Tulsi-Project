import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile

# --- CONFIGURE GEMINI ---
genai.configure(api_key="AIzaSyCtAJLOQjqQOnWf0A9O33Nwmh7KkWebelk")  # Replace with your actual key
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PDF Generator ---
def generate_pdf(meal_plan, shopping_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Weekly Meal Plan\n", align="C")

    pdf.set_font("Arial", size=10)
    for day, meals in meal_plan.items():
        pdf.multi_cell(0, 10, f"{day}\n{meals}\n")

    pdf.set_font("Arial", 'B', size=12)
    pdf.multi_cell(0, 10, "\nShopping List\n", align="C")

    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, shopping_list)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Meal Plan Generator", layout="centered")
st.title("🥗 Weekly Meal Plan Generator")

with st.form("meal_form"):
    dietary_pref = st.selectbox("Choose your dietary preference:", ["Vegan", "Vegetarian", "Keto", "Paleo", "Balanced"])
    goal = st.selectbox("Choose your goal:", ["Weight Loss", "Muscle Gain", "Maintenance"])
    allergies = st.text_input("Any food allergies? (comma-separated)")
    meals_per_day = st.slider("Meals per day:", 2, 6, 3)
    submit = st.form_submit_button("Generate Meal Plan")

if submit:
    with st.spinner("Generating your personalized meal plan..."):
        prompt = f"""
        Create a 7-day meal plan for a user with the following details:
        - Dietary Preference: {dietary_pref}
        - Goal: {goal}
        - Meals per day: {meals_per_day}
        - Allergies: {allergies if allergies else 'None'}

        For each day, provide meals with:
        1. Name of the dish
        2. Brief recipe or preparation instructions

        Then, provide a consolidated shopping list for all 7 days at the end.
        """

        try:
            response = model.generate_content(prompt)
            full_text = response.text

            # Split meal plan and shopping list
            if "Shopping List" in full_text:
                plan_text, shopping_list = full_text.split("Shopping List", 1)
            else:
                plan_text, shopping_list = full_text, "No shopping list found."

            # Format plan by days
            days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
            meal_plan = {}
            for day in days:
                section = plan_text.split(day)[1] if day in plan_text else "No info."
                next_day = next((d for d in days if d in section and d != day), None)
                content = section.split(next_day)[0] if next_day else section
                meal_plan[day] = content.strip()

            # Display meal plan
            st.success("✅ Meal Plan Generated!")
            for day, content in meal_plan.items():
                with st.expander(day):
                    st.markdown(content)

            with st.expander("🛒 Shopping List"):
                st.markdown(shopping_list.strip())

            # Download as PDF
            pdf_path = generate_pdf(meal_plan, shopping_list)
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="📥 Download Meal Plan (PDF)",
                    data=file,
                    file_name="weekly_meal_plan.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Optional: Regenerate button
if st.button("🔄 Regenerate Meal Plan"):
    st.experimental_rerun()
