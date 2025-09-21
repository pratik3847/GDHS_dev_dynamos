import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronDown, 
  ChevronRight, 
  Download, 
  FileText,
  Stethoscope,
  BookOpen,
  Search,
  Pill,
  Clock
} from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { useToast } from "@/hooks/use-toast";
import { generatePdfReport } from "@/services/api";

const ResultsPanel = () => {
  const { agentResults, currentCase } = useAppStore();
  const { toast } = useToast();
  const [openSections, setOpenSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    const newOpenSections = new Set(openSections);
    if (newOpenSections.has(sectionId)) {
      newOpenSections.delete(sectionId);
    } else {
      newOpenSections.add(sectionId);
    }
    setOpenSections(newOpenSections);
  };

  const handleDownloadReport = async () => {
    try {
      const payload: any = {};
      // Map agentResults into the backend expected shape
      for (const r of agentResults) {
        if (r.status !== 'completed') continue;
        switch (r.agentName) {
          case 'symptom':
            payload.symptom_analysis = r.result || {};
            break;
          case 'literature':
            payload.literature = r.result || {};
            break;
          case 'case':
            payload.case_matcher = r.result || {};
            break;
          case 'treatment':
            payload.treatment = r.result || {};
            break;
          case 'summary':
            payload.summary = r.result || {};
            break;
        }
      }

      // Attach patient info if available
      if (currentCase) {
        payload.patient_info = {
          patientId: currentCase.patientId,
          age: currentCase.age,
          gender: currentCase.gender,
          medicalHistory: currentCase.medicalHistory,
          currentMedications: currentCase.currentMedications,
          urgency: currentCase.urgency,
        };
      }

      if (Object.keys(payload).length === 0) {
        toast({
          title: 'No Results Ready',
          description: 'Run an analysis before downloading a report.',
          variant: 'destructive',
        });
        return;
      }

      toast({
        title: 'Generating PDF',
        description: 'Your report will download shortly.',
      });

      const blob = await generatePdfReport(payload);
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'analysis_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      toast({
        title: 'Download Failed',
        description: err?.message || 'Could not generate PDF.',
        variant: 'destructive',
      });
    }
  };

  const getAgentIcon = (agentName: string) => {
    switch (agentName) {
      case 'symptom': return Stethoscope;
      case 'literature': return BookOpen;
      case 'case': return Search;
      case 'treatment': return Pill;
      case 'summary': return FileText;
      default: return FileText;
    }
  };

  const getAgentTitle = (agentName: string) => {
    switch (agentName) {
      case 'symptom': return 'Symptom Analysis Results';
      case 'literature': return 'Literature Review';
      case 'case': return 'Case Matching Results';
      case 'treatment': return 'Treatment Suggestions';
      case 'summary': return 'Final Summary';
      default: return 'Analysis Results';
    }
  };

  const getMockResults = (agentName: string) => {
    switch (agentName) {
      case 'symptom':
        return {
          findings: [
            "Primary symptoms indicate potential cardiovascular involvement",
            "Secondary symptoms suggest inflammatory response",
            "Risk factors identified: Age, family history"
          ],
          confidence: 85
        };
      case 'literature':
        return {
          references: [
            {
              title: "Recent advances in cardiovascular diagnostics",
              journal: "Nature Medicine",
              year: 2024,
              relevance: "High"
            },
            {
              title: "Inflammatory markers in cardiac conditions", 
              journal: "NEJM",
              year: 2023,
              relevance: "Medium"
            }
          ]
        };
      case 'case':
        return {
          similarCases: [
            {
              caseId: "C-2024-001",
              similarity: 92,
              outcome: "Successful treatment with medication"
            },
            {
              caseId: "C-2023-156",
              similarity: 87,
              outcome: "Required surgical intervention"
            }
          ]
        };
      case 'treatment':
        return {
          drugOptions: [
            {
              medication: "ACE Inhibitor",
              dosage: "10mg daily",
              confidence: 88
            },
            {
              medication: "Beta Blocker",
              dosage: "25mg twice daily", 
              confidence: 75
            }
          ],
          nonDrugOptions: [
            "Lifestyle modifications",
            "Regular monitoring",
            "Dietary changes"
          ]
        };
      case 'summary':
        return {
          keyFindings: [
            "Patient presents with cardiovascular symptoms requiring immediate attention",
            "Literature supports current diagnostic approach",
            "Similar cases show positive outcomes with recommended treatment",
            "Combination therapy recommended with close monitoring"
          ],
          recommendations: [
            "Initiate ACE inhibitor therapy",
            "Schedule follow-up in 2 weeks",
            "Monitor cardiac markers",
            "Lifestyle counseling recommended"
          ],
          riskAssessment: "Moderate risk - requires active management"
        };
      default:
        return { message: "Analysis completed successfully" };
    }
  };

  const completedResults = agentResults.filter(result => result.status === 'completed');

  if (completedResults.length === 0) {
    return (
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-primary" />
            <span>Analysis Results</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No results available yet. Start an analysis to see results here.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-primary" />
            <span>Analysis Results</span>
          </div>
          <Button onClick={handleDownloadReport} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {completedResults.map((result) => {
          const AgentIcon = getAgentIcon(result.agentName);
          const isOpen = openSections.has(result.agentName);
          const mockResults = getMockResults(result.agentName);
          const real = result.result || {} as any;

          return (
            <Collapsible
              key={result.agentName}
              open={isOpen}
              onOpenChange={() => toggleSection(result.agentName)}
            >
              <CollapsibleTrigger className="w-full">
                <div className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <AgentIcon className="h-5 w-5 text-primary" />
                    <h3 className="font-medium text-left">
                      {getAgentTitle(result.agentName)}
                    </h3>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className="bg-status-completed text-white">
                      Completed
                    </Badge>
                    {isOpen ? (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </div>
              </CollapsibleTrigger>
              
              <CollapsibleContent>
                <div className="mt-3 p-4 bg-muted/30 rounded-lg space-y-3">
                  {result.agentName === 'symptom' && (
                    <>
                      <div>
                        <h4 className="font-medium mb-2">Key Findings:</h4>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {(real.top_differentials?.map((d: any) => `${d.name}: ${d.rationale} (ICD: ${d.icd10cm_code})`) || mockResults.findings || []).map((finding: string, index: number) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="text-primary">•</span>
                              <span>{finding}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Confidence: </span>
                        <Badge variant="outline">{real.risk_level ? (real.risk_level) : (mockResults.confidence + '%')}</Badge>
                      </div>
                    </>
                  )}

                  {result.agentName === 'literature' && (
                    <div>
                      <h4 className="font-medium mb-2">Relevant References:</h4>
                      <div className="space-y-2">
                        {(real.articles?.summaries || real.articles || mockResults.references || []).map((ref: any, index: number) => (
                          <div key={index} className="p-2 bg-card rounded border">
                            <p className="font-medium text-sm">{ref.title || ref?.summary?.slice(0,60) || 'Reference'}</p>
                            {ref.pmid && (
                              <p className="text-xs text-muted-foreground">PMID: {ref.pmid}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.agentName === 'case' && (
                    <div>
                      <h4 className="font-medium mb-2">Similar Cases:</h4>
                      <div className="space-y-2">
                        {(real.matched_cases || mockResults.similarCases || []).map((caseItem: any, index: number) => (
                          <div key={index} className="p-2 bg-card rounded border">
                            <div className="flex justify-between items-start">
                              <span className="font-medium text-sm">{caseItem.name || caseItem.caseId}</span>
                              <Badge variant="outline">{Math.round((caseItem.match_score || caseItem.similarity || 0) * 100) / 100}% match</Badge>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">{caseItem.description || caseItem.outcome}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.agentName === 'treatment' && (
                    <>
                      <div>
                        <h4 className="font-medium mb-2">Drug Treatments:</h4>
                        <div className="space-y-2">
                          {(real.treatments || mockResults.drugOptions || []).filter((t: any) => (t.type || '').includes('drug')).map((drug: any, index: number) => (
                            <div key={index} className="p-2 bg-card rounded border">
                              <div className="flex justify-between items-center">
                                <span className="font-medium text-sm">{drug.name || drug.medication}</span>
                                {drug.source && <Badge variant="outline">{drug.source}</Badge>}
                              </div>
                              <p className="text-xs text-muted-foreground">{drug.class || ''} {drug.rationale ? `- ${drug.rationale}` : ''}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Non-Drug Options:</h4>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {(real.treatments || mockResults.nonDrugOptions || []).filter((t: any) => (t.type || '').includes('non-drug')).map((option: any, index: number) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="text-primary">•</span>
                              <span>{option.name || option}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}

                  {result.agentName === 'summary' && (
                    <>
                      <div>
                        <h4 className="font-medium mb-2">Key Findings:</h4>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {(real.patient_summary ? [real.patient_summary, real.clinical_summary] : mockResults.keyFindings || []).map((finding: string, index: number) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="text-primary">•</span>
                              <span>{finding}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Recommendations:</h4>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {(real.recommendations || mockResults.recommendations || []).map((rec: any, index: number) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="text-secondary">•</span>
                              <span>{typeof rec === 'string' ? rec : rec.content}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="p-3 bg-primary/10 rounded border border-primary/20">
                        <h4 className="font-medium text-primary mb-1">Risk Assessment:</h4>
                        <p className="text-sm">{real?.patient_summary ? 'See summaries above' : mockResults.riskAssessment}</p>
                      </div>
                    </>
                  )}
                  
                  <div className="text-xs text-muted-foreground border-t pt-2">
                    Completed: {result.timestamp?.toLocaleString()}
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </CardContent>
    </Card>
  );
};

export default ResultsPanel;