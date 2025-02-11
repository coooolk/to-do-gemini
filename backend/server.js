require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

const uri = process.env.MONGODB_URI;
const client = new MongoClient(uri);
let db;

async function connectToDatabase() {
    try {
        await client.connect();
        db = client.db(process.env.DB_NAME);
        console.log("Connected to MongoDB");
    } catch (err) {
        console.error("Failed to connect to MongoDB", err);
        process.exit(1);
    }
}

connectToDatabase();

const TASKS_COLLECTION = 'tasks';

// GET unique categories
app.get('/api/categories', async (req, res) => {
     try {
         const categories = await db.collection(TASKS_COLLECTION).distinct('category'); // Use distinct to get unique categories
         res.json(categories);
     } catch (err) {
         console.error("Error fetching categories", err);
         res.status(500).json({ message: "Failed to fetch categories" });
     }
 });

// GET tasks, optionally filter by category and now SORT
app.get('/api/tasks', async (req, res) => {
    const categoryFilter = req.query.category;
    const sortBy = req.query.sortBy; // NEW: Get sortBy query parameter
    let query = {};
    if (categoryFilter) {
        query = { category: categoryFilter };
    }

    let sortCriteria = {}; // Default no sort
    if (sortBy === 'timeAddedAsc') {
        sortCriteria = { createdAt: 1 }; // 1 for ascending, -1 for descending
    } else if (sortBy === 'timeAddedDesc') {
        sortCriteria = { createdAt: -1 };
    } else if (sortBy === 'priority') {
        sortCriteria = { priority: 1 }; // Sort by priority (High, Medium, Low will be default string sort order, which is okay for now)
    } else if (sortBy === 'priorityTimeAdded') {
        sortCriteria = { priority: 1, createdAt: 1 }; // Sort by priority, then by time added
    }

    try {
        const tasks = await db.collection(TASKS_COLLECTION)
            .find(query, { projection: { dueDate: 1, createdAt: 1, title: 1, category: 1, priority: 1, completed: 1, _id: 1 } }) // Optional projection to be explicit
            .sort(sortCriteria)
            .toArray();
        res.json(tasks);
    } catch (err) {
        console.error("Error fetching tasks:", err);
        res.status(500).json({ message: "Failed to fetch tasks" });
    }
});

// POST a new task
app.post('/api/tasks', async (req, res) => {
    console.log("Backend received POST /api/tasks, req.body:", req.body); // Keep this for debugging
    console.log("Backend received POST /api/tasks, req.body.dueDate:", req.body.dueDate);
    
    const newTask = req.body;
    if (!newTask.title) {
        return res.status(400).json({ message: "Task title is required" });
    }
    const taskToInsert = {
        title: newTask.title,
        category: newTask.category || 'General',
        priority: newTask.priority || '2-Medium',
        completed: false,
        createdAt: new Date(), // Already present
        dueDate: newTask.dueDate ? new Date(newTask.dueDate) : null // NEW: Add dueDate
    };

    try {
        const result = await db.collection(TASKS_COLLECTION).insertOne(taskToInsert);
        res.status(201).json({ ...taskToInsert, _id: result.insertedId });
    } catch (err) {
        console.error("Error creating task", err);
        res.status(500).json({ message: "Failed to create task" });
    }
});
 
 // PUT (Update) task completion status and now ALSO priority (MODIFY to accept 'priority' update)
 app.put('/api/tasks/:id', async (req, res) => {
     const taskId = req.params.id;
     const updates = req.body; // Expecting { completed: true/false, priority: 'High'/'Medium'/'Low' }
 
     if (!ObjectId.isValid(taskId)) {
         return res.status(400).json({ message: "Invalid task ID" });
     }
 
     try {
         await db.collection(TASKS_COLLECTION).updateOne(
             { _id: new ObjectId(taskId) },
             { $set: updates } // Use $set to update only the provided fields (completed, priority)
         );
         res.json({ message: "Task updated successfully" });
     } catch (err) {
         console.error("Error updating task", err);
         res.status(500).json({ message: "Failed to update task" });
     }
 });

// DELETE a task by ID
app.delete('/api/tasks/:id', async (req, res) => {
    try {
        const taskId = req.params.id;
        const result = await db.collection(TASKS_COLLECTION).deleteOne({ _id: new ObjectId(taskId) });
        if (result.deletedCount === 0) {
            return res.status(404).json({ message: "Task not found" });
        }
        res.json({ message: "Task deleted successfully" });
    } catch (err) {
        console.error("Error deleting task", err);
        res.status(500).json({ message: "Failed to delete task" });
    }
});


app.get('/', (req, res) => {
    res.send('To-Do Backend is running!');
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});