# 月宫の教务代理

[![vue](https://img.shields.io/badge/vue-3.0-brightgreen.svg)](https://github.com/vuejs/vue)
[![hammerjs](https://img.shields.io/badge/hammerjs-2.0.8-blue)](https://github.com/hammerjs/hammer.js)

本项目允许你使用手机登录并访问教务系统的部分功能。

针对新教务系统没法在手机上登录的缺点，本项目提供了一个简单的手机端界面，允许你在手机上查看部分教务系统的功能，同时提供新增的服务，包括：
- 查看教务系统理论课程表
- 查看所有课程及其考试安排和成绩
- 登录过一次之后，从浏览器缓存再次查看之前的数据
- 多用户管理
- 第二课堂分数管理及各种加分比赛/考试
等。

本项目所有数据均从前端通过代理直接向教务系统请求。对于来自教务系统的信息后端不设任何持久化手段。不会保存任何学生数据。仅临时保留IP用于限制访问频率。本项目仅用于学习和研究，不涉及任何商业用途。

据相关隐私，本开源项目中不包含资源、部署和网站脚内容相关文件。有需要管我要。

课程表界面长按整周课程可以暂时隐藏，显示普通课程表。

代理见[proxy_server.py](proxy_server.py)

> yku.tsukimiya.site - Beautification Project for Educational Administration System
> Copyright (C) 2025  BPuffer
