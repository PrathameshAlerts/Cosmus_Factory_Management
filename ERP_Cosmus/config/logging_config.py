
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %I:%M:%S %p',
        },
        'simple': {
            'format': '%(levelname)s - %(name)s - %(message)s',
            'datefmt': '%Y-%m-%d %I:%M:%S %p',
        },
    },

    'handlers': {
        'django_file': {                       # can keep diffrent file handlers for diffrent loggers
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_logs.log',
            'formatter': 'verbose',
        },

        'product_file': {                      # can keep diffrent file handlers for diffrent loggers
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'product_logs.log',
            'formatter': 'verbose',
        },

        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['django_file','console'],
            'level': 'INFO',
            'propagate': False,
        },

        'product_views': {                       # Replace 'product_views' with app name 
            'handlers': ['product_file'],        #'console',
            'level': 'DEBUG',
            'propagate': False,
        },

        'product_signals': {  
            'handlers': ['product_file'],         #'console',
            'level': 'DEBUG',
            'propagate': False,
        },

        'product_forms': {  
            'handlers': ['product_file'],         #'console',
            'level': 'DEBUG',
            'propagate': False,
        },
        
    }
}