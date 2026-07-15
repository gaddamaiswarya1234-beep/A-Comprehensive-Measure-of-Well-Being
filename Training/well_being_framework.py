import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class WellBeingDimension(Enum):
    PHYSICAL = "physical"
    MENTAL = "mental"
    SOCIAL = "social"
    FINANCIAL = "financial"
    ENVIRONMENTAL = "environmental"
    PURPOSE = "purpose"
    LEARNING = "learning"

class RiskLevel(Enum):
    CRITICAL = "critical"
    LOW = "low"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"

@dataclass
class MetricScore:
    name: str
    score: float
    weight: float
    description: str
    raw_value: Optional[float] = None
    unit: Optional[str] = None

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight

@dataclass
class DimensionResult:
    dimension: WellBeingDimension
    metrics: List[MetricScore]
    overall_score: float
    risk_level: RiskLevel
    recommendations: List[str]

@dataclass
class WellBeingProfile:
    person_id: str
    assessment_date: str
    dimensions: Dict[WellBeingDimension, DimensionResult]
    composite_score: float
    overall_risk: RiskLevel
    summary: str
    action_plan: List[str]

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "assessment_date": self.assessment_date,
            "composite_score": round(self.composite_score, 2),
            "overall_risk": self.overall_risk.value,
            "summary": self.summary,
            "dimensions": {
                dim.value: {
                    "score": round(res.overall_score, 2),
                    "risk": res.risk_level.value,
                    "metrics": [
                        {
                            "name": m.name,
                            "score": round(m.score, 2),
                            "weight": m.weight,
                            "raw_value": m.raw_value,
                            "unit": m.unit
                        } for m in res.metrics
                    ],
                    "recommendations": res.recommendations
                }
                for dim, res in self.dimensions.items()
            },
            "action_plan": self.action_plan
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

class ScoringEngine:
    @staticmethod
    def normalize(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
        if max_val == min_val:
            return 50
        normalized = (value - min_val) / (max_val - min_val) * 100
        normalized = max(0, min(100, normalized))
        return 100 - normalized if invert else normalized

    @staticmethod
    def bmi_score(bmi: float) -> float:
        if 18.5 <= bmi <= 24.9:
            return 100
        elif bmi < 18.5:
            return ScoringEngine.normalize(bmi, 10, 18.5, invert=True)
        else:
            return ScoringEngine.normalize(bmi, 24.9, 40, invert=True)

    @staticmethod
    def sleep_score(hours: float) -> float:
        if 7 <= hours <= 9:
            return 100
        elif hours < 7:
            return ScoringEngine.normalize(hours, 0, 7)
        else:
            return ScoringEngine.normalize(hours, 9, 12, invert=True)

    @staticmethod
    def risk_level(score: float) -> RiskLevel:
        if score >= 81: return RiskLevel.EXCELLENT
        elif score >= 61: return RiskLevel.GOOD
        elif score >= 41: return RiskLevel.MODERATE
        elif score >= 21: return RiskLevel.LOW
        else: return RiskLevel.CRITICAL

class WellBeingAssessor:
    def __init__(self):
        self.scorer = ScoringEngine()
        self.dimension_weights = {
            WellBeingDimension.PHYSICAL: 0.20,
            WellBeingDimension.MENTAL: 0.20,
            WellBeingDimension.SOCIAL: 0.15,
            WellBeingDimension.FINANCIAL: 0.15,
            WellBeingDimension.ENVIRONMENTAL: 0.10,
            WellBeingDimension.PURPOSE: 0.10,
            WellBeingDimension.LEARNING: 0.10,
        }

    def assess_physical(self, bmi: float, sleep_hours: float, exercise_minutes_week: float, steps_per_day: float, chronic_conditions: int = 0) -> DimensionResult:
        metrics = [
            MetricScore("BMI", self.scorer.bmi_score(bmi), 0.25, "Body Mass Index", bmi, "kg/m2"),
            MetricScore("Sleep Quality", self.scorer.sleep_score(sleep_hours), 0.25, "Average nightly sleep", sleep_hours, "hours"),
            MetricScore("Physical Activity", min(100, exercise_minutes_week / 150 * 100), 0.25, "Weekly exercise minutes", exercise_minutes_week, "min/week"),
            MetricScore("Daily Movement", min(100, steps_per_day / 10000 * 100), 0.15, "Average daily steps", steps_per_day, "steps"),
            MetricScore("Health Conditions", max(0, 100 - chronic_conditions * 20), 0.10, "Number of chronic conditions", chronic_conditions, "count")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if bmi < 18.5 or bmi > 24.9:
            recommendations.append("Consult a nutritionist for weight management")
        if sleep_hours < 7:
            recommendations.append("Establish a consistent sleep schedule; aim for 7-9 hours")
        if exercise_minutes_week < 150:
            recommendations.append("Increase to at least 150 min/week of moderate exercise")
        if steps_per_day < 7000:
            recommendations.append("Aim for 7,000-10,000 steps daily")
        if not recommendations:
            recommendations.append("Maintain current healthy lifestyle habits")
        return DimensionResult(WellBeingDimension.PHYSICAL, metrics, score, risk, recommendations)

    def assess_mental(self, stress_level: float, anxiety_score: float, depression_score: float, mindfulness_minutes: float, life_satisfaction: float) -> DimensionResult:
        metrics = [
            MetricScore("Stress Management", self.scorer.normalize(stress_level, 10, 0), 0.25, "Perceived stress scale (0-10)", stress_level, "0-10"),
            MetricScore("Anxiety Level", self.scorer.normalize(anxiety_score, 21, 0), 0.20, "GAD-7 anxiety score", anxiety_score, "0-21"),
            MetricScore("Mood Stability", self.scorer.normalize(depression_score, 27, 0), 0.20, "PHQ-9 depression score", depression_score, "0-27"),
            MetricScore("Mindfulness Practice", min(100, mindfulness_minutes / 20 * 100), 0.15, "Daily mindfulness minutes", mindfulness_minutes, "min/day"),
            MetricScore("Life Satisfaction", life_satisfaction * 10, 0.20, "Life satisfaction (0-10)", life_satisfaction, "0-10")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if stress_level > 6:
            recommendations.append("Practice stress reduction techniques (breathing, meditation)")
        if anxiety_score > 10:
            recommendations.append("Consider speaking with a mental health professional")
        if depression_score > 10:
            recommendations.append("Seek professional support for mood management")
        if mindfulness_minutes < 10:
            recommendations.append("Start with 10 minutes daily mindfulness practice")
        if not recommendations:
            recommendations.append("Continue mental wellness practices; consider journaling")
        return DimensionResult(WellBeingDimension.MENTAL, metrics, score, risk, recommendations)

    def assess_social(self, close_relationships: int, social_frequency: float, community_belonging: float, support_network_size: int, loneliness_score: float) -> DimensionResult:
        metrics = [
            MetricScore("Close Relationships", min(100, close_relationships / 5 * 100), 0.25, "Number of close relationships", close_relationships, "count"),
            MetricScore("Social Engagement", min(100, social_frequency / 3 * 100), 0.20, "Social activities per week", social_frequency, "times/week"),
            MetricScore("Community Belonging", community_belonging * 10, 0.20, "Sense of belonging (0-10)", community_belonging, "0-10"),
            MetricScore("Support Network", min(100, support_network_size / 10 * 100), 0.20, "People you can rely on", support_network_size, "count"),
            MetricScore("Loneliness", self.scorer.normalize(loneliness_score, 10, 0), 0.15, "Loneliness scale (0-10)", loneliness_score, "0-10")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if close_relationships < 3:
            recommendations.append("Invest time in building 2-3 deep relationships")
        if social_frequency < 2:
            recommendations.append("Schedule at least 2 social activities per week")
        if community_belonging < 5:
            recommendations.append("Join a community group or volunteer organization")
        if loneliness_score > 5:
            recommendations.append("Reach out to existing contacts; consider support groups")
        if not recommendations:
            recommendations.append("Nurture existing relationships; mentor someone new")
        return DimensionResult(WellBeingDimension.SOCIAL, metrics, score, risk, recommendations)

    def assess_financial(self, savings_rate: float, debt_to_income: float, emergency_months: float, income_stability: float, financial_literacy: float) -> DimensionResult:
        metrics = [
            MetricScore("Savings Rate", min(100, savings_rate * 5), 0.25, "Percentage of income saved", savings_rate, "%"),
            MetricScore("Debt Burden", self.scorer.normalize(debt_to_income, 0.5, 0, invert=True), 0.25, "Debt-to-income ratio", debt_to_income, "ratio"),
            MetricScore("Emergency Fund", min(100, emergency_months * 20), 0.20, "Months of expenses covered", emergency_months, "months"),
            MetricScore("Income Stability", income_stability * 10, 0.15, "Income stability (0-10)", income_stability, "0-10"),
            MetricScore("Financial Literacy", financial_literacy * 10, 0.15, "Financial knowledge (0-10)", financial_literacy, "0-10")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if savings_rate < 0.15:
            recommendations.append("Aim to save at least 15-20% of income")
        if debt_to_income > 0.36:
            recommendations.append("Create a debt reduction plan; prioritize high-interest debt")
        if emergency_months < 3:
            recommendations.append("Build emergency fund to cover 3-6 months of expenses")
        if financial_literacy < 6:
            recommendations.append("Take a financial literacy course or read personal finance books")
        if not recommendations:
            recommendations.append("Consider investment diversification and retirement planning")
        return DimensionResult(WellBeingDimension.FINANCIAL, metrics, score, risk, recommendations)

    def assess_environmental(self, air_quality_index: float, green_space_access: float, housing_satisfaction: float, commute_quality: float, noise_level: float) -> DimensionResult:
        metrics = [
            MetricScore("Air Quality", self.scorer.normalize(air_quality_index, 200, 0), 0.25, "Local AQI (lower is better)", air_quality_index, "AQI"),
            MetricScore("Green Access", min(100, green_space_access / 30 * 100), 0.20, "Minutes to nearest green space", green_space_access, "min"),
            MetricScore("Housing Quality", housing_satisfaction * 10, 0.25, "Housing satisfaction (0-10)", housing_satisfaction, "0-10"),
            MetricScore("Commute Experience", commute_quality * 10, 0.20, "Commute satisfaction (0-10)", commute_quality, "0-10"),
            MetricScore("Noise Exposure", self.scorer.normalize(noise_level, 80, 30, invert=True), 0.10, "Average noise level (dB)", noise_level, "dB")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if air_quality_index > 100:
            recommendations.append("Use air purifiers; check air quality before outdoor activities")
        if green_space_access > 15:
            recommendations.append("Find closer green spaces or create indoor plant environment")
        if housing_satisfaction < 6:
            recommendations.append("Identify housing improvements or consider relocation")
        if commute_quality < 5:
            recommendations.append("Explore remote work options or alternative commute methods")
        if not recommendations:
            recommendations.append("Maintain environmental wellness; add plants to living space")
        return DimensionResult(WellBeingDimension.ENVIRONMENTAL, metrics, score, risk, recommendations)

    def assess_purpose(self, goal_clarity: float, values_alignment: float, contribution_sense: float, progress_toward_goals: float, meaning_in_work: float) -> DimensionResult:
        metrics = [
            MetricScore("Goal Clarity", goal_clarity * 10, 0.25, "Clarity of life goals (0-10)", goal_clarity, "0-10"),
            MetricScore("Values Alignment", values_alignment * 10, 0.25, "Actions aligned with values (0-10)", values_alignment, "0-10"),
            MetricScore("Contribution", contribution_sense * 10, 0.20, "Sense of contributing to others (0-10)", contribution_sense, "0-10"),
            MetricScore("Goal Progress", progress_toward_goals * 10, 0.15, "Progress toward goals (0-10)", progress_toward_goals, "0-10"),
            MetricScore("Work Meaning", meaning_in_work * 10, 0.15, "Meaning derived from work (0-10)", meaning_in_work, "0-10")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if goal_clarity < 5:
            recommendations.append("Write a personal mission statement; define 1-year goals")
        if values_alignment < 6:
            recommendations.append("Audit weekly activities against core values")
        if contribution_sense < 5:
            recommendations.append("Volunteer or mentor to increase sense of contribution")
        if progress_toward_goals < 5:
            recommendations.append("Break goals into monthly milestones; track progress")
        if not recommendations:
            recommendations.append("Set stretch goals; share your purpose with others")
        return DimensionResult(WellBeingDimension.PURPOSE, metrics, score, risk, recommendations)

    def assess_learning(self, new_skills_monthly: float, reading_hours: float, curiosity_level: float, skill_diversity: float, learning_satisfaction: float) -> DimensionResult:
        metrics = [
            MetricScore("Skill Acquisition", min(100, new_skills_monthly / 2 * 100), 0.25, "New skills learned per month", new_skills_monthly, "count/month"),
            MetricScore("Reading Habit", min(100, reading_hours / 10 * 100), 0.20, "Weekly reading hours", reading_hours, "hours/week"),
            MetricScore("Curiosity", curiosity_level * 10, 0.20, "Curiosity level (0-10)", curiosity_level, "0-10"),
            MetricScore("Skill Diversity", min(100, skill_diversity / 5 * 100), 0.20, "Number of distinct skill areas", skill_diversity, "count"),
            MetricScore("Growth Satisfaction", learning_satisfaction * 10, 0.15, "Satisfaction with personal growth (0-10)", learning_satisfaction, "0-10")
        ]
        score = sum(m.weighted_score for m in metrics)
        risk = self.scorer.risk_level(score)
        recommendations = []
        if new_skills_monthly < 1:
            recommendations.append("Commit to learning one new skill per month")
        if reading_hours < 3:
            recommendations.append("Start with 30 minutes of reading daily")
        if curiosity_level < 5:
            recommendations.append("Explore new topics outside your comfort zone")
        if skill_diversity < 3:
            recommendations.append("Learn skills from different domains (technical, creative, social)")
        if not recommendations:
            recommendations.append("Teach what you have learned; start a learning project")
        return DimensionResult(WellBeingDimension.LEARNING, metrics, score, risk, recommendations)

    def full_assessment(self, person_id: str, date: str, **kwargs) -> WellBeingProfile:
        dimensions = {}
        dimensions[WellBeingDimension.PHYSICAL] = self.assess_physical(
            kwargs.get('bmi', 24), kwargs.get('sleep_hours', 7), kwargs.get('exercise_minutes_week', 150),
            kwargs.get('steps_per_day', 8000), kwargs.get('chronic_conditions', 0)
        )
        dimensions[WellBeingDimension.MENTAL] = self.assess_mental(
            kwargs.get('stress_level', 5), kwargs.get('anxiety_score', 5), kwargs.get('depression_score', 4),
            kwargs.get('mindfulness_minutes', 10), kwargs.get('life_satisfaction', 7)
        )
        dimensions[WellBeingDimension.SOCIAL] = self.assess_social(
            kwargs.get('close_relationships', 4), kwargs.get('social_frequency', 2), kwargs.get('community_belonging', 6),
            kwargs.get('support_network_size', 5), kwargs.get('loneliness_score', 4)
        )
        dimensions[WellBeingDimension.FINANCIAL] = self.assess_financial(
            kwargs.get('savings_rate', 0.15), kwargs.get('debt_to_income', 0.30), kwargs.get('emergency_months', 4),
            kwargs.get('income_stability', 7), kwargs.get('financial_literacy', 6)
        )
        dimensions[WellBeingDimension.ENVIRONMENTAL] = self.assess_environmental(
            kwargs.get('air_quality_index', 50), kwargs.get('green_space_access', 10), kwargs.get('housing_satisfaction', 7),
            kwargs.get('commute_quality', 6), kwargs.get('noise_level', 50)
        )
        dimensions[WellBeingDimension.PURPOSE] = self.assess_purpose(
            kwargs.get('goal_clarity', 6), kwargs.get('values_alignment', 7), kwargs.get('contribution_sense', 6),
            kwargs.get('progress_toward_goals', 5), kwargs.get('meaning_in_work', 6)
        )
        dimensions[WellBeingDimension.LEARNING] = self.assess_learning(
            kwargs.get('new_skills_monthly', 1), kwargs.get('reading_hours', 5), kwargs.get('curiosity_level', 7),
            kwargs.get('skill_diversity', 4), kwargs.get('learning_satisfaction', 7)
        )
        composite = sum(dimensions[dim].overall_score * self.dimension_weights[dim] for dim in WellBeingDimension)
        overall_risk = self.scorer.risk_level(composite)
        lowest_dim = min(dimensions.items(), key=lambda x: x[1].overall_score)
        highest_dim = max(dimensions.items(), key=lambda x: x[1].overall_score)
        summary = f"Overall well-being score: {composite:.1f}/100 ({overall_risk.value.upper()}). Strongest area: {highest_dim[0].value.title()} ({highest_dim[1].overall_score:.1f}). Area needing attention: {lowest_dim[0].value.title()} ({lowest_dim[1].overall_score:.1f})."
        action_plan = []
        for dim, result in sorted(dimensions.items(), key=lambda x: x[1].overall_score)[:3]:
            if result.risk_level in [RiskLevel.CRITICAL, RiskLevel.LOW, RiskLevel.MODERATE]:
                action_plan.append(f"[{dim.value.title()}] {result.recommendations[0]}")
        return WellBeingProfile(person_id, date, dimensions, composite, overall_risk, summary, action_plan)

class WellBeingTracker:
    def __init__(self):
        self.history: List[WellBeingProfile] = []

    def add_assessment(self, profile: WellBeingProfile):
        self.history.append(profile)

    def trend_analysis(self, dimension: WellBeingDimension) -> Dict:
        if len(self.history) < 2:
            return {"error": "Need at least 2 assessments for trend analysis"}
        scores = [p.dimensions[dimension].overall_score for p in self.history]
        dates = [p.assessment_date for p in self.history]
        if len(scores) >= 2:
            slope = (scores[-1] - scores[0]) / (len(scores) - 1)
            trend = "improving" if slope > 1 else "declining" if slope < -1 else "stable"
        else:
            slope = 0
            trend = "stable"
        return {"dimension": dimension.value, "scores": scores, "dates": dates, "trend": trend, "slope": round(slope, 2), "change": round(scores[-1] - scores[0], 1), "current": round(scores[-1], 1)}

    def generate_report(self) -> str:
        if not self.history:
            return "No assessment history available."
        latest = self.history[-1]
        report = []
        report.append("=" * 60)
        report.append("WELL-BEING ASSESSMENT REPORT")
        report.append("=" * 60)
        report.append(f"Person ID: {latest.person_id}")
        report.append(f"Assessment Date: {latest.assessment_date}")
        report.append(f"Total Assessments: {len(self.history)}")
        report.append("")
        report.append(f"COMPOSITE SCORE: {latest.composite_score:.1f}/100")
        report.append(f"OVERALL STATUS: {latest.overall_risk.value.upper()}")
        report.append("")
        report.append("-" * 60)
        report.append("DIMENSIONAL ANALYSIS")
        report.append("-" * 60)
        for dim in WellBeingDimension:
            result = latest.dimensions[dim]
            report.append(f"\n{dim.value.upper()}")
            report.append(f"  Score: {result.overall_score:.1f}/100 | Status: {result.risk_level.value.upper()}")
            report.append(f"  Metrics:")
            for m in result.metrics:
                report.append(f"    - {m.name}: {m.score:.1f} (weight: {m.weight})")
            report.append(f"  Recommendations:")
            for rec in result.recommendations:
                report.append(f"    -> {rec}")
        report.append("")
        report.append("-" * 60)
        report.append("PRIORITY ACTION PLAN")
        report.append("-" * 60)
        for i, action in enumerate(latest.action_plan, 1):
            report.append(f"{i}. {action}")
        if len(self.history) >= 2:
            report.append("")
            report.append("-" * 60)
            report.append("TREND ANALYSIS")
            report.append("-" * 60)
            for dim in WellBeingDimension:
                trend = self.trend_analysis(dim)
                report.append(f"{dim.value.title()}: {trend['trend'].upper()} (change: {trend['change']:+.1f})")
        return "\n".join(report)