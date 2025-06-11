# file_transfer
基于socket的简易文件传输

## 任务
1. 弄清api返回headers里设置Content-Disposition作用 ✓
2. 下载文件接口返回headers设置正确的Content-Disposition，实现客户端下载文件不打开新窗口，且下载的文件名正确不为随即字符串 ✓
3. 把上传文件接口改写成可以接收同一来源同一请求的多次传输，将同一文件的多次传输数据组合为一个文件