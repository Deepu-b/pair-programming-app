import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createRoom } from '../services/api';
import './Home.css'; // Import the CSS

const Home: React.FC = () => {
  const [inputRoomId, setInputRoomId] = useState('');
  const navigate = useNavigate();

  const handleCreateRoom = async () => {
    try {
      const data = await createRoom();
      navigate(`/room/${data.room_id}`);
    } catch (error) {
      alert("Failed to create room. Is backend running?");
    }
  };

  const handleJoinRoom = () => {
    if (inputRoomId.trim()) {
      navigate(`/room/${inputRoomId}`);
    }
  };

  return (
    <div className="home-container">
      <h1 className="home-title">Pair Programming App</h1>
      
      <button onClick={handleCreateRoom} className="btn-primary">
        Create New Room
      </button>
      
      <div className="join-section">
        <p>OR</p>
        <div className="join-wrapper">
          <input 
            type="text" 
            placeholder="Enter Room ID" 
            value={inputRoomId}
            onChange={(e) => setInputRoomId(e.target.value)}
            className="room-input"
          />
          <button onClick={handleJoinRoom} className="btn-secondary">
            Join
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;