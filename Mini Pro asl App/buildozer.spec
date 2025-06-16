[app]
source.dir = Mini Pro asl App
requirements = python3.10,kivy,requests,flask,pyjnius,opencv-python
    android.permissions = INTERNET,RECORD_AUDIO
title = ASL Translator
package.name = asl_translator
package.domain = org.asl
version = 1.0
source.include_exts = py,png,jpg,kv,ttf,mp4
source.include_patterns = assets/*
icon.filename = icons/app_icon.png

[buildozer]
log_level = 2
warn_on_root = 1
