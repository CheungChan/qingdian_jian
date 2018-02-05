## 轻点公司辣条项目推荐系统
#### 安装运行
1. 系统安装python>3.6,使用pip安装virtualenv virtualenvwrapper
```bash
sudo pip install virtualenv
sudo pip install virtualenvwrapper
```
配置环境变量,在home下建立文件夹envs,里面放置的都是虚拟环境
```shell
PATH=$PATH:/usr/local/python3/bin
VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.5
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=/root/envs
#export QT_QPA_PLATFORM=offscreen
export LESSCHARSET=utf-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

2. 克隆项目地址
```bash
git clone git@gitee.com:CheungChanDevCoder/qingdian_jian.git
```
当然前提是你有权限.

3. 利用crontab提前对内容相似度做离线计算
```bash
crontab crontab.conf
```

4. 启动项目
```bash
cd qingdian_jian
sh restart.sh
```
如果在生产上更改了代码,要测试,可以使用```sh restart.sh -t```或```sh restart.sh --test```来启动预生产环境.
其他都一样,只是启动端口不一样,可通过配置域名访问之.
#### 项目介绍
 本项目基于django.目前有两个app.jian负责推荐和埋点相关工作,kan负责报表相关工作.
#### 代码重点部分介绍
- 本项目使用了mysql,mongo作为存储引擎.除了脚本(calculate_all_content_similarity.py)外,
所有mysql的表操作位于models.py中,所有mongo操作,仿照mysql的方式,都放到了mongo_models.py中,
便于集中管理.
- 整个推荐流程使用了面向对象的编程范式.抽象成了jian.process.py中的Process中.每次推荐的时候实例化Process对象,而这个
对象是一个callable对象,直接括号就可以得到推荐的data数据和analyze分析数据.data主要用于前端展示,analyze可以详细分析
推荐过程.
- 整个推荐过程分为准备用户特征向量,综合推荐,过滤,排序,存储.
- 准备用户特征向量是为了准备在整个推荐过程中关于用户这个维度到处都会用到的值并将这些值绑定到了process对象当中,
在推荐的时候将process对象出入这些引擎的初始化参数,这样引擎中可以随时通过引擎绑定的process对象间接拿到这些特征向量.
- 推荐部分,综合多种推荐引擎,按照配置中的比例和要推荐的数目推荐内容id,如果由于种种原因未能推荐完全,会由后面的引擎
补上缺少的部分,所以越精确的引擎尽量放前面,越不太会推不出来的引擎放在后面.
- 引擎中着重介绍基于内容相似的推荐引擎,脚本calculate_all_content_similarity.py会离线计算内容的两两之间的相似度,引擎
根据离线计算的数据,计算用户喜欢的内容中各个内容的相似度,把这些相似度做加权平均,排序,得到用户喜欢的内容最相似的内容.这里
利用mongo又做了一层用户和喜欢内容id做加权平均的缓存,可以加快推荐速度.
- 基于标签的引擎,利用用户喜欢的内容对应的标签出现的频率做加权平均,根据要推荐的个数,求解要推荐的内容中标签应该占有的比例,
再去根据标签查询出内容做推荐
- 热门推荐,利用近期所有用户点击量做多的内容做推荐
- 基于最近更新的推荐,运营人员刚刚添加的内容或者爬虫自动添加的最新的内容作出推荐,在其他推荐推出的内容不够的时候特别有用,对
实时性要求高的内容也特别有用.
