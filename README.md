# devops (持续更新中)

demo（只是个空架子  大部分功能没开放出来，等权限完成后再打开）

地址 http://121.199.79.74

用户名 admin
   
密码 ASDasd!@#123

#### 项目介绍
devops 自动化运维平台--一站式满足需求

功能点（按顺序实现）：
* CMDB 
* webssh &radic;
* 用户管理 &radic;
* 日志审计 &radic;
* 远程命令/脚本 
* 文件分发 &radic;
* 环境部署 
* 代码发布管理
* 数据库管理 
* DNS管理 &radic;
* 权限细分 
* 接口管理 
* 定时任务管理
* 监控管理
* 容器管理
* WEB 日志 &radic;
* 开放REST API


#### 工具依赖
* Django2
* Python3
### 安装部署（未完待续，不要上生产）
* 搭建salt-api，jenkins，git环境
* 搭建redis，mysql环境
* 修改配置文件（devops/settings.py && conf/example）
* 启动django项目
* 启动web ssh
#### 参与贡献

项目前后端借鉴了很多开源项目，做了个集成，有需求或者建议，请提交issue
