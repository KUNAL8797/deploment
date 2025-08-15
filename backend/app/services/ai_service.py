import google.generativeai as genai
from typing import Dict, Tuple, Optional
import os
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiAIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.prompts_used = []  # Track prompts for documentation
        
    async def refine_idea(self, title: str, description: str, stage: str) -> str:
        """
        AI Prompt #1: Business Idea Refinement
        Context: Transform user's raw idea into professional, compelling pitch
        """
        prompt = f"""You are an expert business consultant and startup advisor with 20+ years of experience. 

Your task: Transform this business idea into a compelling, investor-ready pitch.

BUSINESS IDEA:
Title: {title}
Description: {description}
Development Stage: {stage}

Please provide a refined pitch that includes:

1. **Problem Statement**: What problem does this solve?
2. **Solution Overview**: How does your idea address the problem?
3. **Value Proposition**: What unique value do you offer?
4. **Target Market**: Who are your primary customers?
5. **Competitive Advantage**: What makes this different/better?
6. **Implementation Approach**: Key steps to bring this to market
7. **Market Opportunity**: Size and potential of the market

Keep it professional, compelling, and concise (300-400 words). Focus on clarity and investor appeal.

Format as structured paragraphs, not bullet points."""

        try:
            self.prompts_used.append({
                "prompt_type": "idea_refinement",
                "context": f"Refining idea '{title}' at {stage} stage",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            refined_content = response.text.strip()
            
            logger.info(f"Successfully refined idea: {title}")
            return refined_content
            
        except Exception as e:
            logger.error(f"AI refinement error for '{title}': {e}")
            return self._fallback_refinement(title, description, stage)
    
    async def generate_feasibility_analysis(self, idea_data: Dict) -> Tuple[float, float, float]:
        """
        AI Prompt #2: Feasibility Scoring Analysis
        Context: Analyze business feasibility across multiple dimensions
        """
        prompt = f"""You are a senior business analyst specializing in startup feasibility assessment.

BUSINESS IDEA TO ANALYZE:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Refined Pitch: {idea_data.get('ai_refined_pitch', '')}
Development Stage: {idea_data.get('development_stage', '')}

TASK: Provide feasibility scores (1.0-10.0 scale) for these dimensions:

1. **MARKET POTENTIAL** (1=no market, 10=huge market opportunity)
   - Market size and growth potential
   - Customer demand and willingness to pay
   - Market accessibility and timing
   - Competitive landscape favorability

2. **TECHNICAL COMPLEXITY** (1=very simple, 10=extremely complex)
   - Technical feasibility and innovation required
   - Required expertise and skill level
   - Infrastructure and technology needs
   - Development time and complexity

3. **RESOURCE REQUIREMENTS** (1=minimal resources, 10=massive resources)
   - Initial capital requirements
   - Ongoing operational costs
   - Team size and expertise needed
   - Time to market and breakeven

Respond ONLY in valid JSON format:
{{
    "market_potential": X.X,
    "technical_complexity": X.X,
    "resource_requirements": X.X,
    "analysis": {{
        "market_reasoning": "Brief analysis of market opportunity",
        "technical_reasoning": "Brief analysis of technical feasibility",
        "resource_reasoning": "Brief analysis of resource needs"
    }}
}}

Be precise with scores - use decimal places (e.g., 7.3, not just 7)."""

        try:
            self.prompts_used.append({
                "prompt_type": "feasibility_analysis",
                "context": f"Analyzing feasibility for '{idea_data.get('title', 'unknown')}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "")
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "")
            analysis = json.loads(response_text)
            
            # Validate and clamp scores
            market_score = max(1.0, min(10.0, float(analysis["market_potential"])))
            technical_score = max(1.0, min(10.0, float(analysis["technical_complexity"])))
            resource_score = max(1.0, min(10.0, float(analysis["resource_requirements"])))
            
            logger.info(f"AI feasibility analysis completed: M:{market_score}, T:{technical_score}, R:{resource_score}")
            return (market_score, technical_score, resource_score)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"JSON parsing error in feasibility analysis: {e}")
            return await self._fallback_scoring(idea_data)
        except Exception as e:
            logger.error(f"AI feasibility analysis error: {e}")
            return await self._fallback_scoring(idea_data)
    
    async def generate_market_insights(self, title: str, description: str) -> str:
        """
        AI Prompt #3: Market Analysis and Competitive Landscape
        Context: Provide market insights and competitive analysis
        """
        prompt = f"""You are a market research expert specializing in competitive intelligence and market analysis.

BUSINESS IDEA:
Title: {title}
Description: {description}

Provide comprehensive market insights including:

1. **Market Size & Growth**: Current market size and growth projections
2. **Key Competitors**: Main competitors and their market position
3. **Market Trends**: Relevant industry trends and opportunities
4. **Customer Segments**: Primary and secondary customer segments
5. **Market Entry Strategy**: Recommended approach to enter this market
6. **Potential Challenges**: Key market barriers and challenges

Keep analysis concise but insightful (200-250 words). Focus on actionable intelligence."""

        try:
            self.prompts_used.append({
                "prompt_type": "market_insights",
                "context": f"Generating market analysis for '{title}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Market insights generation error: {e}")
            return "Market analysis temporarily unavailable. Please try again later."
    
    async def generate_risk_assessment(self, idea_data: Dict) -> str:
        """
        AI Prompt #4: Risk Analysis and Mitigation Strategies
        Context: Identify potential risks and suggest mitigation approaches
        """
        prompt = f"""You are a risk management consultant with expertise in startup risk assessment.

BUSINESS IDEA:
Title: {idea_data.get('title', '')}
Refined Pitch: {idea_data.get('ai_refined_pitch', '')}
Market Potential: {idea_data.get('market_potential', 'Unknown')}
Technical Complexity: {idea_data.get('technical_complexity', 'Unknown')}

Identify and analyze key risks:

1. **Market Risks**: Customer adoption, competition, market timing
2. **Technical Risks**: Development challenges, technology limitations
3. **Financial Risks**: Funding needs, revenue model, cash flow
4. **Operational Risks**: Team, execution, scaling challenges

For each risk category, provide:
- Risk level (Low/Medium/High)
- Specific risk factors
- Mitigation strategies

Format as structured analysis (250-300 words)."""

        try:
            self.prompts_used.append({
                "prompt_type": "risk_assessment",
                "context": f"Analyzing risks for '{idea_data.get('title', 'unknown')}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Risk assessment generation error: {e}")
            return "Risk analysis temporarily unavailable. Please try again later."
    
    async def generate_implementation_roadmap(self, idea_data: Dict) -> str:
        """
        AI Prompt #5: Strategic Implementation Roadmap
        Context: Create actionable step-by-step implementation plan
        """
        stage = idea_data.get('development_stage', 'concept')
        
        prompt = f"""You are a strategic planning consultant specializing in startup execution roadmaps.

BUSINESS IDEA:
Title: {idea_data.get('title', '')}
Current Stage: {stage}
Feasibility Scores: Market {idea_data.get('market_potential', 'N/A')}, Technical {idea_data.get('technical_complexity', 'N/A')}, Resources {idea_data.get('resource_requirements', 'N/A')}

Create a strategic implementation roadmap with:

**Phase 1 (Next 3 months):**
- Immediate priorities and actions
- Key milestones and deliverables

**Phase 2 (Months 4-6):**
- Development and validation activities
- Resource requirements

**Phase 3 (Months 7-12):**
- Market entry and scaling activities
- Success metrics and KPIs

Consider the current development stage and adjust recommendations accordingly.
Be specific and actionable (250-300 words)."""

        try:
            self.prompts_used.append({
                "prompt_type": "implementation_roadmap",
                "context": f"Creating roadmap for '{idea_data.get('title', 'unknown')}' at {stage} stage",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Implementation roadmap generation error: {e}")
            return "Implementation roadmap temporarily unavailable. Please try again later."
    
    async def optimize_idea_title(self, title: str, description: str) -> str:
        """
        AI Prompt #6: Title Optimization for Market Appeal
        Context: Optimize idea titles for clarity and market appeal
        """
        prompt = f"""You are a branding expert specializing in startup naming and positioning.

CURRENT IDEA:
Title: {title}
Description: {description}

Suggest 3 optimized title alternatives that are:
1. Clear and descriptive
2. Memorable and marketable
3. Professional yet engaging
4. SEO-friendly

For each suggestion, provide brief reasoning.

Format:
**Option 1:** [Title]
*Reasoning:* [Brief explanation]

**Option 2:** [Title]
*Reasoning:* [Brief explanation]

**Option 3:** [Title]
*Reasoning:* [Brief explanation]

Keep total response under 200 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "title_optimization",
                "context": f"Optimizing title '{title}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Title optimization error: {e}")
            return f"Title optimization temporarily unavailable. Current title '{title}' is acceptable."
    
    def get_prompts_documentation(self) -> list:
        """Return all prompts used for assignment documentation"""
        return self.prompts_used
    
    async def _generate_content_async(self, prompt: str):
        """Async wrapper for Gemini content generation with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.model.generate_content, prompt)
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Gemini API attempt {attempt + 1} failed, retrying: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _fallback_refinement(self, title: str, description: str, stage: str) -> str:
        """Fallback refinement when AI fails"""
        return f"""**{title}** - Professional Business Concept

**Problem & Solution:**
{description}

**Development Status:** Currently in {stage} stage

**Key Highlights:**
- Addresses market need through innovative approach
- Scalable business model with growth potential
- Strategic development roadmap aligned with market opportunities

**Next Steps:**
- Conduct detailed market validation
- Develop minimum viable product
- Establish strategic partnerships

*Note: This is a structured presentation of your original idea. AI enhancement temporarily unavailable.*"""
    
    async def _fallback_scoring(self, idea_data: Dict) -> Tuple[float, float, float]:
        """Fallback scoring when AI analysis fails"""
        # Provide reasonable default scores based on stage
        stage = idea_data.get('development_stage', 'concept')
        
        stage_adjustments = {
            'concept': (6.0, 5.0, 6.0),
            'research': (7.0, 6.0, 7.0),
            'prototype': (7.5, 4.0, 7.5),
            'testing': (8.0, 3.0, 8.0),
            'launch': (8.5, 2.0, 8.5)
        }
        
        return stage_adjustments.get(stage, (6.0, 5.0, 6.0))

# Global service instance
ai_service = GeminiAIService()