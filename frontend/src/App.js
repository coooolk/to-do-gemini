// frontend/src/App.js
import React, { useState, useEffect } from 'react'; // Import useEffect
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { lightTheme, darkTheme } from './theme';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import axios from 'axios'; // Import axios for fetching categories

const GlobalStyle = createGlobalStyle`
  body {
    background-color: ${props => props.theme.body};
    color: ${props => props.theme.text};
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    transition: background-color 0.3s ease;
  }
`;

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px;
`;

const Title = styled.h1`
  color: ${props => props.theme.primary};
  margin-bottom: 20px;
`;

const CategoryFilterSelect = styled.select`
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid ${props => props.theme.secondary};
  margin-bottom: 15px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;


function App() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  const [theme, setTheme] = useState(savedTheme);
  const currentTheme = theme === 'light' ? lightTheme : darkTheme;

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const [tasksUpdated, setTasksUpdated] = useState(false);
  const handleTaskUpdated = () => {
    setTasksUpdated(!tasksUpdated);
  };

  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('');
  const handleCategoryFilterChange = (event) => {
    setSelectedCategoryFilter(event.target.value);
  };

  const [availableCategories, setAvailableCategories] = useState([]);

  // NEW: State to trigger category list update
  const [categoriesUpdated, setCategoriesUpdated] = useState(false);

  // NEW: Callback function to toggle categoriesUpdated state
  const handleCategoryUpdated = () => {
    setCategoriesUpdated(!categoriesUpdated);
  };

  // NEW: State for selected sort option, default to 'timeAddedAsc'
  const [selectedSortOption, setSelectedSortOption] = useState('timeAddedAsc');

  const handleSortOptionChange = (event) => {
    setSelectedSortOption(event.target.value);

};
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/api/categories');
        setAvailableCategories(response.data);
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };
    fetchCategories();
  }, [categoriesUpdated]); // NEW: Add categoriesUpdated as dependency


  return (
    <ThemeProvider theme={currentTheme}>
      <GlobalStyle />
      <AppContainer>
        <Title>Minimalist To-Do App</Title>
        <button onClick={toggleTheme}>Toggle Theme</button>

        <CategoryFilterSelect
          value={selectedCategoryFilter}
          onChange={handleCategoryFilterChange}
        >
          <option value="">All Categories</option>
          {availableCategories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </CategoryFilterSelect>

        {/* NEW: Sort By Dropdown */}
        <CategoryFilterSelect // Reusing CategoryFilterSelect styling for Sort dropdown for now
          value={selectedSortOption}
          onChange={handleSortOptionChange}
        >
          <option value="timeAddedAsc">Time Added (Ascending)</option>
          <option value="timeAddedDesc">Time Added (Descending)</option>
          <option value="priority">Priority</option>
          <option value="priorityTimeAdded">Priority then Time Added</option>
        </CategoryFilterSelect>


        <TaskForm onTaskAdded={handleTaskUpdated} onCategoryUpdated={handleCategoryUpdated} />
        {/* Pass selectedSortOption to TaskList */}
        <TaskList // Render TaskList only once
            tasksUpdatedFlag={tasksUpdated}
            categoryFilter={selectedCategoryFilter} // Pass categoryFilter
            onCategoryUpdated={handleCategoryUpdated} // Pass onCategoryUpdated
            sortOption={selectedSortOption} // Pass sortOption
            onDeleteAllTasks={handleTaskUpdated} // Pass onDeleteAllTasks
        />
      </AppContainer>
    </ThemeProvider>
  );
}


export default App;
