// Thin wrapper for EMS → unified PRANA core.
// Initializes PRANA with EMS system/role context at app startup.
// Reads dynamic context from window.EMSUserContext.

import '../../prana-core/prana_packet_builder.js';

if (typeof window !== 'undefined' && window.PRANA && typeof window.PRANA.init === 'function') {
  try {
    const pranaInstance = window.PRANA.init({
      system_type: 'ems',
      role: 'employee',
      user_id: null, // Will be provided dynamically via context provider
      session_id: null,
      lesson_id: null,
      bucket_endpoint: 'http://localhost:8000/bucket/prana/ingest',
    });

    // Register context provider that reads from EMS window globals
    if (pranaInstance && pranaInstance.packetBuilder) {
      pranaInstance.packetBuilder.registerContextProvider({
        getContext: () => {
          const userCtx = window.EMSUserContext || null;
          // Get session_id from context or sessionStorage
          const sessionId = userCtx?.session_id || sessionStorage.getItem('session_id') || null;
          // Get lesson_id from context or sessionStorage
          const lessonId = userCtx?.currentLessonId || sessionStorage.getItem('current_lesson_id') || null;

          return {
            user_id: userCtx?.id ?? null,
            session_id: sessionId,
            lesson_id: lessonId,
          };
        },
      });
    }

    console.log('[PRANA-E] Unified PRANA core initialized');
  } catch (e) {
    console.error('[PRANA-E] PRANA.init failed:', e);
  }
}

