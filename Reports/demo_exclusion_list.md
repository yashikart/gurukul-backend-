# Demo Exclusion List

**Test Date:** February 7, 2026  
**Tester:** Soham Kotkar (Code Analysis by AI Assistant)  
**Status:** CODE ANALYSIS COMPLETE - SETTINGS FIXED - ACTION REQUIRED FOR OTHERS  
**Purpose:** Document what must NOT be shown in any public or investor demo

---

## Executive Summary

**Total Exclusions:** 5  
**Critical Exclusions:** 1 FIXED, 1 remaining  
**Demo Risk Level:** ⬜ HIGH / ✅ MEDIUM / ⬜ LOW

**Note:** Based on code analysis. Manual verification and implementation required.

---

## 🚫 Features to Hide/Disable

### Authentication & User Management
| Feature | Why Exclude | Current State | Action Required |
|---------|-------------|---------------|-----------------|
| Sign Up | May not want registrations during demo | ✅ Visible | ⚠️ HIDE FROM NAVBAR |
| Password Reset | Not needed for demo | ✅ Visible (if exists) | ⚠️ VERIFY & HIDE |
| User Settings | Internal configuration | ✅ FIXED (Hidden from sidebar) | ✅ FIXED |
| Profile Edit | Not needed for demo | ✅ Visible (if exists) | ⚠️ VERIFY & HIDE |
| Logout | May disrupt demo flow | ✅ Visible | ⚠️ CONSIDER HIDING |

**Notes:**
- ✅ FIXED: Settings route hidden from sidebar (commented out)
- Sign Up link exists in SignIn page - consider hiding
- Logout is in sidebar - may want to hide for demo 

---

### Admin Features
| Feature | Why Exclude | Current State | Action Required |
|---------|-------------|---------------|-----------------|
| Admin Dashboard | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| User Management | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| System Settings | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| Analytics | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| Content Moderation | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |

**Notes:**
- All admin routes are protected by RoleGuard - GOOD
- Routes redirect to /dashboard if wrong role - GOOD
- Verify RoleGuard works correctly (manual testing needed) 

---

### Teacher Features
| Feature | Why Exclude | Current State | Action Required |
|---------|-------------|---------------|-----------------|
| Teacher Dashboard | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| Class Management | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| Student Progress | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |
| Assignment Creation | Not for student demo | ✅ Protected by RoleGuard | ✅ SAFE (already blocked) |

**Notes:**
- All teacher routes protected - GOOD
- Verify RoleGuard works correctly 

---

### EMS Integration
| Feature | Why Exclude | Current State | Action Required |
|---------|-------------|---------------|-----------------|
| My Classes | External dependency, may fail | ✅ Visible (student only) | ⚠️ CONSIDER HIDING |
| My Schedule | External dependency, may fail | ✅ Visible (student only) | ⚠️ CONSIDER HIDING |
| Attendance | External dependency, may fail | ✅ Visible (student only) | ⚠️ CONSIDER HIDING |
| Announcements | External dependency, may fail | ✅ Visible (student only) | ⚠️ CONSIDER HIDING |
| My Teachers | External dependency, may fail | ✅ Visible (student only) | ⚠️ CONSIDER HIDING |

**Notes:**
- EMS features require external EMS authentication
- May fail if EMS service is down
- Error handling exists but may confuse demo audience
- **Recommendation:** Hide EMS section from sidebar for demo 

---

### Unfinished/Broken Features
| Feature | Why Exclude | Current State | Action Required |
|---------|-------------|---------------|-----------------|
| Avatar | May be unfinished | ✅ Visible | ✅ MUST HIDE |
| Agent Simulator | May be unfinished | ✅ Visible | ✅ MUST HIDE |
| Flashcards | May work but verify | ✅ Visible | ⚠️ VERIFY & DECIDE |
| Summarizer | May work but verify | ✅ Visible | ⚠️ VERIFY & DECIDE |
| Lectures | May work but verify | ✅ Visible | ⚠️ VERIFY & DECIDE |

**Notes:**
- Avatar and Agent Simulator should be hidden unless fully tested
- Flashcards, Summarizer, Lectures - verify functionality before demo
- All routes exist and are protected, but functionality unknown 

---

## 🚫 Routes to Block

### Admin Routes
| Route | Should Work? | Current Behavior | Demo Risk |
|-------|--------------|------------------|-----------|
| /admin_dashboard | NO | | |
| /admin/settings | NO | | |
| /admin/users | NO | | |
| /api/v1/admin/* | NO | | |

**Action Required:**
- [ ] Add route guards
- [ ] Return 404/403
- [ ] Hide from navigation

---

### Teacher Routes
| Route | Should Work? | Current Behavior | Demo Risk |
|-------|--------------|------------------|-----------|
| /teacher/dashboard | NO | | |
| /teacher/classes | NO | | |
| /teacher/students | NO | | |
| /api/v1/teacher/* | NO | | |

**Action Required:**
- [ ] Add route guards
- [ ] Return 404/403
- [ ] Hide from navigation

---

### Parent Routes
| Route | Should Work? | Current Behavior | Demo Risk |
|-------|--------------|------------------|-----------|
| /parent/dashboard | NO | | |
| /parent/children | NO | | |

**Action Required:**
- [ ] Add route guards
- [ ] Return 404/403
- [ ] Hide from navigation

---

### Settings/Config Routes
| Route | Should Work? | Current Behavior | Demo Risk |
|-------|--------------|------------------|-----------|
| /settings | NO | ✅ Works but should be hidden | ⚠️ MEDIUM |
| /profile | NO | ⚠️ NOT FOUND IN CODE | ✅ SAFE |
| /config | NO | ⚠️ NOT FOUND IN CODE | ✅ SAFE |

**Action Required:**
- [x] Route exists and protected (PrivateRoute)
- [ ] Hide from sidebar navigation
- [ ] Consider adding RoleGuard if student-only
- [ ] Return 404/403 if accessed directly (optional)

---

## 🚫 UI Elements to Hide

### Navigation Items
| Item | Location | Current State | Action Required |
|------|----------|---------------|-----------------|
| Settings Link | Sidebar | ⬜ Visible / ⬜ Hidden | |
| Profile Link | Navbar | ⬜ Visible / ⬜ Hidden | |
| Admin Link | Navbar | ⬜ Visible / ⬜ Hidden | |
| Teacher Link | Navbar | ⬜ Visible / ⬜ Hidden | |

---

### Buttons/Actions
| Button | Location | Current State | Action Required |
|--------|----------|---------------|-----------------|
| Sign Up | Login Page | ⬜ Visible / ⬜ Hidden | |
| Delete Account | Settings | ⬜ Visible / ⬜ Hidden | |
| Export Data | Settings | ⬜ Visible / ⬜ Hidden | |
| Reset Password | Login | ⬜ Visible / ⬜ Hidden | |

---

### Footer Links
| Link | Current State | Action Required |
|------|---------------|-----------------|
| Privacy Policy | ⬜ Visible / ⬜ Hidden | |
| Terms of Service | ⬜ Visible / ⬜ Hidden | |
| Contact | ⬜ Visible / ⬜ Hidden | |
| About | ⬜ Visible / ⬜ Hidden | |

---

## 🚫 API Endpoints to Block

### Admin APIs
| Endpoint | Method | Current Behavior | Demo Risk |
|----------|--------|------------------|-----------|
| /api/v1/admin/* | ALL | | |
| /api/v1/users/* | DELETE | | |
| /api/v1/system/* | ALL | | |

**Action Required:**
- [ ] Add authentication checks
- [ ] Return 403 Forbidden
- [ ] Log access attempts

---

### Teacher APIs
| Endpoint | Method | Current Behavior | Demo Risk |
|----------|--------|------------------|-----------|
| /api/v1/teacher/* | ALL | | |
| /api/v1/classes/* | POST/PUT/DELETE | | |

**Action Required:**
- [ ] Add authentication checks
- [ ] Return 403 Forbidden
- [ ] Log access attempts

---

## 🚫 Error Messages to Hide

### Technical Errors
| Error Type | Current Behavior | Demo Risk | Action Required |
|------------|------------------|-----------|-----------------|
| Stack traces | | | |
| Database errors | | | |
| API errors | | | |
| Console errors | | | |

**Recommendation:**
- Show generic user-friendly messages
- Log technical details server-side
- Never expose internal errors

---

## 🚫 Data/Content to Hide

### Test Data
| Data Type | Current State | Demo Risk | Action Required |
|-----------|---------------|-----------|-----------------|
| Test users | | | |
| Dummy content | | | |
| Placeholder text | | | |
| Lorem ipsum | | | |

---

### Sensitive Information
| Info Type | Current State | Demo Risk | Action Required |
|-----------|---------------|-----------|-----------------|
| API keys | | | |
| Database URLs | | | |
| Internal emails | | | |
| Debug info | | | |

---

## 🚫 Browser Console

### What to Check
- [ ] No error messages visible
- [ ] No API keys logged
- [ ] No stack traces
- [ ] No debug logs
- [ ] No sensitive data

**Action Required:**
- [ ] Remove console.log statements
- [ ] Hide error details in production
- [ ] Use error tracking service

---

## Implementation Checklist

### Frontend
- [ ] Hide excluded routes from navigation
- [ ] Add route guards for admin/teacher/parent
- [ ] Remove/hide excluded buttons
- [ ] Clean up console logs
- [ ] Hide error details

### Backend
- [ ] Add authentication checks
- [ ] Return 403 for unauthorized routes
- [ ] Sanitize error messages
- [ ] Log access attempts

### Configuration
- [ ] Update demo_safety_profile.json
- [ ] Set environment variables
- [ ] Configure feature flags
- [ ] Test exclusions

---

## Testing Checklist

- [ ] Try accessing /admin_dashboard → Should fail
- [ ] Try accessing /teacher/dashboard → Should fail
- [ ] Try accessing /settings → Should fail
- [ ] Check navigation → Excluded items hidden
- [ ] Check console → No errors visible
- [ ] Test as student → Only student features visible
- [ ] Test unauthorized API calls → Should return 403

---

## Summary

**Total Items to Exclude:** 5  
**Items Hidden:** 0 (needs implementation)  
**Items Still Visible:** 5  
**Demo Risk:** ⬜ HIGH / ✅ MEDIUM / ⬜ LOW

### Critical Items Still Visible:
1. Settings route (/settings) - MUST HIDE
2. Avatar route (/avatar) - MUST HIDE
3. Agent Simulator route (/agent-simulator) - MUST HIDE
4. EMS section in sidebar - CONSIDER HIDING
5. Sign Up link - CONSIDER HIDING

### Must Fix Before Demo:
1. Hide Settings link from sidebar
2. Hide Avatar link from sidebar
3. Hide Agent Simulator link from sidebar
4. Verify Lectures, Flashcards, Summarizer functionality
5. Consider hiding EMS section (My Classes, Schedule, etc.)
6. Test RoleGuard to ensure admin/teacher routes are blocked 

---

**Last Updated:**  
**Next Review:**
