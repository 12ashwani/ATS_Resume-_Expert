from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

# Configure the Google Generative AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_KEY_API"))

def get_gemini_response(input, pdf_content, prompt):
    """
    Generates a response from the Gemini AI model based on the input, PDF content, and a prompt.
    
    Parameters:
        input (str): The text input, typically the job description.
        pdf_content (list): A list containing the PDF content, converted to base64-encoded images.
        prompt (str): The specific prompt or question to guide the AI model's response.
        
    Returns:
        str: The AI-generated response text.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Converts the uploaded PDF file to a base64-encoded JPEG image, suitable for AI processing.
    
    Parameters:
        uploaded_file (UploadedFile): The PDF file uploaded by the user via Streamlit.
        
    Returns:
        list: A list containing a dictionary with the MIME type and base64-encoded image data.
        
    Raises:
        FileNotFoundError: If no file is uploaded.
    """
    if uploaded_file is not None:
        # Convert the PDF to a list of images (one per page)
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        # Get the first page of the PDF as an image
        first_page = images[0]

        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Encode the image to base64 and prepare it for the AI model
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App Configuration
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input for Job Description
input_text = st.text_area("Job Description: ", key="input")

# File uploader for the resume
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# Custom prompt input (Search bar)
custom_prompt = st.text_input("Enter a custom prompt related to the job and resume:")

# Display a message when the PDF is uploaded successfully
if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Button to trigger the resume review based on the first predefined prompt
submit1 = st.button("Tell Me About the Resume")

# Button to trigger the percentage match functionality based on the third predefined prompt
submit3 = st.button("Percentage Match")

# Predefined prompts for different analyses
input_prompt1 = """
 You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
 Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as a percentage, then keywords missing, and finally, your overall thoughts.
"""

# If the "Tell Me About the Resume" button is pressed
if submit1:
    if uploaded_file is not None:
        # Process the uploaded PDF and generate a response based on the first prompt
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.write("Please upload the resume")

# If the "Percentage Match" button is pressed
elif submit3:
    if uploaded_file is not None:
        # Process the uploaded PDF and generate a response based on the third prompt
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.write("Please upload the resume")

# If a custom prompt is entered, use that to get a response
if custom_prompt:
    if uploaded_file is not None:
        # Process the uploaded PDF and generate a response based on the custom prompt
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(custom_prompt, pdf_content, input_text)
        st.subheader("Custom Prompt Response:")
        st.write(response)
    else:
        st.write("Please upload the resume")
