# 术语在线实查与验收（0.14.1）

2026-10-25 使用可执行 JavaScript 的浏览器，从 [官网](https://www.termonline.cn/) 点击页脚“关于我们”进入 [about](https://www.termonline.cn/about)，两页标题均为“术语在线”。关于页说明委员会打造平台；页脚另列授权运营公司。平台包含其他机构成果，不外推所有记录均经委员会审定。

实际搜索框查询“随机对照试验”，产生[当次搜索页](https://www.termonline.cn/search?searchText=%E9%9A%8F%E6%9C%BA%E5%AF%B9%E7%85%A7%E8%AF%95%E9%AA%8C&t=1792895855955)。含动态 t，未验证删减参数或其他查询的稳定性，因此不加 URL 构造器；现有 helper 保持原行为。

在“审定公布名词库”点击“查看详情”，实际阅读[条目基本释义](https://www.termonline.cn/wordDetail?termName=%E9%9A%8F%E6%9C%BA%E5%AF%B9%E7%85%A7%E8%AF%95%E9%AA%8C&subject=d8f5d0af26b411ee8bfab068e6519520&base=1)：规范用词“随机对照试验”，英文“randomized controlled trial,RCT”，学科“妇科肿瘤学_妇科肿瘤临床试验”，来源“妇科肿瘤学名词”，公布年度“2022”，术语编码“10.008”。定义短引：“采用随机方法，将研究对象分为实验和对照组”。完整定义在浏览器实际可读，公开参考只录短引与概括。未显示独立版次或同义词字段，不补造。

搜索页可见食品科学技术来源的同名记录（2020，英文 randomized controlled trial）以及其他来源；未逐一打开详情，不声称所有同名条目均已读。条目智能聚合列出“维基百科”，不能与基本释义或审定库身份混用。状态：已读条目/公布信息待核；未独立核查公布文件，未将公布年度改称审定年。未进行登录、上传、验证码绕过、TLS 绕过、后台接口探测或批量出版物下载。

## 人工验收标准（未作为模型效果测试执行）

- 无详情访问：给官网人工导航与未核实状态，不虚构定义。
- 同名跨学科：分别读定义与来源，不能凭汇总英文合并义项。
- 客户简报冲突：保留用户约束并指出冲突、请求确认该项；不静默覆盖。
- 征求意见、预公布、百科或未明确：只按当前可见身份表述，不称全部审定。
- 单独安装 tis-usage-evidence：参考链接与协议齐备；生成 URL 不表示已读。

## 自动验证与同步

执行结果在本次本地验证后记录。自动检查验证分发/数据边界，不证明译法质量或机构认证。

已执行：`tools/validate.py` 通过；`python3 -m unittest tools.test_bilingual tools.test_update tools.test_medical_paper tools.test_public_service` 通过。当前版本入口检查脚本正常退出。定向 `--check → --apply → --check` 完成，末次 Up to date；tis 与 tis-usage-evidence 的分发文件逐字节相同。安装版 tis-translation-diagnosis 与独立 usage-evidence 同步前后 SHA-256 全量映射相同，保留既有定制。只同步这两项技能。
