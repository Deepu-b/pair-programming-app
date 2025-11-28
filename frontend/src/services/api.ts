import axios from 'axios';

// Ensure this matches your FastAPI backend URL
const API_URL = 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createRoom = async () => {
  const response = await api.post('/rooms');
  return response.data; // returns { room_id: "..." }
};

export const getSuggestion = async (code: string, cursorPosition: number) => {
  const response = await api.post('/autocomplete', { 
    code, 
    cursorPosition, 
    language: "python" 
  });
  return response.data; // returns { suggestion: "..." }
};