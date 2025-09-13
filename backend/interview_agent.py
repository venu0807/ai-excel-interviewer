"""
AI Interview Agent for Excel Mock Interviewer
Intelligent conversational agent that conducts Excel proficiency interviews
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with Local Llama 3 Model"""
    
    def __init__(self):
        from llama_cpp import Llama
        
        # Initialize Llama model
        self.llm = Llama(
            model_path="llama3:latest",  # Your local Llama 3 model path
            n_ctx=4096,  # Context window
            n_threads=4  # Number of CPU threads to use
        )
        
    async def generate_response(self, prompt: str, model: str = "llama") -> str:
        """Generate response using local Llama 3"""
        try:
            response = await asyncio.to_thread(
                self.llm.create_completion,
                prompt,
                max_tokens=1000,
                temperature=0.7,
                stop=["User:", "Assistant:"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error generating Llama response: {str(e)}")
            return "I encountered an error. Please try again."

class ExcelEvaluator:
    """Evaluates Excel knowledge and responses"""
    
    def __init__(self):
        self.skill_categories = {
            "basic_functions": ["SUM", "AVERAGE", "COUNT", "MAX", "MIN"],
            "lookup_functions": ["VLOOKUP", "HLOOKUP", "INDEX", "MATCH", "XLOOKUP"],
            "data_analysis": ["Pivot Tables", "Charts", "Data Validation", "Conditional Formatting"],
            "advanced_features": ["Macros", "VBA", "Array Formulas", "Power Query", "Power Pivot"],
            "data_management": ["Sorting", "Filtering", "Subtotals", "Grouping", "Freeze Panes"]
        }
        
        self.evaluation_criteria = {
            "technical_accuracy": "Correctness of Excel knowledge and concepts",
            "practical_application": "Ability to apply knowledge to real-world scenarios",
            "problem_solving": "Logical approach to solving Excel problems",
            "communication": "Clarity in explaining Excel concepts and solutions"
        }
    
    def evaluate_response(self, question: str, response: str, context: Dict) -> Dict:
        """Evaluate a candidate's response"""
        evaluation = {
            "technical_accuracy": self._assess_technical_accuracy(response),
            "practical_application": self._assess_practical_application(response),
            "problem_solving": self._assess_problem_solving(response),
            "communication": self._assess_communication(response),
            "overall_score": 0,
            "feedback": "",
            "skill_category": self._identify_skill_category(question)
        }
        
        # Calculate overall score
        evaluation["overall_score"] = sum([
            evaluation["technical_accuracy"],
            evaluation["practical_application"],
            evaluation["problem_solving"],
            evaluation["communication"]
        ]) / 4
        
        # Generate feedback
        evaluation["feedback"] = self._generate_feedback(evaluation)
        
        return evaluation
    
    def _assess_technical_accuracy(self, response: str) -> int:
        """Assess technical accuracy (0-100)"""
        response_lower = response.lower()
        
        # Check for correct Excel terminology and concepts
        accuracy_indicators = [
            "vlookup", "hlookup", "index", "match", "sum", "average", "count",
            "pivot table", "conditional formatting", "data validation", "macro",
            "formula", "function", "cell reference", "absolute reference"
        ]
        
        score = 0
        for indicator in accuracy_indicators:
            if indicator in response_lower:
                score += 10
        
        return min(score, 100)
    
    def _assess_practical_application(self, response: str) -> int:
        """Assess practical application (0-100)"""
        response_lower = response.lower()
        
        # Check for practical examples and real-world applications
        practical_indicators = [
            "example", "scenario", "case", "situation", "data", "analysis",
            "business", "report", "dashboard", "automation", "efficiency"
        ]
        
        score = 0
        for indicator in practical_indicators:
            if indicator in response_lower:
                score += 12
        
        return min(score, 100)
    
    def _assess_problem_solving(self, response: str) -> int:
        """Assess problem-solving approach (0-100)"""
        response_lower = response.lower()
        
        # Check for structured problem-solving approach
        problem_solving_indicators = [
            "first", "then", "next", "finally", "step", "process", "approach",
            "method", "solution", "solve", "identify", "analyze", "implement"
        ]
        
        score = 0
        for indicator in problem_solving_indicators:
            if indicator in response_lower:
                score += 12
        
        return min(score, 100)
    
    def _assess_communication(self, response: str) -> int:
        """Assess communication clarity (0-100)"""
        # Simple assessment based on response length and structure
        word_count = len(response.split())
        
        if word_count < 10:
            return 30
        elif word_count < 20:
            return 60
        elif word_count < 50:
            return 80
        else:
            return 90
    
    def _identify_skill_category(self, question: str) -> str:
        """Identify the skill category for the question"""
        question_lower = question.lower()
        
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill.lower() in question_lower:
                    return category
        
        return "general"
    
    def _generate_feedback(self, evaluation: Dict) -> str:
        """Generate constructive feedback based on evaluation"""
        score = evaluation["overall_score"]
        
        if score >= 80:
            return "Excellent response! You demonstrated strong Excel knowledge and clear communication."
        elif score >= 60:
            return "Good response. You show solid understanding with room for improvement in some areas."
        elif score >= 40:
            return "Adequate response. Consider providing more specific examples and technical details."
        else:
            return "Your response could be improved. Try to be more specific about Excel functions and provide practical examples."

class InterviewAgent:
    """Main AI Interview Agent"""
    
    def __init__(self, session_id: str, candidate_info: Dict):
        self.session_id = session_id
        self.candidate_info = candidate_info
        self.llm_client = LLMClient()
        self.evaluator = ExcelEvaluator()
        
        self.interview_state = {
            "phase": "introduction",
            "questions_asked": 0,
            "current_skill_level": "beginner",
            "responses": [],
            "performance_tracking": {
                "correct_answers": 0,
                "total_questions": 0,
                "skill_demonstrations": []
            }
        }
        
        self.question_bank = self._initialize_question_bank()
    
    def _initialize_question_bank(self) -> Dict:
        """Initialize the question bank with Excel interview questions"""
        return {
            "introduction": [
                "Hello! I'm your AI Excel interviewer. Can you tell me about your Excel experience and what you're most comfortable working with?",
                "Welcome! Let's start with a brief introduction. How long have you been using Excel, and what's your primary use case?"
            ],
            "basic_functions": [
                "Can you explain the difference between SUM and SUMIF functions? When would you use each?",
                "How would you calculate the average of values in a range while excluding zeros?",
                "Explain how COUNT, COUNTA, and COUNTBLANK functions work and give examples of when you'd use each."
            ],
            "lookup_functions": [
                "Walk me through how VLOOKUP works. What are its limitations and when might you choose INDEX/MATCH instead?",
                "How would you handle a lookup scenario where you need to find the second occurrence of a value?",
                "Explain the difference between VLOOKUP and XLOOKUP. What advantages does XLOOKUP offer?"
            ],
            "data_analysis": [
                "Describe how you would create a pivot table to analyze sales data by region and product category.",
                "How would you use conditional formatting to highlight cells that are above the average value in a column?",
                "Explain data validation in Excel and provide a practical example of when you'd use it."
            ],
            "advanced_features": [
                "Have you worked with Excel macros? Describe a scenario where you'd use a macro to automate a task.",
                "How would you handle a situation where you need to analyze data from multiple worksheets efficiently?",
                "Explain the concept of array formulas and provide an example of when they're useful."
            ],
            "problem_solving": [
                "You have a dataset with duplicate entries. Walk me through your approach to identify and remove duplicates while preserving the original data.",
                "How would you create a dynamic report that automatically updates when new data is added to your source?",
                "Describe how you would handle a scenario where you need to combine data from multiple Excel files with different structures."
            ]
        }
    
    async def get_initial_greeting(self) -> str:
        """Get the initial greeting message"""
        greeting_prompt = f"""
        You are a professional Excel interviewer conducting a mock interview. 
        
        Candidate information: {self.candidate_info}
        
        Provide a warm, professional greeting that:
        1. Introduces yourself as an AI Excel interviewer
        2. Explains the interview process (15-20 minutes, various Excel topics)
        3. Asks the candidate to introduce themselves and their Excel experience
        
        Keep it conversational and encouraging. Start the interview naturally.
        """
        
        try:
            greeting = await self.llm_client.generate_response(greeting_prompt)
            return greeting
        except Exception as e:
            logger.error(f"Error generating initial greeting: {str(e)}")
            return """Hello! I'm your AI Excel interviewer. I'll be conducting a mock interview to assess your Excel proficiency. 

The interview will take about 15-20 minutes and cover various Excel topics from basic functions to advanced features. Don't worry - this is a learning experience, and I'll provide feedback along the way.

Could you please introduce yourself and tell me about your Excel experience? What's your primary use case for Excel?"""
    
    async def process_response(self, candidate_message: str) -> Dict:
        """Process candidate response and determine next action"""
        try:
            # Add response to history
            self.interview_state["responses"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "candidate_message": candidate_message,
                "phase": self.interview_state["phase"]
            })
            
            # Determine next action based on current state
            if self.interview_state["phase"] == "introduction":
                return await self._handle_introduction_response(candidate_message)
            elif self.interview_state["phase"] == "questions":
                return await self._handle_question_response(candidate_message)
            elif self.interview_state["phase"] == "conclusion":
                return await self._handle_conclusion_response(candidate_message)
            else:
                return await self._generate_next_question()
                
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return {
                "message": "I apologize, but I encountered an error processing your response. Could you please try again?",
                "type": "error"
            }
    
    async def _handle_introduction_response(self, response: str) -> Dict:
        """Handle introduction phase response"""
        # Analyze response to determine skill level
        skill_level = self._assess_initial_skill_level(response)
        self.interview_state["current_skill_level"] = skill_level
        
        # Move to questions phase
        self.interview_state["phase"] = "questions"
        
        # Generate transition message and first question
        transition_prompt = f"""
        The candidate has introduced themselves: "{response}"
        Assessed skill level: {skill_level}
        
        Provide a brief transition message acknowledging their experience and then ask the first Excel question appropriate for their skill level.
        
        Keep it encouraging and professional. Make the first question relevant to their stated experience level.
        """
        
        try:
            message = await self.llm_client.generate_response(transition_prompt)
            return {
                "message": message,
                "type": "question",
                "phase": "questions",
                "skill_level": skill_level
            }
        except Exception as e:
            logger.error(f"Error in introduction transition: {str(e)}")
            return await self._generate_next_question()
    
    async def _handle_question_response(self, response: str) -> Dict:
        """Handle question phase response"""
        # Evaluate the response
        current_question = self.interview_state["responses"][-2]["agent_message"] if len(self.interview_state["responses"]) > 1 else "Previous question"
        evaluation = self.evaluator.evaluate_response(current_question, response, self.interview_state)
        
        # Update performance tracking
        self.interview_state["performance_tracking"]["total_questions"] += 1
        if evaluation["overall_score"] >= 60:
            self.interview_state["performance_tracking"]["correct_answers"] += 1
        
        # Add evaluation to response history
        self.interview_state["responses"][-1]["evaluation"] = evaluation
        
        # Check if interview should continue or end
        if self.interview_state["questions_asked"] >= 5:
            return await self._transition_to_conclusion(evaluation)
        else:
            return await self._generate_follow_up_response(evaluation)
    
    async def _handle_conclusion_response(self, response: str) -> Dict:
        """Handle conclusion phase response"""
        return await self._generate_final_summary()
    
    async def _assess_initial_skill_level(self, response: str) -> str:
        """Assess initial skill level from introduction"""
        response_lower = response.lower()
        
        advanced_indicators = ["vba", "macro", "power query", "power pivot", "advanced", "complex"]
        intermediate_indicators = ["pivot table", "vlookup", "index match", "conditional formatting"]
        beginner_indicators = ["basic", "beginner", "learning", "new to"]
        
        if any(indicator in response_lower for indicator in advanced_indicators):
            return "advanced"
        elif any(indicator in response_lower for indicator in intermediate_indicators):
            return "intermediate"
        else:
            return "beginner"
    
    async def _generate_next_question(self) -> Dict:
        """Generate the next question based on current state"""
        skill_level = self.interview_state["current_skill_level"]
        questions_asked = self.interview_state["questions_asked"]
        
        # Select appropriate question category
        if questions_asked == 0:
            category = "basic_functions"
        elif questions_asked == 1:
            category = "lookup_functions"
        elif questions_asked == 2:
            category = "data_analysis"
        elif questions_asked == 3:
            category = "advanced_features" if skill_level != "beginner" else "data_analysis"
        else:
            category = "problem_solving"
        
        # Get question from bank
        questions = self.question_bank.get(category, self.question_bank["basic_functions"])
        question = questions[0] if questions else "Tell me about your experience with Excel functions."
        
        # Update state
        self.interview_state["questions_asked"] += 1
        
        # Store question in responses
        self.interview_state["responses"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent_message": question,
            "phase": self.interview_state["phase"],
            "category": category
        })
        
        return {
            "message": question,
            "type": "question",
            "category": category,
            "question_number": self.interview_state["questions_asked"]
        }
    
    async def _generate_follow_up_response(self, evaluation: Dict) -> Dict:
        """Generate follow-up response based on evaluation"""
        feedback = evaluation.get("feedback", "")
        
        follow_up_prompt = f"""
        The candidate just answered an Excel question. Here's the evaluation:
        - Overall Score: {evaluation['overall_score']}/100
        - Feedback: {feedback}
        - Skill Category: {evaluation.get('skill_category', 'general')}
        
        Provide a brief acknowledgment of their answer, give constructive feedback, and then ask the next question.
        Keep it encouraging and professional. If they did well, acknowledge it. If they need improvement, provide helpful guidance.
        """
        
        try:
            response = await self.llm_client.generate_response(follow_up_prompt)
            return {
                "message": response,
                "type": "feedback_and_question",
                "evaluation": evaluation
            }
        except Exception as e:
            logger.error(f"Error generating follow-up: {str(e)}")
            return await self._generate_next_question()
    
    async def _transition_to_conclusion(self, evaluation: Dict) -> Dict:
        """Transition to conclusion phase"""
        self.interview_state["phase"] = "conclusion"
        
        conclusion_prompt = f"""
        The Excel interview is coming to an end. The candidate has answered {self.interview_state['questions_asked']} questions.
        Their overall performance shows: {self.interview_state['performance_tracking']['correct_answers']}/{self.interview_state['performance_tracking']['total_questions']} strong answers.
        
        Provide a professional conclusion message that:
        1. Acknowledges their participation
        2. Indicates that you'll be preparing a detailed feedback report
        3. Asks if they have any questions about Excel or the interview process
        
        Keep it positive and encouraging.
        """
        
        try:
            message = await self.llm_client.generate_response(conclusion_prompt)
            return {
                "message": message,
                "type": "conclusion",
                "phase": "conclusion"
            }
        except Exception as e:
            logger.error(f"Error in conclusion transition: {str(e)}")
            return {
                "message": "Thank you for completing the Excel interview! I'll now prepare a detailed feedback report for you. Do you have any questions about Excel or the interview process?",
                "type": "conclusion",
                "phase": "conclusion"
            }
    
    async def _generate_final_summary(self) -> Dict:
        """Generate final interview summary"""
        return await self.generate_final_report({})
    
    async def generate_final_report(self, session_state: Dict) -> Dict:
        """Generate comprehensive final feedback report"""
        try:
            performance = self.interview_state["performance_tracking"]
            responses = self.interview_state["responses"]
            
            # Calculate overall performance
            total_questions = performance["total_questions"]
            correct_answers = performance["correct_answers"]
            success_rate = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Analyze skill demonstrations
            skill_analysis = self._analyze_skill_demonstrations(responses)
            
            # Generate report
            report = {
                "interview_summary": {
                    "total_questions": total_questions,
                    "correct_answers": correct_answers,
                    "success_rate": round(success_rate, 1),
                    "overall_performance": self._get_performance_level(success_rate),
                    "skill_level_assessed": self.interview_state["current_skill_level"]
                },
                "skill_analysis": skill_analysis,
                "strengths": self._identify_strengths(responses),
                "areas_for_improvement": self._identify_improvement_areas(responses),
                "recommendations": self._generate_recommendations(success_rate, skill_analysis),
                "detailed_feedback": self._generate_detailed_feedback(responses)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating final report: {str(e)}")
            return {
                "interview_summary": {
                    "total_questions": 0,
                    "correct_answers": 0,
                    "success_rate": 0,
                    "overall_performance": "Unable to assess",
                    "skill_level_assessed": "Unknown"
                },
                "error": "Unable to generate complete report"
            }
    
    def _analyze_skill_demonstrations(self, responses: List[Dict]) -> Dict:
        """Analyze skill demonstrations across different categories"""
        categories = ["basic_functions", "lookup_functions", "data_analysis", "advanced_features", "problem_solving"]
        analysis = {}
        
        for category in categories:
            category_responses = [r for r in responses if r.get("category") == category]
            if category_responses:
                evaluations = [r.get("evaluation", {}) for r in category_responses if r.get("evaluation")]
                if evaluations:
                    avg_score = sum(e.get("overall_score", 0) for e in evaluations) / len(evaluations)
                    analysis[category] = {
                        "average_score": round(avg_score, 1),
                        "questions_answered": len(category_responses),
                        "performance_level": self._get_performance_level(avg_score)
                    }
        
        return analysis
    
    def _identify_strengths(self, responses: List[Dict]) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        for response in responses:
            evaluation = response.get("evaluation", {})
            if evaluation.get("overall_score", 0) >= 80:
                category = evaluation.get("skill_category", "general")
                if category not in strengths:
                    strengths.append(category.replace("_", " ").title())
        
        return strengths if strengths else ["General Excel knowledge"]
    
    def _identify_improvement_areas(self, responses: List[Dict]) -> List[str]:
        """Identify areas for improvement"""
        improvement_areas = []
        
        for response in responses:
            evaluation = response.get("evaluation", {})
            if evaluation.get("overall_score", 0) < 60:
                category = evaluation.get("skill_category", "general")
                if category not in improvement_areas:
                    improvement_areas.append(category.replace("_", " ").title())
        
        return improvement_areas if improvement_areas else ["Overall Excel proficiency"]
    
    def _generate_recommendations(self, success_rate: float, skill_analysis: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if success_rate < 60:
            recommendations.append("Focus on fundamental Excel functions and formulas")
            recommendations.append("Practice with real-world Excel scenarios")
        elif success_rate < 80:
            recommendations.append("Enhance advanced Excel features knowledge")
            recommendations.append("Practice complex data analysis tasks")
        else:
            recommendations.append("Consider Excel certification programs")
            recommendations.append("Explore advanced automation with VBA and macros")
        
        return recommendations
    
    def _generate_detailed_feedback(self, responses: List[Dict]) -> List[Dict]:
        """Generate detailed feedback for each response"""
        detailed_feedback = []
        
        for response in responses:
            if response.get("evaluation"):
                evaluation = response["evaluation"]
                detailed_feedback.append({
                    "question": response.get("agent_message", "Question not recorded"),
                    "candidate_response": response.get("candidate_message", ""),
                    "score": evaluation.get("overall_score", 0),
                    "feedback": evaluation.get("feedback", ""),
                    "skill_category": evaluation.get("skill_category", "general")
                })
        
        return detailed_feedback
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Satisfactory"
        else:
            return "Needs Improvement"
