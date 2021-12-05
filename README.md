# SUES-autotemp

上海工程技术大学体温自动填报脚本

# 使用教程

python 版本`3.7.0`

- **安装**
  `pip install -r requirements.txt`

- **配置脚本**
  修改以下代码内容,多用户请将账号密码一一对应

```
classnums = ['学号1', '学号2', '学号3']  # 填写学号
passages = [('密码1'), ('密码2'), ('密码3')] # 填写密码
sckey = "sckey"  # Server酱推送提醒，需要填写sckey，官网：https://sct.ftqq.com/sendkey
```

- **运行**
  `python autotemp.py`
