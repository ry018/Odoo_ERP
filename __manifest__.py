{
    'name': 'Digital Transformation Accelerator',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Manage digital transformation consulting projects and client assessments',
    'description': """
Digital Transformation Project Accelerator
==========================================
This module helps IT consulting firms manage digital transformation projects by providing:
* Client digital maturity assessments
* Project phase tracking and management
* Resource allocation and planning
* Automated reporting and notifications
* Client portal for project visibility

Perfect for companies specializing in digital intelligence, transformation, 
and ERP implementation services.
    """,
    'author': 'RUPESH R',
    'website': 'https://github.com/yourusername',
    'depends': [
        'base',
        'project',
        'portal',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security.xml',
        
        # Data
        'data/assessment_templates.xml',
        
        # Views
        'views/client_views.xml',
        'views/assessment_views.xml',
        'views/project_views.xml',
        'views/consultant_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'digital_transformation_accelerator/static/src/css/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}