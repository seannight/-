# 统一技术框架配置
TECH_STACK = {
    'pdf_parser': ['pdfplumber', 'PyPDF2'],  # 兼容两种解析器
    'text_processing': 'jieba',  # 统一使用jieba
    'api_framework': 'FastAPI',  # 统一使用FastAPI
    'env_mode': {
        'A': 'docker',  # A成员使用Docker
        'BC': 'local'   # BC成员使用本地环境
    }
}

# 系统版本信息
VERSION = {
    'api': '2.1.0',
    'ui': '2.0.1',
    'release_date': '2023-04-09',
    'build': '230409'
}

# 组件加载配置
COMPONENT_LOADING = {
    'order': [
        'ui_components',      # 1. 优先加载UI组件
        'data_processor',     # 2. 加载数据处理组件 (B成员)
        'qa_engine',          # 3. 加载问答引擎 (C成员)
        'knowledge_base'      # 4. 加载知识库
    ],
    'timeout': {
        'ui_components': 2,     # UI组件加载超时秒数
        'data_processor': 30,   # 数据处理组件加载超时秒数
        'qa_engine': 45,        # 问答引擎加载超时秒数
        'knowledge_base': 20    # 知识库加载超时秒数
    }
}

# API相关配置
API_CONFIG = {
    'default_port': 8000,
    'cors_allowed_origins': ['*'],  # 允许所有来源，生产环境应限制
    'rate_limit': {
        'enabled': True,
        'requests_per_minute': 60
    },
    'docs_url': '/api/docs',
    'redoc_url': '/api/redoc'
}

# 问答引擎配置
QA_ENGINE_CONFIG = {
    'knowledge_dir': 'data/processed/excel_tables',
    'use_api': False,  # 默认不使用外部API
    'api_config': None,
    'llm_model': None
}

# 表格处理配置
TABLE_PROCESSOR_CONFIG = {
    'input_dir': 'data/raw',
    'output_dir': 'data/processed/excel_tables',
    'max_workers': 4
}

# 启动模式配置
STARTUP_MODES = {
    'fast': {
        'description': '快速启动模式 - 优先加载UI，后台加载组件',
        'env_var': 'FASTSTART',
        'value': '1'
    },
    'ui_priority': {
        'description': 'UI优先模式 - 确保界面快速响应',
        'env_var': 'UI_PRIORITY',
        'value': '1'
    },
    'emergency': {
        'description': '紧急模式 - 仅加载最基本组件',
        'env_var': 'EMERGENCY',
        'value': '1'
    }
}

# 演示界面配置
DEMO_CONFIG = {
    'dashboard_path': 'demo/dashboard',
    'default_questions': [
        '泰迪杯竞赛介绍',
        '报名流程和条件',
        '今年的赛题有哪些',
        '如何提高获奖几率',
        '历届优秀作品'
    ]
} 