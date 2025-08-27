from odoo import models, fields, api


class Consultant(models.Model):
    """Consultant/Employee Model for Digital Transformation"""
    _name = 'dt.consultant'
    _description = 'Digital Transformation Consultant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Full Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='HR Employee Record', ondelete='set null')
    user_id = fields.Many2one('res.users', string='System User', ondelete='set null')
    
    # Professional Details
    title = fields.Char(string='Job Title')
    department = fields.Selection([
        ('consulting', 'Consulting'),
        ('technical', 'Technical'),
        ('project_management', 'Project Management'),
        ('business_analysis', 'Business Analysis'),
        ('change_management', 'Change Management'),
    ], string='Department')
    
    seniority_level = fields.Selection([
        ('junior', 'Junior Consultant'),
        ('consultant', 'Consultant'),
        ('senior', 'Senior Consultant'),
        ('principal', 'Principal Consultant'),
        ('partner', 'Partner'),
    ], string='Seniority Level', default='consultant')
    
    hourly_rate = fields.Float(string='Hourly Rate')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, ondelete='restrict')
    
    # Skills and Expertise
    skill_ids = fields.Many2many('dt.skill', string='Skills & Certifications')
    specialization_areas = fields.Text(string='Specialization Areas')
    
    # Availability and Capacity
    availability = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('partially_available', 'Partially Available'),
        ('unavailable', 'Unavailable'),
    ], string='Availability', default='available')
    
    capacity_percentage = fields.Float(string='Current Capacity %', default=100.0)
    
    # Performance Metrics
    projects_managed = fields.Integer(string='Projects Managed', compute='_compute_project_stats')
    projects_participated = fields.Integer(string='Projects Participated', compute='_compute_project_stats')
    client_satisfaction_avg = fields.Float(string='Avg Client Satisfaction', compute='_compute_satisfaction')
    
    # Contact Information
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    
    # Status
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends()
    def _compute_project_stats(self):
        for record in self:
            managed_projects = self.env['dt.project'].search_count([
                ('project_manager_id', '=', record.id)
            ])
            participated_projects = self.env['dt.project'].search_count([
                ('team_members', 'in', [record.id])
            ])
            record.projects_managed = managed_projects
            record.projects_participated = participated_projects + managed_projects
    
    @api.depends()
    def _compute_satisfaction(self):
        for record in self:
            projects = self.env['dt.project'].search([
                ('project_manager_id', '=', record.id),
                ('satisfaction_score', '!=', False)
            ])
            if projects:
                scores = [float(p.satisfaction_score) for p in projects]
                record.client_satisfaction_avg = sum(scores) / len(scores)
            else:
                record.client_satisfaction_avg = 0.0


class Skill(models.Model):
    """Skills and Certifications"""
    _name = 'dt.skill'
    _description = 'Skill or Certification'
    
    name = fields.Char(string='Skill/Certification Name', required=True)
    category = fields.Selection([
        ('technical', 'Technical'),
        ('functional', 'Functional'),
        ('industry', 'Industry Knowledge'),
        ('soft_skills', 'Soft Skills'),
        ('certification', 'Certification'),
    ], string='Category', required=True)
    
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)