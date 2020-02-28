#### Android Service

1. 分类

   * Local Service:

     Service对象与Service的启动者在同个进程中运行

   * Remote Service:

     对象与启动者不在同一个进程，存在进程间通信问题，Android设计了AIDL来实现。