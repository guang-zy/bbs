# bbs

- ### 主要功能
    - 用户登录注册、个人信息修改如头像、签名
    - 个人主页：显示发布的话题以及参与的话题 
    - 用户之间站内信、邮件通知 
    - 话题的板块、发布、评论 
 
 ### 技术栈     
 Nginx + Gunicorn + gevent+ Flask + MySQL +  SQLalchemy + jinja2 + Redis + Celery 

 - 使用 Nginx 处理静态请求并反向代理
 - 使用 Redis 存放用户 Session 和页面 Token 实现多进程数据共享 
 - Gunicorn 开启多个worker，实现多进程负 载均衡, gevent 实现协程提升并发处理效率  
 - Celery 实现消息队列处理邮件发送,  保证发送成功 
 - 实现对 XSRF 攻击的防御 

 ### 论坛演示
  ![图片](/images/bbs.gif)