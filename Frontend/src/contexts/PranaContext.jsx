import { createContext, useContext, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getPacketBuilder } from '../utils/prana_packet_builder';
import { getCurrentContext } from '../utils/contextManager';

const PranaContext = createContext();

// Context provider that supplies user context to PRANA
export const PranaProvider = ({ children }) => {
  const { user, loading } = useAuth();
  const packetBuilder = getPacketBuilder();

  // Provide context to PRANA packet builder
  const getContext = () => {
    // Use context manager to get current context
    const currentCtx = getCurrentContext();
    
    if (!user || loading) {
      return {
        user_id: null,
        session_id: currentCtx.session_id || null,
        lesson_id: currentCtx.lesson_id || null
      };
    }

    return {
      user_id: user.id || currentCtx.user_id || null,
      session_id: currentCtx.session_id || localStorage.getItem('session_id') || null,
      lesson_id: currentCtx.lesson_id || sessionStorage.getItem('current_lesson_id') || null
    };
  };

  // Register context provider with packet builder when available
  useEffect(() => {
    if (packetBuilder && typeof packetBuilder.registerContextProvider === 'function') {
      packetBuilder.registerContextProvider({ getContext });
      console.log('[PRANA] Connected to AuthContext');
    }
  }, [packetBuilder, user, loading]);

  return (
    <PranaContext.Provider value={{ getContext }}>
      {children}
    </PranaContext.Provider>
  );
};

export const usePranaContext = () => {
  return useContext(PranaContext);
};