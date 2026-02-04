# Demo Risk Notes

## ✅ SAFE TO DEMO

| Feature      | Path          | Notes |
|--------------|---------------|-------|
| Registration | /register     | Works |
| Login        | /login        | Works |
| Home         | /home         | Works |
| Subjects     | /subjects     | Works |
| Lectures     | /lectures/:id | Works |
| Chat         | /chatbot      | Uses Groq, TTS works |
| Quiz         | /test         | AI generates questions |

## ❌ DO NOT TOUCH

| Feature           | Path        | Reason              |
|-------------------|-------------|---------------------|
| Summarizer        | Any         | DISABLED - will 404 |
| Admin Dashboard   | /admin/*    | Incomplete          |
| Teacher Dashboard | /teacher/*  | Incomplete          |
| Flashcards        | /flashcards | Unstable            |
| Settings          | /settings   | UI only, no backend |

## Demo Script (5 minutes)

```
1. Open frontend
2. Register new account
3. Login
4. Click Subjects → Select one
5. View a lecture
6. Open Chat → Ask "Explain photosynthesis"
7. Click speaker icon → Voice plays
8. Go to Quiz → Generate → Answer → See score
9. Done
```

## If Things Break

| Problem         | Action                   |
|-----------------|--------------------------|
| Spinner forever | Refresh, wait 10s        |
| 404 error       | Navigate to /home        |
| Login fails     | Use backup account       |
| Console errors  | Ignore (PRANA, harmless) |

## Backup Accounts

| Email            | Password |
|------------------|----------|
| demo@gurukul.com | demo123  |
| test@gurukul.com | test123  |

## Pre-Demo Checklist

```
[ ] 30 min before: curl backend /health
[ ] 5 min before: Login once to warm up
[ ] Use incognito browser
[ ] Don't open dev tools during demo
```

