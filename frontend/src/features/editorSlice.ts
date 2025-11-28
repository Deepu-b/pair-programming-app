import { createSlice} from '@reduxjs/toolkit';
import type {PayloadAction } from '@reduxjs/toolkit';

interface EditorState {
  code: string;
  roomId: string | null;
  suggestion: string | null;
  isConnected: boolean;
}

const initialState: EditorState = {
  code: "# Start coding here...",
  roomId: null,
  suggestion: null,
  isConnected: false,
};

export const editorSlice = createSlice({
  name: 'editor',
  initialState,
  reducers: {
    setRoomId: (state, action: PayloadAction<string>) => {
      state.roomId = action.payload;
    },
    updateCode: (state, action: PayloadAction<string>) => {
      state.code = action.payload;
    },
    setSuggestion: (state, action: PayloadAction<string | null>) => {
      state.suggestion = action.payload;
    },
    setConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
  },
});

export const { setRoomId, updateCode, setSuggestion, setConnectionStatus } = editorSlice.actions;
export default editorSlice.reducer;