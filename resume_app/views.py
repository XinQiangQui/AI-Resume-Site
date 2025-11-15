import fitz
import docx
import re
import json
import os
from dotenv import load_dotenv
load_dotenv()

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

resume_api_key = os.getenv("OPENAI_API_KEY")


def extract_text(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    else:
        return ValueError("Unsupported file type. Please upload PDF or DOCX")


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\x00', '')
    return text.strip()


@login_required
def analyze_resume(request):
    if request.method == "POST":
        file = request.FILES["resume"]
        text = clean_text(extract_text(file))

        # Call AI API
        prompt = f"""
        You are an expert career advisor and ATS (Applicant Tracking System) consultant.
        Analyze the following resume and respond in strict JSON format with these keys:
        overall_summary, key_strengths, weaknesses, suggestions, ats_tips, skills

        Resume Content:
        {text[:8000]}
        """

        client = OpenAI(api_key=resume_api_key)
        message: list[ChatCompletionUserMessageParam] = [
            ChatCompletionUserMessageParam(role="user", content=prompt)
        ]
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=message
        )

        try:
            feedback = json.loads(response.choices[0].message.content)
        except:
            feedback = {
                "overall_summary": response.choices[0].message.content,
                "key_strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "ats_tips": [],
                "skills": []
            }

        return render(request, "resume_app/result.html", {"feedback": feedback})
    return render(request, "resume_app/upload.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/')
    else:
        form = UserCreationForm()
    return render(request, "resume_app/register.html", {"form": form})