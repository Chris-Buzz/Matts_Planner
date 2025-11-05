let allTasks = [];
let currentView = 'all';
let currentCategory = 'all';
let editingTaskId = null;

// DOM Elements
const tasksContainer = document.getElementById('tasksContainer');
const addTaskBtn = document.getElementById('addTaskBtn');
const taskModal = document.getElementById('taskModal');
const closeModal = document.getElementById('closeModal');
const cancelBtn = document.getElementById('cancelBtn');
const taskForm = document.getElementById('taskForm');
const searchInput = document.getElementById('searchInput');
const modalTitle = document.getElementById('modalTitle');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');

// Sidebar buttons
const sidebarBtns = document.querySelectorAll('.sidebar-btn');
const categoryBtns = document.querySelectorAll('.category-btn');

// Sidebar toggle functionality
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const icon = sidebarToggle.querySelector('i');
        if (sidebar.classList.contains('collapsed')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-chevron-right');
        } else {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-bars');
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadStats();
    setupEventListeners();
    
    // Set minimum date to current date/time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('taskDueDate').min = now.toISOString().slice(0, 16);
});

function setupEventListeners() {
    addTaskBtn.addEventListener('click', openAddModal);
    closeModal.addEventListener('click', closeTaskModal);
    cancelBtn.addEventListener('click', closeTaskModal);
    taskForm.addEventListener('submit', handleTaskSubmit);
    searchInput.addEventListener('input', handleSearch);
    
    sidebarBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sidebarBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            document.getElementById('viewTitle').textContent = btn.textContent.trim();
            filterAndDisplayTasks();
        });
    });
    
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            filterAndDisplayTasks();
        });
    });
    
    // Close modal on outside click
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeTaskModal();
        }
    });
}

async function loadTasks() {
    try {
        const response = await fetch(`/api/tasks?view=${currentView}`);
        allTasks = await response.json();
        filterAndDisplayTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        tasksContainer.innerHTML = '<div class="no-tasks">Error loading tasks</div>';
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('totalTasks').textContent = stats.total_tasks;
        document.getElementById('todayTasks').textContent = stats.today_tasks;
        document.getElementById('completedTasks').textContent = stats.completed_today;
        document.getElementById('pendingTasks').textContent = stats.pending_tasks;
        
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        progressFill.style.width = stats.completion_rate + '%';
        progressText.textContent = stats.completion_rate + '% Complete';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function filterAndDisplayTasks() {
    let filteredTasks = [...allTasks];
    
    // Filter by category
    if (currentCategory !== 'all') {
        filteredTasks = filteredTasks.filter(task => task.category === currentCategory);
    }
    
    // Filter by search
    const searchTerm = searchInput.value.toLowerCase();
    if (searchTerm) {
        filteredTasks = filteredTasks.filter(task => 
            task.title.toLowerCase().includes(searchTerm) ||
            task.description.toLowerCase().includes(searchTerm)
        );
    }
    
    displayTasks(filteredTasks);
}

function displayTasks(tasks) {
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<div class="no-tasks"><i class="fas fa-inbox"></i><br>No tasks found</div>';
        return;
    }
    
    tasksContainer.innerHTML = tasks.map(task => createTaskCard(task)).join('');
    
    // Add event listeners
    document.querySelectorAll('.btn-complete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            completeTask(btn.dataset.id);
        });
    });
    
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            openEditModal(btn.dataset.id);
        });
    });
    
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteTask(btn.dataset.id);
        });
    });
}

function createTaskCard(task) {
    const dueDate = new Date(task.due_date);
    const isOverdue = dueDate < new Date() && task.status === 'pending';
    
    return `
        <div class="task-card priority-${task.priority} ${task.status}">
            <div class="task-header">
                <div>
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <div class="task-meta">
                        <span><i class="fas fa-calendar"></i> ${formatDate(dueDate)}</span>
                        <span><i class="fas fa-clock"></i> ${formatTime(dueDate)}</span>
                        <span><i class="fas fa-tag"></i> ${task.category}</span>
                        <span class="priority-${task.priority}">
                            <i class="fas fa-flag"></i> ${task.priority}
                        </span>
                        ${isOverdue ? '<span style="color: var(--danger-color);"><i class="fas fa-exclamation-triangle"></i> Overdue</span>' : ''}
                    </div>
                </div>
            </div>
            ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
            <div class="task-actions">
                ${task.status === 'pending' ? `<button class="btn-complete" data-id="${task.id}"><i class="fas fa-check"></i> Complete</button>` : ''}
                <button class="btn-edit" data-id="${task.id}"><i class="fas fa-edit"></i> Edit</button>
                <button class="btn-delete" data-id="${task.id}"><i class="fas fa-trash"></i> Delete</button>
            </div>
        </div>
    `;
}

function openAddModal() {
    editingTaskId = null;
    modalTitle.textContent = 'Add New Task';
    taskForm.reset();
    
    // Set default date to current time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('taskDueDate').value = now.toISOString().slice(0, 16);
    
    taskModal.classList.add('show');
}

function openEditModal(taskId) {
    editingTaskId = taskId;
    const task = allTasks.find(t => t.id == taskId);
    
    if (!task) return;
    
    modalTitle.textContent = 'Edit Task';
    document.getElementById('taskId').value = task.id;
    document.getElementById('taskTitle').value = task.title;
    document.getElementById('taskDescription').value = task.description;
    document.getElementById('taskCategory').value = task.category;
    document.getElementById('taskPriority').value = task.priority;
    
    const dueDate = new Date(task.due_date);
    dueDate.setMinutes(dueDate.getMinutes() - dueDate.getTimezoneOffset());
    document.getElementById('taskDueDate').value = dueDate.toISOString().slice(0, 16);
    
    taskModal.classList.add('show');
}

function closeTaskModal() {
    taskModal.classList.remove('show');
    taskForm.reset();
    editingTaskId = null;
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        category: document.getElementById('taskCategory').value,
        priority: document.getElementById('taskPriority').value,
        due_date: document.getElementById('taskDueDate').value
    };
    
    try {
        let response;
        if (editingTaskId) {
            response = await fetch(`/api/tasks/${editingTaskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        } else {
            response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            closeTaskModal();
            await loadTasks();
            await loadStats();
        }
    } catch (error) {
        console.error('Error saving task:', error);
        alert('Error saving task. Please try again.');
    }
}

async function completeTask(taskId) {
    if (!confirm('Mark this task as completed?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}/complete`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadTasks();
            await loadStats();
        }
    } catch (error) {
        console.error('Error completing task:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadTasks();
            await loadStats();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

function handleSearch() {
    filterAndDisplayTasks();
}

function formatDate(date) {
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Refresh tasks every 5 minutes
setInterval(() => {
    loadTasks();
    loadStats();
}, 300000);