// Context Manager for PRANA-G
// Handles session and lesson context establishment

class ContextManager {
  constructor() {
    // Use local backend in development, production URL in production
    this.apiBaseUrl = (import.meta.env.DEV || typeof window === 'undefined') 
      ? 'http://localhost:3000' 
      : (import.meta.env.VITE_API_URL || 'http://localhost:3000');
  }

  // Set session context after login
  setSessionContext(sessionData) {
    if (sessionData?.session_id) {
      localStorage.setItem('session_id', sessionData.session_id);
      console.log('[ContextManager] Session context set:', sessionData.session_id);
      return true;
    }
    return false;
  }

  // Set lesson context when entering lesson
  setLessonContext(lessonId) {
    if (lessonId) {
      sessionStorage.setItem('current_lesson_id', lessonId);
      console.log('[ContextManager] Lesson context set:', lessonId);
      return true;
    }
    return false;
  }

  // Get current context for PRANA
  getCurrentContext() {
    return {
      user_id: this.getUserId(),
      session_id: localStorage.getItem('session_id'),
      lesson_id: sessionStorage.getItem('current_lesson_id')
    };
  }

  // Helper to get user ID from auth context
  getUserId() {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        // Decode JWT to extract user info if needed
        // For now, we'll assume user ID is available through auth context
        return null; // Will be provided by AuthContext
      }
    } catch (e) {
      console.warn('[ContextManager] Error getting user ID:', e);
    }
    return null;
  }

  // Create a new lesson in the backend
  async createLesson(title, subject, topic, content) {
    try {
      console.log('[ContextManager] Creating lesson with:', { title, subject, topic });
      
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.error('[ContextManager] No authentication token available');
        throw new Error('No authentication token available');
      }

      console.log('[ContextManager] Making API call to:', `${this.apiBaseUrl}/api/v1/lesson/`);
      
      const response = await fetch(`${this.apiBaseUrl}/api/v1/lesson/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: title,
          subject: subject,
          topic: topic,
          content: content
        })
      });

      console.log('[ContextManager] API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[ContextManager] API response data:', data);
        
        if (data.lesson_id) {
          this.setLessonContext(data.lesson_id);
          console.log('[ContextManager] New lesson created and context set:', data.lesson_id);
          return data;
        } else {
          console.error('[ContextManager] API returned success but no lesson_id in response');
          return null;
        }
      } else {
        const errorText = await response.text();
        console.error('[ContextManager] Failed to create lesson. Status:', response.status, 'Body:', errorText);
        return null;
      }
    } catch (error) {
      console.error('[ContextManager] Error creating lesson:', error);
      return null;
    }
  }

  // Fetch lesson context from backend
  async fetchLessonContext(lessonId) {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${this.apiBaseUrl}/api/v1/lesson/${lessonId}/context`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.lesson_id) {
          this.setLessonContext(data.lesson_id);
          return data;
        }
      } else {
        console.error('[ContextManager] Failed to fetch lesson context:', response.status);
      }
    } catch (error) {
      console.error('[ContextManager] Error fetching lesson context:', error);
    }
    return null;
  }
}

// Singleton instance
const contextManager = new ContextManager();
export default contextManager;

// Export individual functions for direct use
export const setSessionContext = (sessionData) => contextManager.setSessionContext(sessionData);
export const setLessonContext = (lessonId) => contextManager.setLessonContext(lessonId);
export const getCurrentContext = () => contextManager.getCurrentContext();
export const fetchLessonContext = (lessonId) => contextManager.fetchLessonContext(lessonId);
export const createLesson = (title, subject, topic, content) => contextManager.createLesson(title, subject, topic, content);