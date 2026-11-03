import os
import json
import time
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List
from pathlib import Path

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Groq API key error!!!")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

# STEP-1: TAKE THE JOB DESCRIPTION AND CREATE A SCHEMA AND GENERATE THE JSON USING GROQ
job_description="""
Description
Do you want to solve real customer problems through innovative technology? Do you enjoy working on scalable services in a collaborative team environment? Do you want to see your code directly impact millions of customers worldwide?

At Amazon, we hire the best minds in technology to innovate and build on behalf of our customers. Customer obsession is part of our company DNA, which has made us one of the world's most beloved brands.

Our Software Development Engineers (SDEs) use modern technology to solve complex problems while seeing their work's impact first-hand. The challenges SDEs solve at Amazon are meaningful and influence millions of customers, sellers, and products globally. We seek individuals passionate about creating new products, features, and services while managing ambiguity in an environment where development cycles are measured in weeks, not years.

At Amazon, we believe in ownership at every level. As an SDE-I, you'll own the entire lifecycle of your code - from design through deployment and ongoing operations. This ownership mindset, combined with our commitment to operational excellence, ensures we deliver the highest quality solutions for our customers.

We're looking for curious minds who think big and want to define tomorrow's technology. At Amazon, you'll grow into the high-impact engineer you know you can be, supported by a culture of learning and mentorship. Every day brings exciting new challenges and opportunities for personal growth.
Key job responsibilities
• Collaborate and communicate effectively with experienced cross-disciplinary Amazonians to design, build, and operate innovative products and services that delight our customers, while participating in technical discussions to drive solutions forward.
• Design and develop scalable solutions using cloud-native architectures and microservices in a large distributed computing environment.
• Participate in code reviews and contribute to technical documentation.
• Build and maintain resilient distributed systems that are scalable, fault-tolerant, and cost-effective.
• Leverage and contribute to the development of GenAI and AI-powered tools to enhance development productivity while staying current with emerging technologies.
• Write clean, maintainable code following best practices and design patterns.
• Work in an agile environment practicing CI/CD principles while participating in operational responsibilities including on-call duties.
• Demonstrate operational excellence through monitoring, troubleshooting, and resolving production issues.
Basic Qualifications
- Experience with at least one general-purpose programming language such as Java, Python, C++, C#, Go, Rust, or TypeScript
- Experience with data structure implementation, basic algorithm development, and/or object-oriented design principles
- Currently has, or is in the process of obtaining a bachelor’s degree in Computer Science, Computer Engineering, Data Science, Information Systems, or related STEM fields
- Must be 18 years of age of older
Preferred Qualifications
- Experience from previous technical internship(s) or demonstrated project experience
- Experience with one or more of the following: AI tools for development productivity, Cloud platforms (preferably AWS), Database systems (SQL and NoSQL), Contributing to open-source projects, Version control systems, Debugging and troubleshooting complex systems
- Demonstrated ability to learn and adapt to new technologies quickly
- Basic understanding of software development lifecycle (SDLC)
- Strong problem-solving and analytical skills
- Excellent written and verbal communication skills
"""

class JobD(BaseModel):
    role: str
    required_skills: List[str]
    preffered_skills: List[str]
    minimum_yoe: float | None
    responsibilities: List[str]
    educational_requirements: List[str]

jobd_schema=JobD.model_json_schema()

system_prompt=f"""
You are an expert HR assistant and job description analysis specialist.

Your task is to analyze the provided job description and extract relevant information into a structured format.

### Job Description
{job_description}

### Extraction Guidelines

1. **Job Information**
   - Extract the job title, company name, location, and employment type when available.
   - Identify the primary role and its responsibilities.

2. **Required Skills**
   - Extract technical skills, programming languages, frameworks, tools, platforms, and technologies explicitly required for the role.
   - Identify soft skills and interpersonal abilities mentioned as requirements.
   - Distinguish mandatory skills from preferred or optional skills whenever the schema supports it.

3. **Experience Requirements**
   - Extract minimum and maximum years of experience if explicitly mentioned.
   - Identify relevant experience requirements, such as experience with specific technologies or domains.
   - If minimum experience is not specified, return null.
   - Do not assume experience requirements from the seniority or title of the position.

4. **Educational Qualifications**
   - Extract required degrees, fields of study, certifications, and other qualifications.
   - Distinguish mandatory qualifications from preferred qualifications when possible.

5. **Responsibilities**
   - Extract the primary duties and responsibilities associated with the position.
   - Keep descriptions concise while preserving their original meaning.

6. **Additional Requirements**
   - Identify other relevant requirements, including domain knowledge, communication skills, work arrangements, and eligibility conditions.
   - Include only information supported by the job description.

### Data Extraction Rules

1. Interpret information based on meaning, not just section headings.
2. Handle different formats, including paragraphs, bullet points, tables, and unconventional headings.
3. Avoid duplicate skills and responsibilities.
4. Preserve the original meaning of the job requirements.
5. Do not confuse preferred qualifications with mandatory requirements.
6. Do not infer missing information or fabricate details.
7. If an individual field is unavailable, return null.
8. If a list has no available information, return an empty list (`[]`).
9. If minimum experience is not explicitly stated, return null.
10. If the job description contains conflicting or ambiguous information, do not guess.

### Output Requirements

- Return ONLY valid JSON.
- Populate the provided schema with actual information extracted from the job description.
- Do not return the JSON Schema definition itself.
- Do not include schema metadata such as `properties`, `title`, `type`, or `definitions` as output fields unless explicitly required by the schema.
- Follow the schema's field names, structure, and data types exactly.
- Do not add fields that are not defined in the schema.
- Do not include Markdown, code fences, comments, or explanations.

### Expected JSON Schema
{jobd_schema}
"""

user_prompt=f"""
analyze the job description: {job_description}
"""

message_system={
    "role": "system",
    "content": system_prompt
}

message_user={
    "role": "user",
    "content": user_prompt
}

messages=[message_system, message_user]

response_format={
    "type":"json_object"
}

response_jd=client.chat.completions.create(messages=messages, response_format=response_format, model=model)
answer_jd=response_jd.choices[0].message.content
raw_json=answer_jd

# converting the answer_jd into JSON
job_data=json.loads(raw_json)
json_jd=JobD(**job_data)

# print(json_jd)


# STEP-2: DEFINING THE RESUME STRUCTURE
class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    description: str | None = None
    duration: str | None = None
    skills_used: List[str] = []         # if no skill, it will take empty list

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    skills: List[str] = []
    experiences: List[Experience] = []
    projects: List[str] = []
    education: List[str] = []
    certifications: List[str] = []

    total_yoe: float | None = None

resume_schema=Resume.model_json_schema()



# STEP-3: WRITING THE FUNCTION TO READ THE RESUME
from pypdf import PdfReader
from docx import Document

def read_pdf(file_path):
    reader=PdfReader(file_path)
    text=""
    for page in reader.pages:
        page_text=page.extract_text()
        if page_text:
            text+=page_text+"\n"
    return text

def read_docx(file_path):
    reader=Document(file_path)
    text=""
    for para in reader.paragraphs:
        if para.text.strip():
            text+=para.text+"\n"

    for table in reader.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text+= cell.text+"\n"
    return text

def read_resume(file_path):
    if file_path.suffix.lower()==".pdf":
        return read_pdf(file_path)
    elif file_path.suffix.lower()==".docx":
        return read_docx(file_path)
    return None


# STEP-4: WRITING THE FUNCTION TO PARSE THE RESUME AND CALCULATE THE RESUME SCORE
class MatchResult(BaseModel):
    score: float
    details: dict

def parse_resume(resume_text):
    system_prompt=f"""
    You are an expert resume parsing assistant. Your task is to extract structured information from resumes accurately and consistently.

    ### Extraction Guidelines

    1. **Understand context, not just headings:** Identify information based on its meaning, even when section headings vary. For example, "Work History", "Employment", "Professional Experience", and "Internships" all represent experience-related information.

    2. **Extract information comprehensively:**
    - Personal details: Extract the candidate's name, email, phone number, location, and LinkedIn/GitHub/portfolio URLs when available.
    - Education: Extract degree, institution, field of study, graduation year, and other available details.
    - Experience: Include full-time roles, part-time roles, internships, and relevant employment history.
    - Skills: Identify technical and soft skills mentioned anywhere in the resume, including skills demonstrated through experience and projects.
    - Projects: Extract project names, descriptions, technologies used, and other relevant details.
    - Certifications: Extract certification names, issuing organizations, and dates when available.

    3. **Preserve accuracy:** Extract only information explicitly stated or clearly supported by the resume. Do not assume, infer, or fabricate missing details.

    4. **Handle missing information:**
    - Return `null` for unavailable individual fields.
    - Return an empty list (`[]`) when no relevant items are found.
    - Do not use placeholder strings such as "N/A", "Not provided", or "Unknown".

    5. **Preserve original meaning:** Keep descriptions concise without changing their meaning. Preserve dates, names, technologies, qualifications, and other important details as accurately as possible.

    6. **Avoid duplication:** Do not duplicate the same skill, experience, project, or certification across multiple entries unless the schema explicitly requires it.

    7. **Handle varied formats:** Resumes may contain inconsistent formatting, abbreviations, unconventional section names, or information presented in paragraphs and bullet points. Interpret them using context.

    ### Output Requirements

    - Return ONLY valid JSON.
    - Follow the provided schema exactly.
    - Do not add additional fields.
    - Do not include Markdown, code fences, explanations, or comments.
    - Ensure all values match the expected data types.
    - Never omit required schema fields.

    ### JSON Schema

    {resume_schema}
    """
    user_prompt=f"""
    Parse the following resume {resume_text}
    """
    message_system={
        "role": "system",
        "content": system_prompt
    }
    message_user={
        "role": "user",
        "content": user_prompt
    }
    messages=[message_system, message_user]
    response_format={
        "type": "json_object"
    }
    response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    raw_output=response.choices[0].message.content
    data=json.loads(raw_output)
    resume=Resume(**data)       # creating object of Resume class
    return resume


def final_score(job, resume):
    match_schema=MatchResult.model_json_schema()
    prompt=f"""
    You are an experienced HR recruiter and technical talent assessment specialist.

    Your task is to evaluate how well a candidate's resume matches a given job description. Analyze the candidate's qualifications objectively and provide an evidence-based assessment.

    ### Job Description
    {job.model_dump_json(indent=2)}

    ### Candidate Resume
    {resume.model_dump_json(indent=2)}

    ### Evaluation Criteria

    Evaluate the candidate using the following criteria:

    1. **Skills Match (40%)**
    - Identify skills required by the job description.
    - Compare them with skills explicitly mentioned or demonstrated in the resume.
    - Identify matching skills and important skills that are missing or not demonstrated.
    - Consider equivalent technologies and terminology where appropriate.

    2. **Experience Match (25%)**
    - Compare the candidate's experience with the required experience.
    - Consider relevant internships, professional experience, and projects where appropriate.
    - Evaluate the relevance of previous responsibilities, not just the number of years.
    - Clearly state whether the experience requirement is met, partially met, or not met.

    3. **Education and Qualifications (15%)**
    - Compare the candidate's educational background and qualifications with the job requirements.
    - Identify whether the required degree, field of study, or certifications are satisfied.

    4. **Projects and Relevant Work (20%)**
    - Evaluate projects and practical work relevant to the job.
    - Consider technologies used, implementation details, and demonstrated problem-solving abilities.
    - Give credit for relevant practical experience even when it comes from academic or personal projects.

    ### Scoring Guidelines

    Calculate an overall match percentage from 0 to 100 using the following weighted criteria:

    - Skills Match: 40%
    - Experience Match: 25%
    - Education and Qualifications: 15%
    - Projects and Relevant Work: 20%

    Rules:
    - Base the score only on information available in the resume and job description.
    - Do not award points for skills, qualifications, or experience that are not supported by the resume.
    - Do not automatically assign zero points when information is unavailable; distinguish missing evidence from confirmed lack of qualifications.
    - Do not penalize equivalent skills simply because different terminology is used.
    - Treat internships and projects as relevant evidence, but do not automatically consider them equivalent to full-time professional experience.
    - Avoid inflated scores and arbitrary judgments.
    - The final score must be an integer between 0 and 100.

    ### Output Requirements

    Return ONLY valid JSON matching the following schema:

    {match_schema}

    Additional rules:
    1. Include the candidate's name exactly as extracted from the resume. Use null if unavailable.
    2. List relevant matching skills.
    3. List important skills required by the job but not demonstrated in the resume.
    4. Clearly report whether the experience requirement is met, partially met, not met, or cannot be determined.
    5. Provide the overall match percentage.
    6. Give a short, objective verdict explaining the candidate's suitability.
    7. Keep the response concise, professional, and easy to understand.
    8. Do not invent information or include unsupported claims.
    9. Follow the schema exactly. Do not add extra fields, explanations, or Markdown.
    """
    message={
        "role": "user",
        "content": prompt
    }
    messages=[message]
    response_format={
        "type": "json_object"
    }
    response=client.chat.completions.create(model=model, response_format=response_format, messages=messages)
    raw_output=response.choices[0].message.content
    data=json.loads(raw_output)
    result=MatchResult(**data)
    return result


# reading files from a folder
resume_folder=Path("resumes")
all_results=[]

for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        continue

    print("\nProcessing:", file_path.name)

    resume_text=read_resume(file_path)
    # making the LLM calls
    parsed_resume=parse_resume(resume_text)
    time.sleep(5)
    final_result=final_score(json_jd, parsed_resume)
    time.sleep(5)

    print("\nResume score: ", final_result.score)

    all_results.append(
        {
            "name": parsed_resume.name,
            "score": final_result.score,
            "details": final_result.details
        }
    )


all_results.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)

# getting top 2 and worst 2 candidates
top_2=all_results[:2]
worst_2=all_results[-2:]

print("TOP 2 CANDIDATES")
for candidate in top_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )

    print(candidate["details"])

print("LOWEST 2 CANDIDATES")
for candidate in worst_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )
    print(candidate["details"])