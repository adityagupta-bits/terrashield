import uvicorn

if __name__ == "__main__":
    print("=================================================================")
    print("  TERRA SHIELD - AI-Powered Environmental Monitoring Network")
    print("  Smart India Hackathon 2026 | Problem Statement: SIH26178")
    print("  Starting API & Real-Time Engine on http://localhost:8000")
    print("=================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    