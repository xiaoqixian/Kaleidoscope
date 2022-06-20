### **服务器快速搭建shadowsocks全纪录**

SSH连接软件:Xshell

Tip:当Xshell提示"WARNING! The remote SSH server rejected X11 forwarding request."时，可运行下面的命令重新连接即可。

```
yum install xorg-x11-xauth -y
```

#### 1.开始搭建shadowsocks

1. 如果服务器没有安装wget,则

```python
yum install wget
```

2. 执行安装shadowsocks

```
wget -no-check-certificate -0 shadowsocks.sh https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks.sh
```

*tip:这是一句命令，不要拆开了*

3. 获取shadowsocks.sh的读取权限

```
chmod +x shadowsocks.sh
```

4. 设置ss密码和端口号

```
./shadowsocks.sh 2>&1 | tee shadowsocks.log
```

搞定这些之后，应该就可以看到VPN的一些信息了，将其保存起来。

#### 2.shadowsocks客户端

1. Windows端：[Windows][https://pan.baidu.com/s/19m0AfTkPDSRj0bfYrGpbIg]

2. Android端:[Android][https://pan.baidu.com/s/1coAkZn-GuYHu5eIKaHECxA]

3. ios端:需要另外搭建一个[IPsec/L2TP VPN][https://wistbean.github.io/ipsec,l2tp_vpn.html#%E4%BD%BF%E7%94%A8-IPsec-L2TP-%E8%84%9A%E6%9C%AC%E6%90%AD%E5%BB%BA],以后买了iPhone再说。
4. Mac端:Mac可以直接通过终端远程连接，不再赘述。

#### 3.vultr使用BBR加速上网

1. 安装BBR

```
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh
```

2. 获取读写权限

```
chmod +x bbr.sh
```

3. 启动BBR安装

```
./bbr.sh
```

4. 接着按任意键，开始安装，坐等一会。安装完成一会之后它会提示我们是否重新启动vps，我们输入 y 确定重启服务器。

   重新启动之后，输入 `lsmod | grep bbr` 如果看到 tcp_bbr 就说明 BBR 已经启动了。

