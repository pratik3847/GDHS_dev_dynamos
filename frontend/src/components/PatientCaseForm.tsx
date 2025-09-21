import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAppStore } from "@/store/useAppStore";
import { User, Calendar, Stethoscope } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const PatientCaseForm = () => {
  const { setCurrentCase, currentCase } = useAppStore();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    patientId: currentCase?.patientId || "",
    age: currentCase?.age || 0,
    gender: currentCase?.gender || "",
    symptoms: currentCase?.symptoms || "",
    medicalHistory: currentCase?.medicalHistory || "",
    currentMedications: currentCase?.currentMedications || "",
    urgency: currentCase?.urgency || "medium"
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.patientId || !formData.symptoms) {
      toast({
        title: "Missing Information",
        description: "Patient ID and symptoms are required.",
        variant: "destructive",
      });
      return;
    }

    setCurrentCase({
      ...formData,
      urgency: formData.urgency as 'low' | 'medium' | 'high' | 'critical'
    });

    toast({
      title: "Case Saved",
      description: "Patient case information has been saved successfully.",
    });
  };

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const urgencyColors = {
    low: "text-green-600",
    medium: "text-yellow-600", 
    high: "text-orange-600",
    critical: "text-red-600"
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <User className="h-5 w-5 text-primary" />
          <span>Patient Case Input</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="patientId">Patient ID *</Label>
              <Input
                id="patientId"
                placeholder="P-12345"
                value={formData.patientId}
                onChange={(e) => handleInputChange('patientId', e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="45"
                value={formData.age || ''}
                onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="gender">Gender</Label>
            <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="other">Other</SelectItem>
                <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="symptoms">Symptoms *</Label>
            <Textarea
              id="symptoms"
              placeholder="Describe the patient's current symptoms..."
              value={formData.symptoms}
              onChange={(e) => handleInputChange('symptoms', e.target.value)}
              rows={3}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="medicalHistory">Medical History</Label>
            <Textarea
              id="medicalHistory"
              placeholder="Previous conditions, surgeries, family history..."
              value={formData.medicalHistory}
              onChange={(e) => handleInputChange('medicalHistory', e.target.value)}
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="currentMedications">Current Medications</Label>
            <Textarea
              id="currentMedications"
              placeholder="List current medications and dosages..."
              value={formData.currentMedications}
              onChange={(e) => handleInputChange('currentMedications', e.target.value)}
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="urgency">Case Urgency</Label>
            <Select value={formData.urgency} onValueChange={(value) => handleInputChange('urgency', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">
                  <span className={urgencyColors.low}>Low Priority</span>
                </SelectItem>
                <SelectItem value="medium">
                  <span className={urgencyColors.medium}>Medium Priority</span>
                </SelectItem>
                <SelectItem value="high">
                  <span className={urgencyColors.high}>High Priority</span>
                </SelectItem>
                <SelectItem value="critical">
                  <span className={urgencyColors.critical}>Critical</span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button type="submit" className="w-full">
            <Stethoscope className="w-4 h-4 mr-2" />
            Save Patient Case
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default PatientCaseForm;