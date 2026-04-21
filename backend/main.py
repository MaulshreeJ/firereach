from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os, smtplib
from agent import run_agent

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    icp: str
    company: str
    recipient_email: str

@app.get("/")
def health_check():
    return {"status": "OutreachAI API running"}

@app.get("/test-smtp")
def test_smtp():
    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 587)))
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.quit()
        return {"status": "ok", "message": "SMTP login successful ✅"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test-hunter")
def test_hunter(company: str = "servicenow"):
    from tools.email_finder import find_email_for_company
    email = find_email_for_company(company)
    return {"company": company, "found_email": email}

@app.post("/run-agent")
def run_agent_endpoint(request: AgentRequest):
    result = run_agent(
        icp=request.icp,
        company=request.company,
        recipient_email=request.recipient_email
    )
    return result
