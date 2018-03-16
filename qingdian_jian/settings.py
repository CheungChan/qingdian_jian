#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

"""
Django settings for qingdian_jian project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7a66qzbk+vowjz0^(@$n=rbvjy8h84yv-56ku4hz6r6$gwb@#d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
profile_file = os.path.join(os.path.expanduser('~'), 'profile')
if os.path.exists(profile_file):
    with open(profile_file) as f:
        if f.read().strip() == 'dev':
            DEBUG = True
print(f'settings DEBUG={DEBUG}')
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jian',
    'kan',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qingdian_jian.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qingdian_jian.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

test_db = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'qdbuluo',
        'HOST': '10.10.6.2',
        'USER': 'develop',
        'PASSWORD': '123-qwe',
        'OPTIONS': {'charset': 'utf8mb4'},
    }

}
prod_db = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'qdbuluo',
        'HOST': '10.10.10.2',
        'PORT': 2000,
        'USER': 'qd',
        'PASSWORD': '123^%$-qwe-asd',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

prod_readonly_db = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'qdbuluo',
        'HOST': '10.10.6.6',
        'PORT': 3306,
        'USER': 'develop',
        'PASSWORD': '123^%$-qwe',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
if DEBUG:
    DATABASES = prod_readonly_db
else:
    DATABASES = prod_db

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# 用户设置

LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'handlers': {
        'console_handler': {
            # logging handler that outputs log messages to terminal
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',  # message level to be written to console
            'formatter': 'standard',
        },
        'default_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/qingdian_jian.log',  # 日志输出文件
            'maxBytes': 1024 * 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份份数
            "encoding": "utf-8",
            'formatter': 'standard',  # 使用哪种formatters日志格式
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] p:%(process)s [%(name)s:%(lineno)d] %(message)s'},
    },
    'loggers': {
        'jian': {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            'handlers': ['console_handler', "default_handler"],
            'level': 'DEBUG',
            # 'propagate': True,  # this tells logger to send logging message
            # to its parent (will send if set to True)
        },
        'qingdian_jian': {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            'handlers': ['console_handler', "default_handler"],
            'level': 'DEBUG',
            # 'propagate': True,  # this tells logger to send logging message
            # to its parent (will send if set to True)
        },
        # 'django': {
        #     'handlers': ['console_handler', "default_handler"],
        #     'level': 'DEBUG',
        # },
    },
}
STATIC_URL = '/static/'
if DEBUG:
    REDIS_HOST = '10.10.6.5'
    REDIS_PORT = 6012
    MONGO_HOST = '10.10.6.3'
    RABBITMQ_HOSTS = '10.10.6.5'
    RABBITMQ_POST = 5672
    RABBITMQ_USER = 'yanghao'
    RABBITMQ_PASSWORD = '123456'
else:
    REDIS_HOST = '10.10.10.3'
    REDIS_PORT = 6000
    # MONGO_HOST = '10.10.10.2'
    MONGO_HOST = '10.10.10.4'
    RABBITMQ_HOSTS = '10.10.10.3'
    RABBITMQ_POST = 5000
    RABBITMQ_USER = 'hgz'
    RABBITMQ_PASSWORD = 'hgz123^%$'
REDIS_DB = 15
# MONGO_PORT = 27017
MONGO_PORT = 3000
MONGO_DATABASE = 'qingdian'
weight = {
    'CFContentBasedEngine': 0.3,
    'CFUserBasedEngine': 0,
    'ContentBasedEngine': 0.3,
    'TagBasedEngine': 0,
    'HotBasedEngine': 0.3,
    'RecentBasedEngine': 0.1,
}
LOG_BEGIN = '+' * 10
LOG_END = '-' * 10
# 协同过滤最大评分值
GRADE_MAX = 3