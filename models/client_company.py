# models/client_company.py
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ClientCompany(models.Model):
    """
    Extended partner model to handle consulting clients with digital transformation data
    """
    _name = 'dt.client.company'
    _description = 'Digital Transformation Client Company'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(
        string='Company Name',
        required=True,
        tracking=True,
        help="Name of the client company"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Contact',
        required=True,
        help="Link to the main contact in the partner database"
    )
    
    # Company Details
    industry_type = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail & E-commerce'),
        ('finance', 'Financial Services'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('technology', 'Technology'),
        ('construction', 'Construction'),
        ('logistics', 'Logistics & Transportation'),
        ('other', 'Other'),
    ], string='Industry', required=True, tracking=True)
    
    company_size = fields.Selection([
        ('startup', 'Startup (1-10 employees)'),
        ('small', 'Small (11-50 employees)'),
        ('medium', 'Medium (51-200 employees)'),
        ('large', 'Large (201-1000 employees)'),
        ('enterprise', 'Enterprise (1000+ employees)'),
    ], string='Company Size', required=True, tracking=True)
    
    annual_revenue = fields.Float(
        string='Annual Revenue',
        help="Annual revenue in company currency"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Current Technology Stack
    current_erp = fields.Char(
        string='Current ERP System',
        help="Current ERP system being used (if any)"
    )
    
    tech_stack = fields.Text(
        string='Current Technology Stack',
        help="Brief description of current technology infrastructure"
    )
    
    cloud_adoption = fields.Selection([
        ('none', 'No Cloud'),
        ('basic', 'Basic Cloud Services'),
        ('hybrid', 'Hybrid Cloud'),
        ('full', 'Full Cloud Native'),
    ], string='Cloud Adoption Level', default='none')
    
    # Digital Maturity Assessment
    digital_maturity_score = fields.Float(
        string='Digital Maturity Score',
        compute='_compute_digital_maturity_score',
        store=True,
        help="Overall digital maturity score (0-100)"
    )
    
    maturity_level = fields.Selection([
        ('beginner', 'Digital Beginner'),
        ('developing', 'Developing'),
        ('proficient', 'Proficient'),
        ('advanced', 'Advanced'),
        ('expert', 'Digital Expert'),
    ], string='Maturity Level', compute='_compute_maturity_level', store=True)
    
    # Assessment History 
    assessment_ids = fields.One2many(
        'dt.assessment',
        'client_id',
        string='Assessments'
    )
    
    assessment_count = fields.Integer(
        string='Assessment Count',
        compute='_compute_assessment_count',
        default=0
    )

    # 🔹 Latest Assessment Details (regardless of state)
    latest_assessment_date = fields.Date(
        string='Latest Assessment Date',
        compute='_compute_latest_assessment',
        store=True
    )

    latest_assessment_state = fields.Selection(
        string='Latest Assessment State',
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('review', 'Under Review'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        compute='_compute_latest_assessment',
        store=True
    )

    latest_assessment_score = fields.Float(
        string='Latest Total Score',
        compute='_compute_latest_assessment',
        store=True
    )

    # 🔹 Project Information
    project_ids = fields.One2many(
        'dt.project',
        'client_id',
        string='Transformation Projects'
    )
    
    project_count = fields.Integer(
        string='Project Count',
        compute='_compute_project_count',
        default=0
    )

    # 🔹 Latest Project Details
    latest_project_start_date = fields.Date(
        string='Latest Project Start Date',
        compute='_compute_latest_project',
        store=True
    )
    latest_project_target_completion_date = fields.Date(
        string='Latest Project Target Completion Date',
        compute='_compute_latest_project',
        store=True
    )
    latest_project_progress = fields.Float(
        string='Latest Project Progress',
        compute='_compute_latest_project',
        store=True
    )
    latest_project_state = fields.Selection(
        string='Latest Project State',
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('review', 'Under Review'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        compute='_compute_latest_project',
        store=True
    )
    
    # Status and Timeline
    status = fields.Selection([
        ('prospect', 'Prospect'),
        ('assessment', 'Under Assessment'),
        ('proposal', 'Proposal Stage'),
        ('active', 'Active Client'),
        ('completed', 'Project Completed'),
        ('inactive', 'Inactive'),
    ], string='Status', default='prospect', tracking=True)
    
    onboarding_date = fields.Date(
        string='Onboarding Date',
        help="Date when the client was onboarded"
    )
    
    # Contact Information
    primary_contact = fields.Many2one(
        'res.partner',
        string='Primary Contact',
        help="Main point of contact for this client"
    )
    
    decision_makers = fields.Many2many(
        'res.partner',
        string='Decision Makers',
        help="Key decision makers in the organization"
    )
    
    # Notes and Documentation
    notes = fields.Text(string='Internal Notes')
    
    # ---------------------------
    # COMPUTED FIELDS
    # ---------------------------
    @api.depends('assessment_ids', 'assessment_ids.total_score')
    def _compute_digital_maturity_score(self):
        """Compute the latest digital maturity score from assessments"""
        for record in self:
            latest_assessment = record.assessment_ids.sorted('assessment_date', reverse=True)[:1]
            if latest_assessment:
                record.digital_maturity_score = latest_assessment.total_score
            else:
                record.digital_maturity_score = 0.0
    
    @api.depends('digital_maturity_score')
    def _compute_maturity_level(self):
        """Determine maturity level based on score"""
        for record in self:
            score = record.digital_maturity_score
            if score >= 80:
                record.maturity_level = 'expert'
            elif score >= 65:
                record.maturity_level = 'advanced'
            elif score >= 45:
                record.maturity_level = 'proficient'
            elif score >= 25:
                record.maturity_level = 'developing'
            else:
                record.maturity_level = 'beginner'
    
    @api.depends('assessment_ids')
    def _compute_assessment_count(self):
        """Count total assessments for this client"""
        for record in self:
            record.assessment_count = len(record.assessment_ids)

    @api.depends('assessment_ids')
    def _compute_latest_assessment(self):
        """Fetch latest assessment details regardless of state"""
        for record in self:
            latest_assessment = record.assessment_ids.sorted('assessment_date', reverse=True)[:1]
            if latest_assessment:
                record.latest_assessment_date = latest_assessment.assessment_date
                record.latest_assessment_state = latest_assessment.state
                record.latest_assessment_score = latest_assessment.total_score
            else:
                record.latest_assessment_date = False
                record.latest_assessment_state = False
                record.latest_assessment_score = 0.0
    
    @api.depends('project_ids')
    def _compute_project_count(self):
        """Count total projects for this client"""
        for record in self:
            record.project_count = len(record.project_ids)

    @api.depends('project_ids')
    def _compute_latest_project(self):
        """Fetch latest project details regardless of state"""
        for record in self:
            latest_project = record.project_ids.sorted('start_date', reverse=True)[:1]
            if latest_project:
                record.latest_project_start_date = latest_project.start_date
                record.latest_project_target_completion_date = latest_project.target_completion_date
                record.latest_project_progress = latest_project.progress
                record.latest_project_state = latest_project.state
            else:
                record.latest_project_start_date = False
                record.latest_project_target_completion_date = False
                record.latest_project_progress = 0.0
                record.latest_project_state = False
    
    # ---------------------------
    # CONSTRAINTS
    # ---------------------------
    @api.constrains('digital_maturity_score')
    def _check_maturity_score(self):
        """Ensure maturity score is within valid range"""
        for record in self:
            if record.digital_maturity_score < 0 or record.digital_maturity_score > 100:
                raise ValidationError("Digital maturity score must be between 0 and 100")
    
    @api.constrains('annual_revenue')
    def _check_annual_revenue(self):
        """Ensure annual revenue is positive"""
        for record in self:
            if record.annual_revenue < 0:
                raise ValidationError("Annual revenue cannot be negative")
    
    # ---------------------------
    # ACTIONS
    # ---------------------------
    def action_start_assessment(self):
        return {
            'name': 'New Assessment',
            'type': 'ir.actions.act_window',
            'res_model': 'dt.assessment',
            'view_mode': 'form',
            'context': {
                'default_client_id': self.id,
                'default_name': f"Assessment - {self.name}",
            },
            'target': 'current',
        }
    
    def action_create_project(self):
        return {
            'name': 'New Project',
            'type': 'ir.actions.act_window',
            'res_model': 'dt.project',
            'view_mode': 'form',
            'context': {
                'default_client_id': self.id,
                'default_name': f"Digital Transformation - {self.name}",
            },
            'target': 'current',
        }
    
    def action_view_assessments(self):
        return {
            'name': 'Client Assessments',
            'type': 'ir.actions.act_window',
            'res_model': 'dt.assessment',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }
    
    def action_view_projects(self):
        return {
            'name': 'Client Projects',
            'type': 'ir.actions.act_window',
            'res_model': 'dt.project',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }
