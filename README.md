## 1.使用说明
venv包已上传，在终端激活环境后，直接运行main.py即可。
![alt text](image.png)

### 打包命令
```python
pyinstaller main.py -i="E:\Python\ProgramFile\wuziqi\tubiao.ico" -F -w -n wuziqi_v2
```
生成的exe文件在dist文件夹中。
exe文件可以脱离python环境运行。

### 打包方法讲解
[使用pyinstaller打包conda环境下多文件的python程序](https://www.yuque.com/u39067637/maezfz/qqm6xavvkp00blyb#L2q2w)

## 2.游戏玩法：
五子棋游戏，鼠标控制，黑棋先行。
