from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Assessment(models.Model):
    """Digital Maturity Assessment Model"""
    _name = 'dt.assessment'
    _description = 'Digital Transformation Assessment'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assessment_date desc'

    name = fields.Char(string='Assessment Name', required=True, tracking=True)
    client_id = fields.Many2one('dt.client.company', string='Client', required=True, tracking=True)
    consultant_id = fields.Many2one('dt.consultant', string='Lead Consultant', required=True)
    assessment_date = fields.Date(string='Assessment Date', default=fields.Date.context_today, required=True)
    completion_date = fields.Date(string='Completion Date')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Assessment Categories
    technology_score = fields.Float(string='Technology Score', compute='_compute_category_scores', store=True,
                                    help="Current technology infrastructure score")
    process_score = fields.Float(string='Process Score', compute='_compute_category_scores', store=True,
                                 help="Business process maturity score")
    people_score = fields.Float(string='People & Skills Score', compute='_compute_category_scores', store=True,
                                help="Team capabilities and skills score")
    culture_score = fields.Float(string='Culture Score', compute='_compute_category_scores', store=True,
                                 help="Digital culture and change readiness score")
    
    total_score = fields.Float(string='Total Score', compute='_compute_total_score', store=True)
    
    # Detailed Assessment
    assessment_line_ids = fields.One2many('dt.assessment.line', 'assessment_id', string='Assessment Questions')
    
    # Recommendations
    recommendations = fields.Html(string='Recommendations')
    priority_areas = fields.Text(string='Priority Areas')
    estimated_timeline = fields.Char(string='Estimated Timeline')
    estimated_budget = fields.Float(string='Estimated Budget')
    
    # Progress Tracking
    progress = fields.Float(string='Assessment Progress', compute='_compute_progress')
    
    @api.depends('technology_score', 'process_score', 'people_score', 'culture_score')
    def _compute_total_score(self):
        for record in self:
            scores = [record.technology_score, record.process_score, record.people_score, record.culture_score]
            valid_scores = [s for s in scores if s > 0]
            record.total_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    @api.depends('assessment_line_ids', 'assessment_line_ids.answer')
    def _compute_progress(self):
        for record in self:
            total_questions = len(record.assessment_line_ids)
            answered_questions = len(record.assessment_line_ids.filtered('answer'))
            record.progress = (answered_questions / total_questions * 100) if total_questions else 0

    @api.depends('assessment_line_ids', 'assessment_line_ids.score', 'assessment_line_ids.category')
    def _compute_category_scores(self):
        for record in self:
            tech_scores = [l.score for l in record.assessment_line_ids if l.category == 'technology']
            proc_scores = [l.score for l in record.assessment_line_ids if l.category == 'process']
            people_scores = [l.score for l in record.assessment_line_ids if l.category == 'people']
            culture_scores = [l.score for l in record.assessment_line_ids if l.category == 'culture']

            record.technology_score = (sum(tech_scores) / len(tech_scores))*10 if tech_scores else 0.0
            record.process_score = sum(proc_scores) / len(proc_scores)*10 if proc_scores else 0.0
            record.people_score = sum(people_scores) / len(people_scores)*10 if people_scores else 0.0
            record.culture_score = sum(culture_scores) / len(culture_scores)*10 if culture_scores else 0.0

    def action_start_assessment(self):
        self.state = 'in_progress'
        self._generate_assessment_questions()
    
    def action_submit_review(self):
        if self.progress < 100:
            raise ValidationError("Please complete all assessment questions before submitting.")
        self.state = 'review'
    
    def action_complete(self):
        self.state = 'completed'
        self.completion_date = fields.Date.context_today(self)
        self._generate_recommendations()
    
    def _generate_assessment_questions(self):
        """Generate assessment questions based on templates"""
        template_questions = self.env['dt.assessment.template'].search([('active', '=', True)])
        for question in template_questions:
            self.env['dt.assessment.line'].create({
                'assessment_id': self.id,
                'question_id': question.id,
                'category': question.category,
                'question_text': question.question_text,
                'weight': question.weight,
            })
    
    def _generate_recommendations(self):
        """Generate recommendations based on scores"""
        recommendations = []
        if self.technology_score < 50:
            recommendations.append("• Urgent technology infrastructure upgrade needed")
        if self.process_score < 50:
            recommendations.append("• Business process optimization required")
        if self.people_score < 50:
            recommendations.append("• Skills development and training programs essential")
        if self.culture_score < 50:
            recommendations.append("• Change management and culture transformation needed")
        
        self.recommendations = '<br/>'.join(recommendations)


class AssessmentLine(models.Model):
    """Assessment Question Line"""
    _name = 'dt.assessment.line'
    _description = 'Assessment Question Line'
    
    assessment_id = fields.Many2one('dt.assessment', string='Assessment', required=True, ondelete='cascade')
    question_id = fields.Many2one('dt.assessment.template', string='Question Template')
    category = fields.Selection([
        ('technology', 'Technology'),
        ('process', 'Process'),
        ('people', 'People & Skills'),
        ('culture', 'Culture'),
    ], string='Category', required=True)
    
    question_text = fields.Text(string='Question', required=True)
    weight = fields.Float(string='Weight', default=1.0)
    answer = fields.Selection([
        ('1', 'Strongly Disagree (1)'),
        ('2', 'Disagree (2)'),
        ('3', 'Neutral (3)'),
        ('4', 'Agree (4)'),
        ('5', 'Strongly Agree (5)'),
    ], string='Answer')
    score = fields.Float(string='Score', compute='_compute_score', store=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('answer', 'weight')
    def _compute_score(self):
        for record in self:
            record.score = (float(record.answer) * record.weight) if record.answer else 0.0


class AssessmentTemplate(models.Model):
    """Assessment Question Template"""
    _name = 'dt.assessment.template'
    _description = 'Assessment Question Template'
    
    name = fields.Char(string='Question Name', required=True)
    category = fields.Selection([
        ('technology', 'Technology'),
        ('process', 'Process'),
        ('people', 'People & Skills'),
        ('culture', 'Culture'),
    ], string='Category', required=True)
    question_text = fields.Text(string='Question Text', required=True)
    weight = fields.Float(string='Weight', default=1.0)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
