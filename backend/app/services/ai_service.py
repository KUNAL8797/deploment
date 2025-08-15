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
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Updated to latest model
        self.prompts_used = []  # Track prompts for documentation
        
    async def refine_idea(self, title: str, description: str, stage: str) -> str:
        """
        AI Prompt #1: Business Idea Refinement
        Context: Transform user's raw idea into professional, compelling pitch
        """
        prompt = f"""You are an expert business consultant and startup advisor with 20+ years of experience helping entrepreneurs develop compelling business pitches.

Your task: Transform this business idea into a comprehensive, investor-ready pitch with clear structure and professional formatting.

BUSINESS IDEA:
Title: {title}
Description: {description}
Development Stage: {stage}

Please provide a detailed business analysis with the following structure:

**Executive Summary**
Provide a compelling 2-3 sentence overview of the business opportunity that hooks investors.

**Problem Statement**
- What specific problem does this solve?
- Who experiences this problem and how often?
- How significant is the pain point and current solutions' limitations?

**Solution Overview**
- How does your solution uniquely address the problem?
- What makes this solution different from existing alternatives?
- Key features, benefits, and competitive advantages

**Market Opportunity**
- Target market size and addressable segments
- Market trends and growth potential (include specific data if possible)
- Customer demographics, behavior, and willingness to pay

**Competitive Advantage**
- What differentiates this from direct and indirect competitors?
- Barriers to entry for potential competitors
- Unique value proposition and positioning strategy

**Business Model**
- Revenue streams and monetization strategy
- Pricing model and unit economics
- Scalability and growth potential

**Implementation Strategy**
- Key development phases and milestones
- Resource requirements (team, technology, capital)
- Timeline expectations and critical path activities
- Success metrics and KPIs

**Market Entry & Growth**
- Go-to-market strategy and customer acquisition
- Marketing and distribution channels
- Scaling plan and expansion opportunities

Use clear headers with ** formatting, bullet points for lists, and structured formatting for maximum readability. Make it investor-ready and professional.

Keep the total response between 600-900 words with clear section breaks and engaging, specific language."""

        try:
            self.prompts_used.append({
                "prompt_type": "idea_refinement",
                "context": f"Refining idea '{title}' at {stage} stage",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            refined_content = response.text.strip()
            
            # Ensure proper formatting
            if not refined_content.startswith('**'):
                refined_content = f"**Enhanced Business Pitch**\n\n{refined_content}"
            
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
        prompt = f"""You are a senior business analyst specializing in startup feasibility assessment with expertise in market analysis, technical evaluation, and resource planning.

BUSINESS IDEA TO ANALYZE:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Refined Pitch: {idea_data.get('ai_refined_pitch', '')}
Development Stage: {idea_data.get('development_stage', '')}

TASK: Provide precise feasibility scores (1.0-10.0 scale) for these dimensions:

1. **MARKET POTENTIAL** (1.0=no market opportunity, 10.0=massive market opportunity)
   - Market size and growth trajectory
   - Customer demand intensity and willingness to pay
   - Market accessibility and timing favorability
   - Competitive landscape and positioning opportunities

2. **TECHNICAL COMPLEXITY** (1.0=very simple to implement, 10.0=extremely complex)
   - Technical feasibility and innovation requirements
   - Required expertise, skills, and technology stack
   - Infrastructure needs and development complexity
   - Integration challenges and scalability factors

3. **RESOURCE REQUIREMENTS** (1.0=minimal resources needed, 10.0=massive resources required)
   - Initial capital and funding requirements
   - Ongoing operational costs and burn rate
   - Team size, expertise, and hiring needs
   - Time to market and break-even timeline

Respond ONLY in valid JSON format:
{{
    "market_potential": X.X,
    "technical_complexity": X.X,
    "resource_requirements": X.X,
    "analysis": {{
        "market_reasoning": "Detailed analysis of market opportunity and potential",
        "technical_reasoning": "Assessment of technical challenges and complexity factors",
        "resource_reasoning": "Evaluation of capital, human, and time resource needs"
    }}
}}

Be precise with scores - use decimal places (e.g., 7.3, 8.7) based on careful analysis."""

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
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```","").strip()
            
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
    
    async def generate_market_insights(self, title: str, description: str, refined_pitch: str = None) -> str:
        """
        AI Prompt #3: Comprehensive Market Analysis and Competitive Intelligence
        Context: Provide detailed market insights and competitive landscape analysis
        """
        prompt = f"""You are a senior market research analyst with expertise in competitive intelligence, market sizing, and industry trend analysis.

BUSINESS IDEA FOR ANALYSIS:
Title: {title}
Description: {description}
Refined Pitch: {refined_pitch or 'Not available'}

Provide comprehensive market intelligence covering:

**Market Size & Growth Potential**
- Total Addressable Market (TAM) estimates with data sources
- Serviceable Addressable Market (SAM) analysis
- Current market growth rate and 5-year projections
- Key market drivers and growth catalysts

**Customer Segmentation & Analysis**
- Primary target customer segments with demographics
- Customer pain points and unmet needs analysis
- Buying behavior, decision factors, and price sensitivity
- Customer acquisition costs and lifetime value estimates

**Competitive Landscape**
- Direct competitors and their market share/positioning
- Indirect competitors and substitute solutions
- Competitive strengths, weaknesses, and market gaps
- Opportunities for differentiation and competitive advantage

**Market Trends & Dynamics**
- Industry trends supporting this business opportunity
- Technology trends and adoption patterns
- Regulatory, social, or economic factors impacting the market
- Emerging opportunities and market shifts

**Go-to-Market Strategy Insights**
- Recommended market entry approach and timing
- Optimal pricing strategy and model considerations
- Distribution channels and partnership opportunities
- Marketing channels and customer acquisition strategies

**Market Challenges & Barriers**
- Key market entry barriers and competitive threats
- Regulatory or compliance challenges
- Market education and adoption timeline considerations
- Potential risks and mitigation strategies

Provide specific, actionable insights with concrete examples and data points where possible. Structure with clear headers and bullet points. Total length: 500-700 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "comprehensive_market_insights",
                "context": f"Generating detailed market analysis for '{title}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Market insights generation error: {e}")
            return self._fallback_market_insights(title, description)
    
    async def generate_risk_assessment(self, idea_data: Dict) -> str:
        """
        AI Prompt #4: Comprehensive Risk Analysis and Mitigation Framework
        Context: Identify potential risks across all business dimensions and suggest mitigation strategies
        """
        prompt = f"""You are a senior risk management consultant specializing in startup risk assessment and mitigation strategy development.

BUSINESS IDEA FOR RISK ANALYSIS:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Refined Pitch: {idea_data.get('ai_refined_pitch', '')}
Development Stage: {idea_data.get('development_stage', '')}
Market Potential Score: {idea_data.get('market_potential', 'N/A')}/10
Technical Complexity Score: {idea_data.get('technical_complexity', 'N/A')}/10
Resource Requirements Score: {idea_data.get('resource_requirements', 'N/A')}/10

Conduct comprehensive risk analysis across all critical business dimensions:

**Market & Commercial Risks**
- Customer adoption challenges and market acceptance risks
- Competitive threats and market saturation concerns
- Market timing risks and demand volatility
- Pricing pressure and revenue model viability
Risk Level: [High/Medium/Low] | Mitigation Strategies: [Specific actions]

**Technical & Operational Risks**
- Development challenges and technical feasibility concerns
- Technology scalability and performance limitations
- Integration complexity and system reliability risks
- Quality control and product delivery challenges
Risk Level: [High/Medium/Low] | Mitigation Strategies: [Specific actions]

**Financial & Resource Risks**
- Funding availability and cash flow management
- Cost overruns and budget control challenges
- Revenue generation timeline and break-even risks
- Investment return and profitability concerns
Risk Level: [High/Medium/Low] | Mitigation Strategies: [Specific actions]

**Team & Execution Risks**
- Key talent acquisition and retention challenges
- Team scaling and management complexity
- Skills gaps and expertise requirements
- Leadership and decision-making risks
Risk Level: [High/Medium/Low] | Mitigation Strategies: [Specific actions]

**Strategic & External Risks**
- Regulatory changes and compliance requirements
- Economic conditions and market disruptions
- Strategic partnership and vendor dependencies
- Intellectual property and legal protection risks
Risk Level: [High/Medium/Low] | Mitigation Strategies: [Specific actions]

**Early Warning Indicators & Monitoring**
- Key metrics to track for each risk category
- Warning signs and trigger points
- Regular review and assessment framework
- Contingency planning recommendations

For each risk category, provide specific risk factors, likelihood assessment, potential impact, and actionable mitigation strategies. Total length: 600-800 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "comprehensive_risk_assessment",
                "context": f"Analyzing business risks for '{idea_data.get('title', 'unknown')}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Risk assessment generation error: {e}")
            return self._fallback_risk_assessment(idea_data)
    
    async def generate_implementation_roadmap(self, idea_data: Dict) -> str:
        """
        AI Prompt #5: Strategic Implementation Roadmap with Detailed Action Plans
        Context: Create comprehensive, actionable implementation plan with timelines and milestones
        """
        stage = idea_data.get('development_stage', 'concept')
        
        prompt = f"""You are a strategic planning consultant specializing in startup execution roadmaps and operational planning.

BUSINESS IDEA FOR ROADMAP DEVELOPMENT:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Current Stage: {stage}
Market Potential: {idea_data.get('market_potential', 'N/A')}/10
Technical Complexity: {idea_data.get('technical_complexity', 'N/A')}/10
Resource Requirements: {idea_data.get('resource_requirements', 'N/A')}/10

Create a comprehensive 12-month strategic implementation roadmap:

**Phase 1: Foundation & Validation (Months 1-3)**
- Primary objectives and critical deliverables
- Market validation and customer discovery activities
- Technical feasibility assessment and prototype development
- Team building and key hiring priorities
- Initial funding and resource acquisition
- Success metrics: [Specific, measurable outcomes]
- Budget estimate: [Resource requirements]

**Phase 2: Development & Iteration (Months 4-6)**
- Product/service development priorities and milestones
- Customer feedback integration and iteration cycles
- Technology infrastructure setup and scaling preparation
- Marketing strategy development and brand building
- Partnership development and strategic alliances
- Success metrics: [Specific, measurable outcomes]
- Budget estimate: [Resource requirements]

**Phase 3: Launch Preparation (Months 7-9)**
- Go-to-market strategy execution and channel development
- Sales process optimization and team scaling
- Marketing campaign launch and customer acquisition
- Operations scaling and quality assurance systems
- Legal, compliance, and intellectual property protection
- Success metrics: [Specific, measurable outcomes]
- Budget estimate: [Resource requirements]

**Phase 4: Market Entry & Growth (Months 10-12)**
- Official product/service launch and market penetration
- Customer acquisition scaling and retention optimization
- Performance monitoring, analytics, and optimization
- Revenue scaling and profitability pathway
- Expansion planning and next-phase preparation
- Success metrics: [Specific, measurable outcomes]
- Budget estimate: [Resource requirements]

**Critical Success Factors & Dependencies**
- Key assumptions and validation requirements
- Critical path activities and potential bottlenecks
- Resource optimization strategies and cost management
- Risk mitigation measures and contingency plans

**Implementation Guidelines**
- Weekly and monthly milestone tracking
- Decision points and pivot considerations
- Stakeholder communication and reporting framework
- Resource allocation and budget management approach

Adjust recommendations based on the current development stage ({stage}). Be specific and actionable with concrete timelines, responsibilities, and measurable outcomes. Total length: 700-900 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "detailed_implementation_roadmap",
                "context": f"Creating 12-month roadmap for '{idea_data.get('title', 'unknown')}' at {stage} stage",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Implementation roadmap generation error: {e}")
            return self._fallback_implementation_roadmap(idea_data)
    
    async def optimize_idea_title(self, title: str, description: str) -> str:
        """
        AI Prompt #6: Title Optimization for Market Appeal and Brand Positioning
        Context: Optimize idea titles for clarity, market appeal, and brand positioning
        """
        prompt = f"""You are a branding expert and marketing strategist specializing in startup naming, positioning, and market communication.

CURRENT BUSINESS IDEA:
Title: {title}
Description: {description}

Analyze the current title and suggest 3 optimized alternatives that are:
1. Clear, descriptive, and immediately understandable
2. Memorable, marketable, and brandable
3. Professional yet engaging and modern
4. SEO-friendly and searchable
5. Differentiated from competitors

For each suggestion, provide:
- The optimized title
- Branding rationale and positioning benefits
- Target audience appeal analysis
- SEO and marketability advantages

Format your response as:

**Current Title Analysis:**
[Brief assessment of current title's strengths and weaknesses]

**Optimized Title Options:**

**Option 1:** [Optimized Title]
*Rationale:* [Detailed explanation of branding strategy, target appeal, and market positioning benefits]
*Advantages:* [Specific SEO, marketing, and brand benefits]

**Option 2:** [Optimized Title]
*Rationale:* [Detailed explanation of branding strategy, target appeal, and market positioning benefits]
*Advantages:* [Specific SEO, marketing, and brand benefits]

**Option 3:** [Optimized Title]
*Rationale:* [Detailed explanation of branding strategy, target appeal, and market positioning benefits]
*Advantages:* [Specific SEO, marketing, and brand benefits]

**Recommendation:**
[Which option you recommend and why, considering market positioning and brand strategy]

Keep total response under 400 words while being specific and actionable."""

        try:
            self.prompts_used.append({
                "prompt_type": "title_optimization_and_branding",
                "context": f"Optimizing and analyzing title '{title}' for market positioning",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Title optimization error: {e}")
            return self._fallback_title_optimization(title, description)
    
    def get_prompts_documentation(self) -> list:
        """Return all prompts used for assignment documentation"""
        return self.prompts_used
    
    async def _generate_content_async(self, prompt: str):
        """Async wrapper for Gemini content generation with retry logic and rate limiting"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.model.generate_content, prompt)
                
                # Validate response
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Gemini API failed after {max_retries} attempts: {e}")
                    raise e
                
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Gemini API attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
    
    def _fallback_refinement(self, title: str, description: str, stage: str) -> str:
        """Enhanced fallback refinement when AI fails"""
        return f"""**{title}** - Professional Business Concept

**Executive Summary**
{description}

**Current Development Status**
This innovative concept is currently in the {stage} stage, representing a compelling opportunity for strategic development and market entry.

**Key Value Proposition**
- Addresses identified market need through innovative approach
- Scalable business model with clear growth trajectory
- Strategic positioning for competitive advantage

**Market Opportunity**
- Significant market potential in target segments
- Growing demand for innovative solutions in this space
- Opportunity for early market entry and positioning

**Implementation Framework**
- Structured development approach aligned with current stage
- Clear milestone progression and success metrics
- Resource optimization for maximum market impact

**Next Steps**
- Comprehensive market validation and customer discovery
- Minimum viable product development and testing
- Strategic partnership evaluation and development

*Note: This is an enhanced presentation of your original concept. Full AI analysis temporarily unavailable - please try again later for complete professional refinement.*"""
    
    async def _fallback_scoring(self, idea_data: Dict) -> Tuple[float, float, float]:
        """Enhanced fallback scoring with stage-based intelligence"""
        stage = idea_data.get('development_stage', 'concept')
        title = idea_data.get('title', '').lower()
        description = idea_data.get('description', '').lower()
        
        # Base scores by development stage
        stage_scores = {
            'concept': (6.0, 5.5, 6.5),
            'research': (7.0, 6.0, 7.0),
            'prototype': (7.5, 4.5, 7.5),
            'testing': (8.0, 3.5, 8.0),
            'launch': (8.5, 2.5, 8.5)
        }
        
        base_market, base_tech, base_resource = stage_scores.get(stage, (6.0, 5.5, 6.5))
        
        # Adjust based on keywords
        if any(word in title or word in description for word in ['ai', 'artificial intelligence', 'machine learning', 'automation']):
            base_market += 1.0
            base_tech += 2.0
            base_resource += 1.5
        
        if any(word in title or word in description for word in ['mobile', 'app', 'platform', 'software']):
            base_market += 0.5
            base_tech += 1.0
            base_resource += 0.5
        
        # Clamp scores
        market = max(1.0, min(10.0, base_market))
        technical = max(1.0, min(10.0, base_tech))
        resource = max(1.0, min(10.0, base_resource))
        
        logger.info(f"Fallback scoring applied: M:{market}, T:{technical}, R:{resource}")
        return (market, technical, resource)
    
    def _fallback_market_insights(self, title: str, description: str) -> str:
        """Fallback market insights when AI analysis fails"""
        return f"""**Market Analysis for {title}**

**Market Opportunity**
Based on the business concept, this solution addresses a clear market need with potential for significant growth and customer adoption.

**Target Market**
- Primary customers likely include individuals and businesses seeking innovative solutions in this domain
- Market size appears substantial with room for new entrants and innovative approaches
- Customer segments show strong potential for early adoption and market penetration

**Competitive Landscape**
- Market contains established players but shows opportunities for differentiation
- Innovation potential suggests ability to capture market share through unique value proposition
- Competitive positioning can be strengthened through strategic feature development

**Growth Potential**
- Market trends indicate positive growth trajectory and increasing demand
- Technology adoption patterns support business model viability
- Expansion opportunities exist across multiple customer segments

**Strategic Recommendations**
- Focus on customer validation and product-market fit
- Develop strong brand positioning and market differentiation
- Consider strategic partnerships for market entry and scaling

*Note: This is a general market overview. Full AI market analysis temporarily unavailable - please try again later for comprehensive competitive intelligence.*"""
    
    def _fallback_risk_assessment(self, idea_data: Dict) -> str:
        """Fallback risk assessment when AI analysis fails"""
        title = idea_data.get('title', 'This Business Idea')
        stage = idea_data.get('development_stage', 'concept')
        
        return f"""**Risk Assessment for {title}**

**Market Risks - Medium Level**
- Customer adoption timeline may vary based on market readiness
- Competitive response could impact market positioning
- Market validation requirements need careful attention

**Technical Risks - Varies by Complexity**
- Development challenges typical for {stage} stage projects
- Technical feasibility should be validated through prototyping
- Integration requirements need thorough analysis

**Financial Risks - Standard Startup Profile**
- Funding requirements align with development stage expectations
- Revenue timeline dependent on market entry strategy
- Cash flow management critical for sustainability

**Operational Risks - Manageable**
- Team building and talent acquisition standard for stage
- Scaling challenges manageable with proper planning
- Quality control systems need early implementation

**Mitigation Strategies**
- Conduct thorough market validation before major investments
- Develop minimum viable product for early testing
- Establish clear milestones and success metrics
- Build strong advisory network and mentorship

*Note: This is a general risk overview. Full AI risk analysis temporarily unavailable - please try again later for comprehensive risk assessment.*"""
    # ... existing methods ...
    
    async def generate_market_insights(self, title: str, description: str, refined_pitch: str = None) -> str:
        """
        AI Prompt #3: Comprehensive Market Analysis and Competitive Intelligence
        Context: Provide detailed market insights and competitive landscape analysis
        """
        # Validate inputs
        if not title or not description:
            logger.warning("Missing title or description for market insights")
            return self._fallback_market_insights(title or "Unknown", description or "No description")
        
        prompt = f"""You are a senior market research analyst with expertise in competitive intelligence and market analysis.

BUSINESS IDEA FOR ANALYSIS:
Title: {title}
Description: {description}
Refined Pitch: {refined_pitch or 'Not available'}

Provide comprehensive market intelligence covering:

**Market Size & Growth Potential**
- Total Addressable Market (TAM) estimates
- Market growth rate and projections
- Key market drivers and opportunities

**Customer Segmentation**
- Primary target customer segments
- Customer pain points and needs
- Buying behavior and decision factors

**Competitive Landscape**
- Direct and indirect competitors
- Market positioning opportunities
- Competitive advantages and gaps

**Market Trends**
- Industry trends supporting this opportunity
- Technology adoption patterns
- Market timing considerations

**Go-to-Market Strategy**
- Recommended market entry approach
- Pricing strategy considerations
- Distribution and partnership opportunities

**Market Challenges**
- Key barriers and competitive threats
- Regulatory or compliance considerations
- Market education requirements

Provide specific, actionable insights with clear structure. Total length: 400-600 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "comprehensive_market_insights",
                "context": f"Generating detailed market analysis for '{title}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            result = response.text.strip()
            
            if not result or len(result) < 50:
                logger.warning(f"Short or empty market insights response for '{title}'")
                return self._fallback_market_insights(title, description)
            
            logger.info(f"Market insights generated successfully for '{title}' ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Market insights generation error for '{title}': {e}")
            return self._fallback_market_insights(title, description)
    
    async def generate_risk_assessment(self, idea_data: Dict) -> str:
        """
        AI Prompt #4: Comprehensive Risk Analysis and Mitigation Framework
        """
        # Validate input data
        if not idea_data or not idea_data.get('title'):
            logger.warning("Invalid idea data for risk assessment")
            return self._fallback_risk_assessment(idea_data or {})
        
        title = idea_data.get('title', 'Unknown Idea')
        prompt = f"""You are a senior risk management consultant specializing in startup risk assessment.

BUSINESS IDEA FOR RISK ANALYSIS:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Development Stage: {idea_data.get('development_stage', '')}
Market Potential Score: {idea_data.get('market_potential', 'N/A')}/10
Technical Complexity Score: {idea_data.get('technical_complexity', 'N/A')}/10

Conduct comprehensive risk analysis across critical business dimensions:

**Market & Commercial Risks**
- Customer adoption challenges and market acceptance
- Competitive threats and market saturation
- Market timing and demand volatility
Risk Level: [High/Medium/Low] | Mitigation Strategies

**Technical & Operational Risks**
- Development challenges and feasibility concerns
- Technology scalability and performance limitations
- Quality control and delivery challenges
Risk Level: [High/Medium/Low] | Mitigation Strategies

**Financial & Resource Risks**
- Funding availability and cash flow management
- Cost overruns and budget control
- Revenue generation and profitability timeline
Risk Level: [High/Medium/Low] | Mitigation Strategies

**Team & Execution Risks**
- Talent acquisition and retention
- Team scaling and management complexity
- Skills gaps and expertise requirements
Risk Level: [High/Medium/Low] | Mitigation Strategies

**Strategic & External Risks**
- Regulatory changes and compliance
- Market disruptions and economic factors
- Partnership dependencies and vendor risks
Risk Level: [High/Medium/Low] | Mitigation Strategies

For each category, provide specific risk factors, likelihood, impact, and actionable mitigation strategies. Total length: 400-600 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "comprehensive_risk_assessment",
                "context": f"Analyzing business risks for '{title}'",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            result = response.text.strip()
            
            if not result or len(result) < 50:
                logger.warning(f"Short or empty risk assessment response for '{title}'")
                return self._fallback_risk_assessment(idea_data)
            
            logger.info(f"Risk assessment generated successfully for '{title}' ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Risk assessment generation error for '{title}': {e}")
            return self._fallback_risk_assessment(idea_data)
    
    async def generate_implementation_roadmap(self, idea_data: Dict) -> str:
        """
        AI Prompt #5: Strategic Implementation Roadmap with Detailed Action Plans
        """
        # Validate input data
        if not idea_data or not idea_data.get('title'):
            logger.warning("Invalid idea data for implementation roadmap")
            return self._fallback_implementation_roadmap(idea_data or {})
        
        title = idea_data.get('title', 'Unknown Idea')
        stage = idea_data.get('development_stage', 'concept')
        
        prompt = f"""You are a strategic planning consultant specializing in startup execution roadmaps.

BUSINESS IDEA FOR ROADMAP DEVELOPMENT:
Title: {idea_data.get('title', '')}
Description: {idea_data.get('description', '')}
Current Stage: {stage}
Market Potential: {idea_data.get('market_potential', 'N/A')}/10
Technical Complexity: {idea_data.get('technical_complexity', 'N/A')}/10
Resource Requirements: {idea_data.get('resource_requirements', 'N/A')}/10

Create a comprehensive 12-month strategic implementation roadmap:

**Phase 1: Foundation & Validation (Months 1-3)**
- Primary objectives and critical deliverables
- Market validation and customer discovery activities
- Technical feasibility and prototype development
- Team building and key hiring priorities
- Success metrics and budget requirements

**Phase 2: Development & Iteration (Months 4-6)**
- Product/service development priorities
- Customer feedback integration and iterations
- Technology infrastructure and scaling prep
- Marketing strategy and brand development
- Success metrics and resource needs

**Phase 3: Launch Preparation (Months 7-9)**
- Go-to-market strategy execution
- Sales process and team scaling
- Marketing campaigns and customer acquisition
- Operations scaling and quality systems
- Success metrics and budget requirements

**Phase 4: Market Entry & Growth (Months 10-12)**
- Product launch and market penetration
- Customer acquisition scaling and retention
- Performance monitoring and optimization
- Revenue scaling and profitability path
- Success metrics and expansion planning

**Critical Success Factors**
- Key assumptions and validation requirements
- Critical path activities and bottlenecks
- Resource optimization and cost management
- Risk mitigation and contingency plans

Adjust recommendations based on current stage ({stage}). Be specific with timelines, responsibilities, and measurable outcomes. Total length: 500-700 words."""

        try:
            self.prompts_used.append({
                "prompt_type": "detailed_implementation_roadmap",
                "context": f"Creating 12-month roadmap for '{title}' at {stage} stage",
                "timestamp": datetime.now().isoformat()
            })
            
            response = await self._generate_content_async(prompt)
            result = response.text.strip()
            
            if not result or len(result) < 50:
                logger.warning(f"Short or empty roadmap response for '{title}'")
                return self._fallback_implementation_roadmap(idea_data)
            
            logger.info(f"Implementation roadmap generated successfully for '{title}' ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Implementation roadmap generation error for '{title}': {e}")
            return self._fallback_implementation_roadmap(idea_data)

    # Enhanced fallback methods
    def _fallback_market_insights(self, title: str, description: str) -> str:
        """Enhanced fallback market insights when AI analysis fails"""
        return f"""**Market Analysis for {title}**

**Market Opportunity**
Based on the business concept described, this solution addresses a clear market need with significant potential for growth and customer adoption in the current business environment.

**Target Market Segments**
- Primary customers likely include individuals and businesses seeking innovative solutions in this domain
- Market size appears substantial with room for new entrants and innovative approaches
- Customer segments demonstrate strong potential for early adoption and market penetration

**Competitive Landscape Assessment**
- Market contains established players but shows opportunities for differentiation through innovation
- Competitive positioning can be strengthened through strategic feature development and unique value proposition
- Market gaps exist that can be exploited through focused product development

**Growth Potential & Trends**
- Industry trends indicate positive growth trajectory and increasing demand for solutions in this space
- Technology adoption patterns and market dynamics support business model viability
- Expansion opportunities exist across multiple customer segments and geographic markets

**Strategic Market Entry Recommendations**
- Focus on comprehensive customer validation and achieving strong product-market fit
- Develop compelling brand positioning and clear market differentiation strategy
- Consider strategic partnerships for accelerated market entry and scaling opportunities
- Implement robust market feedback loops for continuous product improvement

*Note: This is a general market overview based on available information. Comprehensive AI market analysis temporarily unavailable - please try again later for detailed competitive intelligence and market sizing.*"""

    def _fallback_risk_assessment(self, idea_data: Dict) -> str:
        """Enhanced fallback risk assessment when AI analysis fails"""
        title = idea_data.get('title', 'This Business Idea')
        stage = idea_data.get('development_stage', 'concept')
        
        return f"""**Risk Assessment for {title}**

**Market Risks - Medium Level**
- Customer adoption timeline may vary based on market readiness and competitive landscape
- Market timing risks and potential demand volatility require careful monitoring
- Competitive response could impact market positioning and customer acquisition strategy

**Technical Risks - Stage-Appropriate Level**
- Development challenges typical for {stage} stage projects need thorough assessment
- Technical feasibility should be validated through systematic prototyping and testing
- Integration and scalability requirements need comprehensive analysis and planning

**Financial Risks - Standard Startup Profile**
- Funding requirements align with development stage expectations and market conditions
- Revenue timeline dependent on market entry strategy and customer acquisition effectiveness
- Cash flow management critical for sustainability during growth phases

**Operational Risks - Manageable with Planning**
- Team building and talent acquisition standard challenges for current stage
- Scaling challenges manageable with proper planning and phased approach
- Quality control systems need early implementation and continuous improvement

**Strategic Risks - Controllable Factors**
- Strategic positioning requires ongoing market analysis and competitive intelligence
- Partnership and vendor dependencies need risk mitigation and backup planning
- Long-term sustainability depends on market adaptation and continuous innovation

**Risk Mitigation Framework**
- Conduct thorough market validation before major capital investments
- Develop minimum viable product approach for early market testing and feedback
- Establish clear success metrics and regular milestone review processes
- Build strong advisory network and mentorship for strategic guidance

*Note: This is a general risk overview based on available information. Comprehensive AI risk analysis temporarily unavailable - please try again later for detailed risk assessment with specific mitigation strategies.*"""

    def _fallback_implementation_roadmap(self, idea_data: Dict) -> str:
        """Enhanced fallback implementation roadmap when AI analysis fails"""
        title = idea_data.get('title', 'This Business Idea')
        stage = idea_data.get('development_stage', 'concept')
        
        return f"""**12-Month Implementation Roadmap for {title}**

**Phase 1: Foundation & Validation (Months 1-3)**
- Comprehensive market validation and customer discovery research
- Competitive analysis and strategic positioning development
- Core team assembly and critical skill gap analysis
- Initial funding strategy and resource planning framework
- Technical feasibility assessment and prototype development initiation

**Phase 2: Development & Iteration (Months 4-6)**
- Minimum viable product development and testing cycles
- Technology infrastructure setup and scalability planning
- Brand development and comprehensive marketing strategy creation
- Early customer feedback integration and rapid iteration cycles
- Strategic partnership exploration and development activities

**Phase 3: Testing & Launch Preparation (Months 7-9)**
- Extensive beta testing and user feedback integration processes
- Product refinement and feature optimization based on market response
- Go-to-market strategy finalization and execution preparation
- Sales process development and team scaling initiatives
- Legal, compliance, and intellectual property protection measures

**Phase 4: Market Entry & Growth (Months 10-12)**
- Official market launch and comprehensive customer acquisition campaigns
- Performance monitoring, analytics implementation, and optimization
- Revenue generation scaling and clear path to profitability establishment
- Expansion planning and preparation for next growth phase
- Continuous improvement based on market performance and feedback

**Critical Success Factors & Implementation Guidelines**
- Customer-centric development approach with regular market feedback integration
- Agile methodology implementation with rapid iteration and adaptation capabilities
- Strong financial management and resource optimization throughout all phases
- Risk mitigation measures and contingency planning for potential challenges
- Measurable success metrics and regular progress assessment frameworks

**Key Performance Indicators by Phase**
- Phase 1: Market validation completion, team assembly, technical feasibility confirmation
- Phase 2: MVP completion, initial customer feedback, brand recognition establishment
- Phase 3: Beta testing success, go-to-market readiness, operational scaling preparation
- Phase 4: Market penetration metrics, revenue targets, customer acquisition costs

*Note: This is a general implementation framework based on best practices for {stage} stage ventures. Comprehensive AI strategic roadmap temporarily unavailable - please try again later for detailed phase-specific planning and resource allocation guidance.*"""

    def _fallback_implementation_roadmap(self, idea_data: Dict) -> str:
        """Fallback implementation roadmap when AI analysis fails"""
        title = idea_data.get('title', 'This Business Idea')
        stage = idea_data.get('development_stage', 'concept')
        
        return f"""**Implementation Roadmap for {title}**

**Phase 1: Foundation (Months 1-3)**
- Market validation and customer discovery
- Competitive analysis and positioning
- Team assembly and skill gap analysis
- Initial funding and resource planning

**Phase 2: Development (Months 4-6)**
- Minimum viable product development
- Technology infrastructure setup
- Brand development and marketing strategy
- Early customer feedback and iteration

**Phase 3: Testing & Refinement (Months 7-9)**
- Beta testing and user feedback integration
- Product refinement and feature optimization
- Go-to-market strategy finalization
- Strategic partnership development

**Phase 4: Launch & Scale (Months 10-12)**
- Market launch and customer acquisition
- Performance monitoring and optimization
- Revenue generation and growth tracking
- Expansion planning and next phase preparation

**Key Success Factors**
- Customer-centric development approach
- Agile methodology and rapid iteration
- Strong market feedback integration
- Sustainable business model validation

*Note: This is a general implementation framework. Full AI roadmap analysis temporarily unavailable - please try again later for detailed strategic planning.*"""
    
    def _fallback_title_optimization(self, title: str, description: str) -> str:
        """Fallback title optimization when AI analysis fails"""
        return f"""**Title Optimization Analysis**

**Current Title:** {title}
The current title provides a good foundation and is descriptive of the core concept.

**General Optimization Suggestions:**

**Option 1:** Enhanced version focusing on key benefits
*Rationale:* Emphasize primary value proposition for target audience
*Advantages:* Clear positioning and market appeal

**Option 2:** Solution-focused alternative highlighting outcomes
*Rationale:* Focus on results and customer benefits
*Advantages:* Strong customer connection and differentiation

**Option 3:** Market-positioned variant for competitive advantage
*Rationale:* Strategic positioning for market leadership
*Advantages:* Professional appeal and brand development potential

**Recommendation:**
Consider customer feedback and market testing to validate optimal title choice. The current title provides a solid foundation for brand development.

*Note: This is general guidance. Full AI title optimization temporarily unavailable - please try again later for specific recommendations.*"""
    # Add these methods to your existing GeminiAIService class



# Global service instance

ai_service = GeminiAIService()
