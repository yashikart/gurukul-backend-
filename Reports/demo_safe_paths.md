# Demo Safe Paths

**Test Date:** February 7, 2026  
**Tester:** Soham Kotkar (Code Analysis by AI Assistant)  
**Status:** CODE ANALYSIS COMPLETE - 9 ISSUES FIXED - MANUAL TESTING REQUIRED  
**Purpose:** Identify which user flows work reliably and can be safely demonstrated

---

## Executive Summary

**Total Safe Paths:** 5 (from code analysis)  
**Total Risky Paths:** 3 (needs verification)  
**Demo Confidence:** ⬜ High / ✅ Medium / ⬜ Low

**Note:** Based on code analysis. Manual testing required to verify actual behavior.

---

## ✅ Safe Demo Paths (Recommended)

### Path 1: Student Login → Dashboard → Subject Selection
**Confidence:** ✅ High / ⬜ Medium / ⬜ Low  
**Tested:** ⚠️ CODE ANALYSIS ONLY  
**Last Test Date:** February 7, 2026

**Steps:**
1. Navigate to homepage (/)
2. Click Sign In
3. Enter credentials
4. Land on Dashboard (/dashboard)
5. Click Subjects (/subjects)
6. Select a subject

**Success Criteria:**
- [x] Login route exists and protected
- [x] Dashboard route exists with RoleGuard
- [x] Subjects route exists
- [x] Error handling in place
- [ ] Login completes in <3s (NEEDS TESTING)
- [ ] Dashboard loads without errors (NEEDS TESTING)
- [ ] Subject list appears (NEEDS TESTING)
- [ ] No console errors (NEEDS TESTING)

**Known Issues:**
- Cold start delay possible (30-60s) on first request
- Retry logic exists to handle delays

**Demo Notes:**
- Pre-warm backend before demo
- If cold start occurs, user will see loading state (acceptable)
- Route guards verified in code 

---

### Path 2: Subject → Lesson → Chat Interaction
**Confidence:** ✅ High / ⬜ Medium / ⬜ Low  
**Tested:** ⚠️ CODE ANALYSIS ONLY  
**Last Test Date:** February 7, 2026

**Steps:**
1. Select subject (/subjects)
2. View lesson content (generated via /api/v1/learning/explore)
3. Click Chatbot (/chatbot)
4. Ask a question
5. Receive response

**Success Criteria:**
- [x] Routes exist and protected
- [x] API endpoints exist
- [x] Error handling in place
- [x] Retry logic for timeouts
- [ ] Lesson loads in <2s (NEEDS TESTING)
- [ ] Chat opens smoothly (NEEDS TESTING)
- [ ] Response arrives in <5s (NEEDS TESTING)
- [ ] No timeout errors (NEEDS TESTING)

**Known Issues:**
- Cold start delay possible
- API has retry logic (30s, 40s, 50s, 60s)
- Error messages are user-friendly

**Demo Notes:**
- Pre-warm backend
- If delay occurs, loading state is acceptable
- Chat uses /api/v1/chat endpoint (verified in code) 

---

### Path 3: Quiz Generation → Answer → Results
**Confidence:** ✅ High / ⬜ Medium / ⬜ Low  
**Tested:** ⚠️ CODE ANALYSIS ONLY  
**Last Test Date:** February 7, 2026

**Steps:**
1. Complete a lesson
2. Generate quiz (/api/v1/quiz/generate)
3. Answer questions
4. Submit (/api/v1/quiz/submit)
5. View results (/api/v1/quiz/results)

**Success Criteria:**
- [x] Routes exist (/test page)
- [x] API endpoints exist
- [x] Error handling in place
- [ ] Quiz generates in <4s (NEEDS TESTING)
- [ ] Questions render correctly (NEEDS TESTING)
- [ ] Submission works (NEEDS TESTING)
- [ ] Results display accurately (NEEDS TESTING)

**Known Issues:**
- Cold start delay possible
- Quiz generation may take longer on first request

**Demo Notes:**
- Pre-warm backend
- Have a pre-generated quiz ready as backup
- Test page route verified: /test 

---

### Path 4: Multilingual Switch (English → Hindi)
**Confidence:** ✅ High / ⬜ Medium / ⬜ Low  
**Tested:** ⚠️ CODE ANALYSIS ONLY  
**Last Test Date:** February 7, 2026

**Steps:**
1. Start in English
2. Click language selector (Navbar)
3. Select Hindi
4. Verify translation (Google Translate)
5. Test TTS in Hindi

**Success Criteria:**
- [x] Language selector exists (Navbar.jsx)
- [x] Google Translate integration exists
- [x] TTS language sync code exists (Chatbot.jsx)
- [x] Vaani TTS supports Hindi (tts.py)
- [ ] Language switches smoothly (NEEDS TESTING)
- [ ] All text translates (NEEDS TESTING)
- [ ] TTS works in Hindi (NEEDS TESTING)
- [ ] No layout breaks (NEEDS TESTING)

**Known Issues:**
- Google Translate bar hiding (recently fixed)
- TTS language sync (recently fixed)
- Translation depends on Google Translate service

**Demo Notes:**
- Test with stable internet connection
- Google Translate bar should be hidden (CSS fix in place)
- TTS should auto-sync with website language (recently implemented) 

---

### Path 5: TTS Playback (English)
**Confidence:** ✅ High / ⬜ Medium / ⬜ Low  
**Tested:** ⚠️ CODE ANALYSIS ONLY  
**Last Test Date:** February 7, 2026

**Steps:**
1. Open Chatbot (/chatbot)
2. Receive AI response
3. Click TTS button (Vaani or Google TTS)
4. Audio plays
5. Can stop/restart

**Success Criteria:**
- [x] TTS endpoints exist (/api/v1/tts/speak, /api/v1/tts/vaani)
- [x] TTS button exists in Chatbot UI
- [x] Error handling in place
- [x] Audio playback code exists
- [ ] Audio starts in <2s (NEEDS TESTING)
- [ ] Quality is clear (NEEDS TESTING)
- [ ] Controls work (NEEDS TESTING)
- [ ] No crashes (NEEDS TESTING)

**Known Issues:**
- Vaani TTS language support recently fixed
- Cold start delay possible
- Network speed affects audio loading

**Demo Notes:**
- Pre-warm backend
- Test with stable internet
- Both Google TTS and Vaani TTS available
- Vaani TTS now supports multiple languages (recently fixed) 

---

## ⚠️ Risky Paths (Use with Caution)

### Path A: EMS Integration (My Classes, Schedule, etc.)
**Risk Level:** ⬜ HIGH / ✅ MEDIUM / ⬜ LOW  
**Why Risky:**
- Requires external EMS authentication
- May fail if EMS service is down
- Additional dependency

**When It Fails:**
- EMS token expired
- EMS service unavailable
- Network issues

**Workaround:**
- Skip EMS features in demo
- Show error message gracefully (code handles this)

**Demo Recommendation:** ✅ Avoid / ⬜ Use with backup plan / ⬜ Fix first

---

### Path B: Avatar / Agent Simulator
**Risk Level:** ⬜ HIGH / ✅ MEDIUM / ⬜ LOW  
**Why Risky:**
- May be unfinished features
- Unknown functionality

**When It Fails:**
- Feature not fully implemented
- Unexpected errors

**Workaround:**
- Hide from sidebar for demo

**Demo Recommendation:** ✅ Avoid / ⬜ Use with backup plan / ⬜ Fix first

---

### Path C: Settings Page
**Risk Level:** ⬜ HIGH / ✅ MEDIUM / ⬜ LOW  
**Why Risky:**
- Should be hidden for demo
- May expose internal configuration

**When It Fails:**
- User sees settings they shouldn't
- May confuse demo audience

**Workaround:**
- Hide Settings link from sidebar

**Demo Recommendation:** ✅ Avoid / ⬜ Use with backup plan / ⬜ Fix first

---

## 🚫 Unsafe Paths (Do NOT Demo)

### Path X: Admin/Teacher/Parent Dashboards
**Why Unsafe:**
- Not part of student demo
- Protected by RoleGuard (good)
- Should not be accessible

**Failure Modes:**
- If RoleGuard fails, unauthorized access
- May expose admin features

**Impact:**
- Security risk
- Confusion in demo

**Fix Required Before Demo:** ✅ YES - Verify RoleGuard works correctly

---

### Path Y: Sign Up Flow
**Why Unsafe:**
- May not want new registrations during demo
- Could expose registration issues

**Failure Modes:**
- Registration fails
- Email verification issues
- Database errors

**Impact:**
- Bad impression
- Demo disruption

**Fix Required Before Demo:** ⚠️ CONDITIONAL - Hide if not needed

---

## Path Reliability Matrix

| Path | Tested | Success Rate | Avg Time | Demo Safe? | Notes |
|------|--------|--------------|----------|------------|-------|
| Login → Dashboard | | % | s | ⬜ YES / ⬜ NO | |
| Subject Selection | | % | s | ⬜ YES / ⬜ NO | |
| Lesson View | | % | s | ⬜ YES / ⬜ NO | |
| Chat Interaction | | % | s | ⬜ YES / ⬜ NO | |
| Quiz Generation | | % | s | ⬜ YES / ⬜ NO | |
| Quiz Submission | | % | s | ⬜ YES / ⬜ NO | |
| TTS Playback | | % | s | ⬜ YES / ⬜ NO | |
| Language Switch | | % | s | ⬜ YES / ⬜ NO | |
| EMS Integration | | % | s | ⬜ YES / ⬜ NO | |
| Teacher Dashboard | | % | s | ⬜ YES / ⬜ NO | |
| Admin Dashboard | | % | s | ⬜ YES / ⬜ NO | |

---

## Recommended Demo Flow

### Primary Demo (5-7 minutes)
1. **Start:** Login → Dashboard (30s) ✅ SAFE
2. **Core:** Subject → Lesson → Chat (2min) ✅ SAFE
3. **Feature:** Quiz Generation → Answer (2min) ✅ SAFE
4. **Polish:** TTS Playback (30s) ✅ SAFE
5. **Multilingual:** Language Switch (1min) ✅ SAFE
6. **End:** Results View (30s) ✅ SAFE

**Total Time:** ~7 minutes  
**Confidence:** ⬜ High / ✅ Medium / ⬜ Low

**Pre-Demo Checklist:**
- [ ] Pre-warm backend (5 min before)
- [ ] Test login credentials
- [ ] Verify subject data available
- [ ] Test TTS with stable connection
- [ ] Hide Settings/Avatar/Agent Simulator from sidebar
- [ ] Verify Google Translate bar is hidden

### Backup Demo (If Primary Fails)
1. 
2. 
3. 

---

## Stress Test Results

### Under Load
| Path | 1 User | 2 Users | 5 Users | Status |
|------|--------|---------|---------|--------|
| Login | | | | |
| Chat | | | | |
| Quiz | | | | |
| TTS | | | | |

### Under Slow Network
| Path | Fast 3G | Slow 3G | Offline | Status |
|------|---------|---------|---------|--------|
| Login | | | | |
| Chat | | | | |
| Quiz | | | | |
| TTS | | | | |

---

## Edge Cases Tested

| Edge Case | Path Affected | Result | Demo Safe? |
|-----------|---------------|--------|------------|
| Expired token | Login | | |
| Cold start | All | | |
| Long text | Chat | | |
| Special chars | Chat | | |
| Rapid clicks | All | | |
| Browser back | Navigation | | |

---

## Recommendations

### Must Fix Before Demo:
1. 

### Should Fix:
1. 

### Can Work Around:
1. 

---

## Sign-off

**Tester:** _________________  
**Date:** _________________  
**Demo Readiness:** ⬜ READY / ⬜ NEEDS WORK / ⬜ NOT READY
