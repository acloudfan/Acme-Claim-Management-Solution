/**
 * Chatbot API client
 */
import { getApiClient } from './client';

/**
 * Send a message to the chatbot
 * @param {number} customerId - Customer ID
 * @param {string} message - User's message
 * @param {string|null} sessionId - Session ID (null for new session)
 * @param {object|null} context - Page context (claim data, damages, etc.)
 * @returns {Promise<{session_id: string, response: string, tool_calls: array}>}
 */
export const sendChatMessage = async (customerId, message, sessionId = null, context = null) => {
  try {
    const apiClient = getApiClient();
    const response = await apiClient.post('/chatbot/customer/message', {
      customer_id: customerId,
      message,
      session_id: sessionId,
      context
    });

    return response.data;
  } catch (error) {
    console.error('Chatbot API error:', error);
    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      'Failed to send message'
    );
  }
};

/**
 * Delete a chat session
 * @param {string} sessionId - Session ID
 * @returns {Promise<{success: boolean}>}
 */
export const deleteChatSession = async (sessionId) => {
  try {
    const apiClient = getApiClient();
    const response = await apiClient.delete(`/chatbot/session/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Delete session error:', error);
    throw new Error(
      error.response?.data?.detail ||
      'Failed to delete session'
    );
  }
};

/**
 * Get chat session history
 * @param {string} sessionId - Session ID
 * @returns {Promise<{session_id: string, message_count: number, history: array}>}
 */
export const getChatHistory = async (sessionId) => {
  try {
    const apiClient = getApiClient();
    const response = await apiClient.get(`/chatbot/session/${sessionId}/history`);
    return response.data;
  } catch (error) {
    console.error('Get history error:', error);
    throw new Error(
      error.response?.data?.detail ||
      'Failed to get chat history'
    );
  }
};

/**
 * Get chatbot statistics (admin)
 * @returns {Promise<{active_sessions: number, status: string}>}
 */
export const getChatbotStats = async () => {
  try {
    const apiClient = getApiClient();
    const response = await apiClient.get('/chatbot/stats');
    return response.data;
  } catch (error) {
    console.error('Get stats error:', error);
    throw new Error('Failed to get chatbot stats');
  }
};
