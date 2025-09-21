import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  Users, 
  CheckCircle, 
  TrendingUp, 
  Stethoscope,
  BookOpen,
  Search,
  Pill,
  FileText,
  Clock,
  Play,
  Pause,
  LogOut
} from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { useNavigate } from "react-router-dom";
import PatientCaseForm from "@/components/PatientCaseForm";
import AIAgentsPanel from "@/components/AIAgentsPanel";
import WorkflowPanel from "@/components/WorkflowPanel";
import ResultsPanel from "@/components/ResultsPanel";

const Dashboard = () => {
  const { user, stats, clearAuth, analysisInProgress } = useAppStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const { signOut } = await import('@/services/api');
      await signOut();
      clearAuth();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
      clearAuth();
      navigate('/');
    }
  };

  const statCards = [
    {
      title: "Active Agents",
      value: stats.activeAgents,
      icon: Users,
      color: "text-primary"
    },
    {
      title: "Completed",
      value: stats.completedCases,
      icon: CheckCircle,
      color: "text-status-completed"
    },
    {
      title: "Cases Analyzed",
      value: stats.casesAnalyzed.toLocaleString(),
      icon: Activity,
      color: "text-secondary"
    },
    {
      title: "Progress",
      value: `${stats.progress}%`,
      icon: TrendingUp,
      color: "text-primary"
    }
  ];

  return (
    <div className="min-h-screen bg-muted/20">
      {/* Header */}
      <header className="bg-background border-b shadow-card">
        <div className="container flex items-center justify-between py-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold text-foreground">MedsAI</span>
            </div>
            {analysisInProgress && (
              <Badge variant="outline" className="text-status-running border-status-running">
                <Clock className="w-3 h-3 mr-1 animate-spin" />
                Analysis in Progress
              </Badge>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-muted-foreground">Welcome back, {user?.name}!</span>
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="container py-8 space-y-8">
        {/* Welcome Section */}
        <div className="bg-gradient-card rounded-lg p-6 shadow-card">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-muted-foreground">
            Ready to analyze patient cases with AI-powered diagnostics
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => (
            <Card key={index} className="shadow-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-foreground">
                      {stat.value}
                    </p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Patient Input */}
          <div className="lg:col-span-1 space-y-6">
            <PatientCaseForm />
            <AIAgentsPanel />
          </div>

          {/* Right Column - Workflow and Results */}
          <div className="lg:col-span-2 space-y-6">
            <WorkflowPanel />
            <ResultsPanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;