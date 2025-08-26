from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DigitalTransformationProject(models.Model):
    """
    Model to manage digital transformation projects
    """
    _name = 'dt.project'
    _description = 'Digital Transformation Project'
    _order = 'create_date desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Info
    name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Description')
    client_id = fields.Many2one(
        'dt.client.company',
        string='Client Company',
        required=True,
        ondelete='cascade'
    )

    # Dates
    start_date = fields.Date(string='Start Date')
    target_completion_date = fields.Date(string='Target Completion Date')
    actual_completion_date = fields.Date(string='Actual Completion Date')

    # Progress & State
    progress = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    # Budget
    budget = fields.Float(string='Budget')
    estimated_budget = fields.Monetary(string='Estimated Budget', currency_field='currency_id')
    actual_budget = fields.Monetary(string='Actual Budget Used', currency_field='currency_id')

    # Relationships
    phase_ids = fields.One2many('dt.project.phase', 'project_id', string='Phases')
    milestone_ids = fields.One2many('dt.project.milestone', 'project_id', string='Milestones')
    deliverable_ids = fields.One2many('dt.project.deliverable', 'project_id', string='Deliverables')
    consultant_ids = fields.Many2many(
        'dt.consultant', 
        'dt_project_consultant_rel',  # relational table for Assigned Consultants
        'project_id', 
        'consultant_id',
        string='Assigned Consultants'
    )
    assessment_id = fields.Many2one('dt.assessment', string='Assessment', domain="[('client_id','=',client_id)]")

    # New fields added to match views
    project_manager_id = fields.Many2one('dt.consultant', string='Project Manager')
    risk_level = fields.Char(string='Risk Level')
    duration_months = fields.Integer(string='Duration (Months)')
    currency_id = fields.Many2one('res.currency', string='Currency')
    team_members = fields.Many2many(
        'dt.consultant', 
        'dt_project_team_rel',  # relational table for Team Members
        'project_id', 
        'consultant_id',
        string='Team Members'
    )
    objectives = fields.Text(string='Objectives')
    scope = fields.Text(string='Scope')
    risks = fields.Text(string='Risks')
    mitigation_plans = fields.Text(string='Mitigation Plans')
    satisfaction_score = fields.Float(string='Satisfaction Score')
    client_feedback = fields.Text(string='Client Feedback')
    responsible_id = fields.Many2one('dt.consultant', string='Responsible')
    sequence = fields.Integer(string='Sequence', default=1)
    end_date = fields.Date(string='End Date')
    due_date = fields.Date(string='Due Date')
    delivery_date = fields.Date(string='Delivery Date')
    document_url = fields.Char(string='Document URL')
    target_date = fields.Date(string='Target Date')
    actual_date = fields.Date(string='Actual Date')
    importance = fields.Selection([('low','Low'), ('medium','Medium'), ('high','High')], string='Importance')
    
    
    
    # Chatter / Followers
    # message_follower_ids = fields.Many2many(
    #     'res.partner', 
    #     'project_follower_rel', 
    #     'project_id', 
    #     'partner_id', 
    #     string='Followers'
    # )
    # activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities',
    #                            domain=[('res_model', '=', 'dt.project')])
    # message_ids = fields.One2many('mail.message', 'res_id', string='Messages',
    #                           domain=[('model', '=', 'dt.project')])

    # Computed
    phase_count = fields.Integer(
        string='Number of Phases',
        compute='_compute_phase_count',
        store=True
    )

    # ------------------ COMPUTES ------------------

    @api.depends('phase_ids', 'phase_ids.progress')
    def _compute_progress(self):
        """Compute overall project progress as average of phase progress."""
        for record in self:
            if record.phase_ids:
                record.progress = sum(record.phase_ids.mapped('progress')) / len(record.phase_ids)
            else:
                record.progress = 0.0

    @api.depends('phase_ids')
    def _compute_phase_count(self):
        for record in self:
            record.phase_count = len(record.phase_ids)

    # ------------------ CONSTRAINTS ------------------

    @api.constrains('start_date', 'target_completion_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.target_completion_date:
                if record.target_completion_date < record.start_date:
                    raise ValidationError("Target completion date cannot be earlier than start date.")

    # ------------------ ACTIONS ------------------

    def action_start(self):
        for record in self:
            record.state = 'in_progress'

    def action_complete(self):
        for record in self:
            record.state = 'completed'
            record.actual_completion_date = fields.Date.today()

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'

    # ------------------ UTILITIES ------------------

    def _generate_project_phases(self):
        """
        Utility to generate standard phases for a project
        """
        standard_phases = [
            ('Initiation', 10),
            ('Planning', 20),
            ('Design', 15),
            ('Development', 35),
            ('Testing', 15),
            ('Deployment', 5)
        ]
        for phase_name, weight in standard_phases:
            self.env['dt.project.phase'].create({
                'name': phase_name,
                'project_id': self.id,
                'weight': weight,
                'sequence': len(self.phase_ids) + 1,
            })


class ProjectPhase(models.Model):
    """Phases within a project"""
    _name = 'dt.project.phase'
    _description = 'Project Phase'
    _order = 'sequence'

    name = fields.Char(string='Phase Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=1)
    project_id = fields.Many2one('dt.project', string='Project', required=True, ondelete='cascade')
    weight = fields.Integer(string='Weight (%)', default=0)
    progress = fields.Float(string='Progress %', default=0.0)

    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], string='Status', default='not_started')

    task_ids = fields.One2many('dt.project.task', 'phase_id', string='Tasks')
    responsible_id = fields.Many2one('dt.consultant', string='Responsible')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')


class ProjectMilestone(models.Model):
    """Milestones in a project"""
    _name = 'dt.project.milestone'
    _description = 'Project Milestone'

    name = fields.Char(string='Milestone', required=True)
    description = fields.Text(string='Description')
    due_date = fields.Date(string='Due Date')
    achieved = fields.Boolean(string='Achieved', default=False)
    project_id = fields.Many2one('dt.project', string='Project', required=True, ondelete='cascade')
    target_date = fields.Date(string='Target Date')
    actual_date = fields.Date(string='Actual Date')
    importance = fields.Selection([('low','Low'), ('medium','Medium'), ('high','High')], string='Importance')
    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], string='Status', default='not_started')


class ProjectDeliverable(models.Model):
    """Deliverables of a project"""
    _name = 'dt.project.deliverable'
    _description = 'Project Deliverable'

    name = fields.Char(string='Deliverable', required=True)
    description = fields.Text(string='Description')
    due_date = fields.Date(string='Due Date')
    delivered = fields.Boolean(string='Delivered', default=False)
    project_id = fields.Many2one('dt.project', string='Project', required=True, ondelete='cascade')
    responsible_id = fields.Many2one('dt.consultant', string='Responsible')
    delivery_date = fields.Date(string='Delivery Date')
    document_url = fields.Char(string='Document URL')
    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], string='Status', default='not_started')


class ProjectTask(models.Model):
    """Tasks within a project phase"""
    _name = 'dt.project.task'
    _description = 'Project Task'

    name = fields.Char(string='Task', required=True)
    description = fields.Text(string='Description')
    assigned_to = fields.Many2one('dt.consultant', string='Assigned Consultant')
    phase_id = fields.Many2one('dt.project.phase', string='Phase', required=True, ondelete='cascade')

    state = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('blocked', 'Blocked')
    ], string='Status', default='todo')
