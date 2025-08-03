import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';
import './App.css';

// Main App component for ODIN testing
function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  // Fetch users from API
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('https://jsonplaceholder.typicode.com/users');
      setUsers(response.data);
    } catch (err) {
      setError('Failed to fetch users');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search function
  const debouncedSearch = debounce((term) => {
    filterUsers(term);
  }, 300);

  // Filter users based on search term
  const filterUsers = (term) => {
    if (!term) {
      fetchUsers();
      return;
    }
    
    const filtered = users.filter(user => 
      user.name.toLowerCase().includes(term.toLowerCase()) ||
      user.email.toLowerCase().includes(term.toLowerCase())
    );
    setUsers(filtered);
  };

  // Calculate user stats
  const calculateUserStats = (userList) => {
    const totalUsers = userList.length;
    const domainsCount = new Set(userList.map(user => 
      user.email.split('@')[1]
    )).size;
    
    return {
      total: totalUsers,
      domains: domainsCount,
      averageId: totalUsers > 0 ? userList.reduce((sum, user) => sum + user.id, 0) / totalUsers : 0
    };
  };

  // Handle search input
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    debouncedSearch(value);
  };

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const stats = calculateUserStats(users);

  return (
    <div className="App">
      <header className="App-header">
        <h1>ODIN React Sample App</h1>
        <p>Testing ODIN v6.0 - Semantic Integrity Hash & TestGen</p>
      </header>

      <main className="App-main">
        <div className="search-section">
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>

        <div className="stats-section">
          <div className="stat-card">
            <h3>Total Users</h3>
            <span>{stats.total}</span>
          </div>
          <div className="stat-card">
            <h3>Unique Domains</h3>
            <span>{stats.domains}</span>
          </div>
          <div className="stat-card">
            <h3>Average ID</h3>
            <span>{stats.averageId.toFixed(1)}</span>
          </div>
        </div>

        {loading && <div className="loading">Loading users...</div>}
        {error && <div className="error">{error}</div>}

        <div className="users-section">
          {users.map(user => (
            <div key={user.id} className="user-card">
              <h3>{user.name}</h3>
              <p>Email: {user.email}</p>
              <p>Phone: {user.phone}</p>
              <p>Website: {user.website}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;
