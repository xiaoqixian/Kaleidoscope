#### 关于Ubuntu下安装tesserocr库失败的问题

近期在Ubuntu下安装tesserocr库进行验证码识别的时候出现了```Failed building wheel for tesserocr```的错误，经过一番寻找之后找到了问题。

1. 首先在安装tesserocr之前要安装pkg-config

```shell
sudo apt install pkg-config
```

2. 其次要安装tesseract-ocr

```sudo apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev```

3. 安装tesserocr

```pip3 install tesserocr```

问题解决方法来源:https://github.com/sirfz/tesserocr/issues/169