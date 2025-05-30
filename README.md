# TODO

## 安装

1. 确认是 python 3.10 版本

2. 安装依赖包

  ``` bash
  pip install poetry
  poetry install
  ```

3. 配置环境变量

复制 .env.template 为 .env，并配置变量

4. neo4j docker

  ``` bash
  docker pull neo4j:5.26.5
  docker run -d \
    -p 7474:7474 -p 7687:7687 \
    --name neo4j-hackthon-5.26.5 \
    -v $HOME/neo4j/data:/data \
    --env NEO4J_AUTH=none \
    --env NEO4J_PLUGINS='["apoc", "graph-data-science"]' \
    neo4j:5.26.5
  ```

5. 执行代码

  ``` bash
  python weaver/build_memory.py
  python weaver/weave_memory.py
  ```


ps: docker use
1、 sudo sh -c su 
2、 conda activate test
2、 docker run -d -P m.daocloud.io/docker.io/library/neo4j:5.26.5
export POETRY_PYPI_MIRROR_URL=http://mirrors.aliyun.com/pypi/simple/
pip install xxx -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


reference docs:
chat2graph: https://github.com/TuGraph-family/chat2graph
docker: https://yuque.antfin.com/cloud-ide/bpz1u7/ybts3hdak3ae2tpz?singleDoc
