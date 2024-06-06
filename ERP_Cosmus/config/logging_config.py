import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s - %(name)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'product_view_logs.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        # 'django': {
        #     'handlers': ['file'], #'console',
        #     'level': 'INFO',
        #     'propagate': False,
        # },
        'product_views': {  # Replace 'myapp' with your app name
            'handlers': ['file'],  #'console',
            'level': 'DEBUG',
            'propagate': False,
        },
        
    }
}