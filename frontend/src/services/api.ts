import axios from 'axios'
import { supabase } from '@/integrations/supabase/client'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token if available
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface PatientData {
  patientId: string
  age: number
  gender: string
  symptoms: string
  medicalHistory: string
  currentMedications: string
  urgency: string
}

export interface AnalysisResult {
  agentName: string
  status: string
  result: any
  timestamp: string
}

// Main analysis endpoint
export const analyzePatientCase = async (patientData: PatientData) => {
  const response = await api.post('/analyze', patientData)
  return response.data
}

// Generate PDF report
export const generatePdfReport = async (analysisPayload: any) => {
  const response = await api.post('/generate-pdf', analysisPayload, {
    responseType: 'blob'
  })
  return response.data as Blob
}

// Individual agent endpoints
export const callSymptomAgent = async (symptoms: string) => {
  const response = await api.post('/agents/symptom', { symptoms })
  return response.data
}

export const callLiteratureAgent = async (condition: string) => {
  const response = await api.post('/agents/literature', { condition })
  return response.data
}

export const callCaseAgent = async (patientData: PatientData) => {
  const response = await api.post('/agents/case', patientData)
  return response.data
}

export const callTreatmentAgent = async (condition: string, patientData: PatientData) => {
  const response = await api.post('/agents/treatment', { condition, patientData })
  return response.data
}

export const callSummaryAgent = async (allResults: any[]) => {
  const response = await api.post('/agents/summary', { results: allResults })
  return response.data
}

// Auth functions using Supabase
export const loginUser = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  
  if (error) throw error
  
  return {
    user: {
      id: data.user!.id,
      email: data.user!.email!,
      name: data.user!.user_metadata?.name || data.user!.email!.split('@')[0]
    },
    session: data.session
  }
}

export const signupUser = async (email: string, password: string, name: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        name: name,
      },
      emailRedirectTo: `${window.location.origin}/`
    }
  })
  
  if (error) throw error
  
  return {
    user: {
      id: data.user!.id,
      email: data.user!.email!,
      name: name
    },
    session: data.session
  }
}

export const signInWithProvider = async (provider: 'google' | 'github') => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider,
    options: {
      redirectTo: `${window.location.origin}/dashboard`
    }
  })
  
  if (error) throw error
  return data
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

export default api