# 创建ca证书

## 初始化工作目录和配置
1. 初始化工作目录
> mkdir -p ./ca/{certs,newcerts,crl,private}
> cd ./ca
> touch index.txt
> echo "01" > {serial,crlnumber}
2. 创建配置文件
> cp /etc/pki/tls/openssl.cnf ./
> (macos: /usr/local/etc/openssl@$version/openssl.cnf)
3. 配置openssl.cnf
> 1) 配置ca目录: CA_default.dir = ./
> 2) 配置域名: alt_names.DNS.*

## 创建ca根证书及秘钥
> openssl req -new -x509 -newkey rsa:4096 -keyout ca.key -out ca.crt -config openssl.cnf -days 3650 -subj '/C=CN/ST=GuangDong/L=ShenZhen/O=Demo/OU=IT/CN=demo.com/emailAddress=ca@demo.com' -passin pass:123456 -passout pass:123456

## 签发服务器证书
1. 生成客户端私钥
> openssl genrsa -out server.key 4096
2. 新建证书请求
> openssl req -new -key server.key -out server.csr -config openssl.cnf -subj '/C=CN/ST=GuangDong/L=ShenZhen/O=Demo/OU=IT/CN=demo.com/emailAddress=server@demo.com'
3. 使用ca证书签发服务器证书
> openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key -config openssl.cnf -passin pass:123456 -days 1095
4. 证书有效性验证
> openssl verify -CAfile ca.crt server.crt

## 证书转换
1. 合并pem证书
> cat server.crt server.key > server.pem
2. 转p12证书
> openssl pkcs12 -export -in server.crt -inkey server.key -out server.p12 -passin pass:123456 -passout pass:123456

## 吊销证书
1. 校验证书的serial和subject
> openssl x509 -in server.crt -noout -serial -subject
2. 吊销
> openssl ca -revoke newcerts/$serial.pem -cert ca.crt -keyfile ca.key -config openssl.cnf -passin pass:123456
3. 更新吊销证书列表
> echo 01 > ./crlnumber(第一次吊销证书执行)
> openssl ca -gencrl -out crl/crl.pem -config openssl.cnf -passin pass:123456
4. 查看吊销列表
> openssl crl -in crl/crl.pem -noout -text