import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Stethoscope, 
  BookOpen, 
  Search, 
  Pill, 
  FileText,
  Activity
} from "lucide-react";

const AIAgentsPanel = () => {
  const agents = [
    {
      id: "symptom",
      name: "Symptom Analyzer",
      description: "Analyzes patient symptoms to identify potential conditions",
      icon: Stethoscope,
      status: "active",
      color: "bg-primary"
    },
    {
      id: "literature",
      name: "Literature Agent", 
      description: "Searches medical literature and PubMed for relevant research",
      icon: BookOpen,
      status: "active", 
      color: "bg-secondary"
    },
    {
      id: "case",
      name: "Case Matcher",
      description: "Matches patient cases with similar historical cases",
      icon: Search,
      status: "active",
      color: "bg-accent-foreground"
    },
    {
      id: "treatment",
      name: "Treatment Agent",
      description: "Suggests treatment options based on analysis results",
      icon: Pill,
      status: "active",
      color: "bg-status-completed"
    },
    {
      id: "summary",
      name: "Summarizer Agent",
      description: "Creates comprehensive summary of all findings",
      icon: FileText,
      status: "active",
      color: "bg-status-running"
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-status-completed text-white';
      case 'inactive': return 'bg-muted text-muted-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-primary" />
          <span>AI Agents</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="flex items-start space-x-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
          >
            <div className={`p-2 rounded-md ${agent.color}`}>
              <agent.icon className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h4 className="font-medium text-sm text-foreground">
                  {agent.name}
                </h4>
                <Badge className={getStatusColor(agent.status)} variant="secondary">
                  {agent.status}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                {agent.description}
              </p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

export default AIAgentsPanel;