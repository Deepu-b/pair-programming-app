import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../app/store';
import { updateCode, setConnectionStatus, setSuggestion } from '../features/editorSlice';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism.css'; 
import { getSuggestion } from '../services/api';
import './Room.css'; // Import the CSS

const Room: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const { code, isConnected, suggestion } = useSelector((state: RootState) => state.editor);
  const codeRef = useRef(code); 

  const socketRef = useRef<WebSocket | null>(null);
  const typingTimeoutRef = useRef<number | null>(null);
  const isRemoteUpdate = useRef(false);
  const cursorRef = useRef<number | null>(null);

  useEffect(() => {
    codeRef.current = code;
  }, [code]);

  useEffect(() => {
    if (!roomId) return;

    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${roomId}`);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to room:', roomId);
      dispatch(setConnectionStatus(true));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'INIT' || data.type === 'CODE_UPDATE') {
           const newCode = data.payload.code;
           const oldCode = codeRef.current; 

           const textarea = document.querySelector('textarea');
           let currentCursor = 0;
           if (textarea) {
             currentCursor = textarea.selectionStart;
           }

           let diffIndex = 0;
           while (
             diffIndex < oldCode.length && 
             diffIndex < newCode.length && 
             oldCode[diffIndex] === newCode[diffIndex]
           ) {
             diffIndex++;
           }

           const lengthDelta = newCode.length - oldCode.length;
           let newCursorPosition = currentCursor;
           if (diffIndex < currentCursor) {
             newCursorPosition = Math.max(0, currentCursor + lengthDelta);
           }

           cursorRef.current = newCursorPosition;
           isRemoteUpdate.current = true;
           dispatch(updateCode(newCode));
        }
      } catch (err) {
        console.error("Failed to parse WS message", err);
      }
    };

    ws.onclose = (event) => {
      dispatch(setConnectionStatus(false));
      if (event.code === 1008) {
        alert("Room not found! Redirecting to home.");
        navigate('/');
      }
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [roomId, dispatch, navigate]);

  useEffect(() => {
    if (isRemoteUpdate.current && cursorRef.current !== null) {
      const textarea = document.querySelector('textarea');
      if (textarea) {
        textarea.setSelectionRange(cursorRef.current, cursorRef.current);
      }
      isRemoteUpdate.current = false;
    }
  }, [code]);

  const handleCodeChange = (newCode: string) => {
    isRemoteUpdate.current = false; 
    dispatch(updateCode(newCode));
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const payload = {
        type: "CODE_UPDATE",
        payload: { code: newCode }
      };
      socketRef.current.send(JSON.stringify(payload));
    }

    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    if (suggestion) dispatch(setSuggestion(null));

    typingTimeoutRef.current = window.setTimeout(async () => {
        const result = await getSuggestion(newCode, newCode.length);
        dispatch(setSuggestion(result.suggestion));
    }, 600);
  };

  const handleDisconnect = () => {
    if (socketRef.current) {
      socketRef.current.close();
    }
    navigate('/');
  };

  return (
    <div className="room-container">
      <div className="room-header">
        <h2 className="room-title">
            Room: {roomId} <br/>
            <span className={`status-indicator ${isConnected ? 'status-live' : 'status-disconnected'}`}>
                ● {isConnected ? 'Live' : 'Disconnected'}
            </span>
        </h2>
        
        <button onClick={handleDisconnect} className="btn-leave">
            Leave Room
        </button>
      </div>
      
      <div className="editor-wrapper">
        <Editor
          value={code}
          onValueChange={handleCodeChange}
          highlight={(code: string) => highlight(code, languages.python, 'python')}
          padding={20}
          className="code-editor-font" // Pass class to library
          style={{
            fontFamily: '"Fira code", "Fira Mono", monospace',
            fontSize: 16,
            minHeight: '400px',
            color: '#eee', 
          }}
        />
        {suggestion && (
            <div className="ai-suggestion-box">
                <strong>AI Suggestion:</strong>
                <pre className="ai-suggestion-text">{suggestion}</pre>
            </div>
        )}
      </div>
    </div>
  );
};

export default Room;