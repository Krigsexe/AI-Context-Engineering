import React, { useState, useEffect } from 'react';
import { Activity, Terminal, Shield, Brain, Send, Server, Play, StopCircle } from 'lucide-react';
import { io } from 'socket.io-client';

function App() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTask, setNewTask] = useState('');
  const [agents, setAgents] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>({
    api: false,
    orchestrator: false,
    redis: false,
    postgres: false,
    llm: false
  });

  useEffect(() => {
    // Check health
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/v1/health');
        if (res.ok) {
          const data = await res.json();
          setSystemStatus(data.components);
        }
      } catch (e) {
        console.error("Health check failed", e);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    try {
      const res = await fetch('/api/v1/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: newTask })
      });
      
      if (res.ok) {
        const task = await res.json();
        setTasks(prev => [task, ...prev]);
        setNewTask('');
      }
    } catch (e) {
      console.error("Failed to submit task", e);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-primary" />
            <h1 className="text-xl font-bold">ODIN v7.0</h1>
            <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">BETA</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <StatusIndicator label="API" status={systemStatus?.api} />
            <StatusIndicator label="Orchestrator" status={systemStatus?.orchestrator} />
            <StatusIndicator label="LLM" status={systemStatus?.llm} />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Task Input & Active Tasks */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Input Area */}
          <section className="bg-card rounded-lg border border-border p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Terminal className="w-5 h-5" />
              New Task
            </h2>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Describe your task (e.g., 'Create a Python script to scrape website titles')..."
                className="flex-1 bg-background border border-input rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button 
                type="submit"
                className="bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Execute
              </button>
            </form>
          </section>

          {/* Active Tasks */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Active Operations
            </h2>
            
            {tasks.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground border-2 border-dashed border-border rounded-lg">
                No active tasks running
              </div>
            ) : (
              tasks.map(task => (
                <TaskCard key={task.id} task={task} />
              ))
            )}
          </section>
        </div>

        {/* Right Column - System Status & Agents */}
        <div className="space-y-8">
          
          {/* Agent Status */}
          <section className="bg-card rounded-lg border border-border p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Server className="w-5 h-5" />
              Agent Pool
            </h2>
            <div className="space-y-3">
              <AgentStatus name="Intake" status="idle" />
              <AgentStatus name="Retrieval" status="idle" />
              <AgentStatus name="Reasoning" status="offline" />
              <AgentStatus name="Dev" status="idle" />
              <AgentStatus name="Oracle Code" status="active" />
              <AgentStatus name="Security" status="idle" />
            </div>
          </section>

          {/* Security & Checkpoints */}
          <section className="bg-card rounded-lg border border-border p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5" />
              System Integrity
            </h2>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span>Last Checkpoint</span>
                <span className="font-mono text-muted-foreground">#CK-9281</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span>Security Scan</span>
                <span className="text-green-500">Passed</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Rollback Status</span>
                <span className="text-green-500">Ready</span>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}

const StatusIndicator = ({ label, status }: { label: string, status: boolean }) => (
  <div className="flex items-center gap-2">
    <div className={`w-2 h-2 rounded-full ${status ? 'bg-green-500' : 'bg-red-500'}`} />
    <span>{label}</span>
  </div>
);

const AgentStatus = ({ name, status }: { name: string, status: 'idle' | 'active' | 'offline' }) => {
  const colors = {
    idle: 'bg-yellow-500',
    active: 'bg-green-500',
    offline: 'bg-gray-500'
  };
  
  return (
    <div className="flex items-center justify-between p-2 bg-background rounded border border-border">
      <span className="font-medium">{name}</span>
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase text-muted-foreground">{status}</span>
        <div className={`w-2 h-2 rounded-full ${colors[status]}`} />
      </div>
    </div>
  );
};

const TaskCard = ({ task }: { task: any }) => (
  <div className="bg-card rounded-lg border border-border p-4 shadow-sm animate-in fade-in slide-in-from-bottom-4">
    <div className="flex justify-between items-start mb-2">
      <h3 className="font-medium">{task.description}</h3>
      <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100 text-xs rounded-full">
        Processing
      </span>
    </div>
    <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
      <div className="bg-primary h-full w-1/3 animate-pulse" />
    </div>
    <div className="mt-2 text-xs text-muted-foreground font-mono">
      > Initializing context analysis...
    </div>
  </div>
);

export default App;
