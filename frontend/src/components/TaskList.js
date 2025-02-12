// frontend/src/components/TaskList.js
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { motion } from 'framer-motion';
import { FaTrash, FaCheck } from 'react-icons/fa';
// REMOVE ObjectId import: import { ObjectId } from 'mongodb';

const TaskListContainer = styled.ul`
  list-style: none;
  padding: 0;
  width: 100%;
  max-width: 600px;
`;

const TaskItem = styled(motion.li)`
    background-color: ${props => props.theme.background};
    padding: 15px 20px;
    margin-bottom: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex; /* Use flexbox for main layout */
    flex-direction: column; /* Stack elements vertically by default */
    align-items: stretch; /* Stretch items to fill width */
    justify-content: flex-start; /* Align items to the start */
`;

const TaskHeader = styled.div`
    display: flex;
    justify-content: space-between; /* Category on left, actions on right in header */
    align-items: center;
    margin-bottom: 8px; /* Spacing between header and task text */
`;

const TaskDetails = styled.div`
    margin-bottom: 10px; /* Spacing between details and actions */
    display: flex;
    flex-direction: column; /* Stack priority and dates vertically */
    gap: 4px; /* Spacing between priority and date lines */
`;


const TaskActions = styled.div`
    display: flex;
    justify-content: flex-end; /* Align action buttons to the right */
    align-items: center;
    margin-top: 10px; /* Push actions down a bit */
`;


const TaskText = styled.span`
  flex-grow: 1;
  margin-right: 15px;
  text-decoration: ${props => props.completed ? 'line-through' : 'none'};
  opacity: ${props => props.completed ? 0.6 : 1};
  margin-bottom: 5px;
`;


// Option B: Tags with a Border and Background Color
const CategoryTag = styled.span`
  font-size: 0.75em;
  font-weight: bold;
  color: ${props => props.theme.text}; /* Use text color for tag text */
  background-color: ${props => props.theme.secondary}; /* Use secondary color for background */
  padding: 3px 7px;
  border-radius: 6px;
  margin-right: 8px;
  border: 1px solid ${props => props.theme.secondary}; /* Add a border */
`;


const PriorityText = styled.span`
  font-size: 0.85em;
  font-style: italic;
  color: ${props => props.priority && props.priority.startsWith('1-') ? '#FF4D4D' : (props.priority && props.priority.startsWith('2-') ? '#FFAA00' : props.theme.secondary)}; // Example priority-based colors
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.secondary};
  cursor: pointer;
  margin-left: 8px;
  font-size: 1em;
  &:hover {
    color: ${props => props.theme.primary};
  }
`;

// NEW: Styled component for Due Date display
const DueDateText = styled.span`
    font-size: 0.75em;
    color: ${props => props.theme.secondary};
    font-style: italic;
    margin-top: 5px;
`;

// NEW: Styled component for Created Date display
const CreatedDateText = styled.span`
    font-size: 0.7em;
    color: ${props => props.theme.text};
    opacity: 0.7;
    margin-top: 2px;
`;

const DeleteAllButton = styled.button`
    background-color: #ff6f61; /* Example red color */
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9em;
    margin-top: 20px;
    transition: background-color 0.3s ease;
    &:hover {
        background-color: #e0524a;
    }
`;

function TaskList({ tasksUpdatedFlag, categoryFilter, onCategoryUpdated, sortOption, onDeleteAllTasks }) {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, [tasksUpdatedFlag, categoryFilter, sortOption]);

  const fetchTasks = async () => {
    try {
      const response = await axios.get('/api/tasks', {
        params: {
          category: categoryFilter,
          sortBy: sortOption, // NEW: Send sortOption to backend as query parameter
        },
      });
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    }
  };

  const handleDeleteTask = async (id) => {
    try {
      await axios.delete(`/api/tasks/${id}`);
      fetchTasks();
      onCategoryUpdated();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };


  const handleDeleteAllTasks = useCallback(async () => {
    console.log("handleDeleteAllTasks: Function called");
    if (window.confirm("Are you sure you want to delete all tasks? This action cannot be undone.")) {
      try {
        console.log("handleDeleteAllTasks: Confirmation accepted, sending DELETE request");
        const response = await axios.delete('/api/tasks/clear');
        console.log("handleDeleteAllTasks: DELETE request completed");
        console.log("handleDeleteAllTasks: Response status:", response.status);
        console.log("handleDeleteAllTasks: Response data:", response.data);

        if (response.status >= 200 && response.status < 300) { // Explicitly check for 2xx success status
          console.log("handleDeleteAllTasks: Success status detected (2xx)");
          fetchTasks(); // Refresh task list after deletion
          onDeleteAllTasks(); // Call onDeleteAllTasks prop if needed
          console.log("handleDeleteAllTasks: fetchTasks and onDeleteAllTasks called");
        } else {
          // This *shouldn't* happen with axios on 2xx, but for robustness, handle non-2xx explicitly
          console.error("handleDeleteAllTasks: Backend responded with non-success status, should not reach here with axios success. Status:", response.status);
          alert("Unexpected issue deleting tasks (non-200 status). Please check console.");
        }


      } catch (error) {
        console.error("handleDeleteAllTasks: ERROR caught in try-catch block");
        console.error("handleDeleteAllTasks: Error object:", error);
        alert("Failed to delete all tasks due to an error. Please check console.");
      }
    } else {
      console.log("handleDeleteAllTasks: Confirmation cancelled by user");
    }
  }, [fetchTasks, onDeleteAllTasks]);

    const handleCompleteToggle = async (task) => {
    try {
      await axios.put(`/api/tasks/${task._id}`, { completed: !task.completed, priority: task.priority });
      fetchTasks();
    } catch (error) {
      console.error("Error updating task completion:", error);
    }
  };


  return (
    <TaskListContainer>
        {tasks.map(task => (
            <TaskItem
                key={task._id}
                completed={task.completed}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
            >
                <TaskHeader>
                    <CategoryTag>{task.category}</CategoryTag>
                    {/* Actions moved to TaskActions section below */}
                </TaskHeader>

                <TaskText completed={task.completed}>{task.title}</TaskText>

                <TaskDetails>
                    <PriorityText priority={task.priority}>Priority: {task.priority && task.priority.split('-')[1]}</PriorityText>
                    {/* NEW: Display Due Date and Time - Explicitly set UTC timezone for formatting */}
                    {task.dueDate && (
                        <DueDateText>
                            Due: {new Date(task.dueDate).toLocaleDateString('en-US', { timeZone: 'UTC' })},
                                 {new Date(task.dueDate).toLocaleTimeString('en-US', { timeZone: 'UTC' })}
                        </DueDateText>
                    )}
                    <CreatedDateText>
                        Added: {new Date(task.createdAt).toLocaleDateString()} {new Date(task.createdAt).toLocaleTimeString()}
                    </CreatedDateText>
                </TaskDetails>

                <TaskActions>
                    <ActionButton onClick={() => handleCompleteToggle(task)}>
                        <FaCheck />
                    </ActionButton>
                    <ActionButton onClick={() => handleDeleteTask(task._id)}>
                        <FaTrash />
                    </ActionButton>
                </TaskActions>


            </TaskItem>
        ))}

<DeleteAllButton onClick={handleDeleteAllTasks}>
    Delete All Tasks
</DeleteAllButton>
    </TaskListContainer>
);
}

export default TaskList;