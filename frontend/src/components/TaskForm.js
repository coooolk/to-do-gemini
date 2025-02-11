// frontend/src/components/TaskForm.js
import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const FormContainer = styled.div`
  margin-bottom: 20px;
  width: 100%;
  max-width: 600px;
  padding: 15px;
  background-color: ${props => props.theme.background};
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Input = styled.input`
  width: calc(100% - 22px);
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid ${props => props.theme.secondary};
  border-radius: 4px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;

// NEW: Styled Select for Priority Dropdown
const PrioritySelect = styled.select`
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid ${props => props.theme.secondary};
  border-radius: 4px;
  background-color: ${props => props.theme.body};
  color: ${props => props.theme.text};
  width: 100%;
  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;


const Button = styled.button`
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: ${props => props.theme.primary};
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
  &:hover {
    background-color: ${props => props.theme.primary};
  }
`;

function TaskForm({ onTaskAdded, onCategoryUpdated }) {
  const [taskTitle, setTaskTitle] = useState('');
  const [taskCategory, setTaskCategory] = useState('');
  const [taskPriority, setTaskPriority] = useState('2-Medium');
  const [taskDueDate, setTaskDueDate] = useState(''); // NEW: State for due date

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!taskTitle.trim()) return;

    const newTask = {
        title: taskTitle,
        category: taskCategory,
        priority: taskPriority,
        dueDate: taskDueDate, // NEW: Include dueDate
        completed: false,
    };

    console.log("TaskForm: taskPriority before sending:", taskPriority);
    console.log("TaskForm: taskDueDate before sending:", taskDueDate); // NEW: log dueDate
    console.log("TaskForm: taskDueDate before sending (handleSubmit):", taskDueDate);

    try {
        await axios.post('/api/tasks', newTask);
        onTaskAdded();
        onCategoryUpdated();
        setTaskTitle('');
        setTaskCategory('');
        setTaskPriority('2-Medium');
        setTaskDueDate(''); // NEW: Reset dueDate after submission
    } catch (error) {
        console.error("Error creating task:", error);
    }
};

  return (
    <FormContainer>
      <form onSubmit={handleSubmit}>
        <Input
          type="text"
          placeholder="Add a new task..."
          value={taskTitle}
          onChange={(e) => setTaskTitle(e.target.value)}
        />
        <Input
          type="text"
          placeholder="Category (Optional)"
          value={taskCategory}
          onChange={(e) => setTaskCategory(e.target.value)}
        />
        {/* NEW: Priority Dropdown */}
        <PrioritySelect
          value={taskPriority}
          onChange={(e) => setTaskPriority(e.target.value)}
        >
          <option value="1-High">High</option>
          <option value="2-Medium">Medium</option>
          <option value="3-Low">Low</option>
        </PrioritySelect>

        {/* UPDATED: Date and Time Input for Due Date */}
        <Input
            type="datetime-local"  // Changed from type="date" to "datetime-local"
            value={taskDueDate}
            onChange={(e) => {
              setTaskDueDate(e.target.value);
              // ADD THIS console.log STATEMENT:
              console.log("TaskForm: datetime-local input onChange value:", e.target.value);
          }}
            placeholder="Due Date & Time (Optional)"
        />

        <Button type="submit">Add Task</Button>
      </form>
    </FormContainer>
  );
}

export default TaskForm;