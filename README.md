# Forum Radar — review prototype

A private, single-user, local-first forum reading prototype. It follows only explicitly selected threads, public authors, boards or tags, and supports pausing, stopping and expiration. It does not automatically expand its monitoring scope.

Reddit integration uses read-only OAuth endpoints and stays inactive until access approval and credentials are supplied. No Reddit data has been collected by this project. The intended initial application scope is r/flying, r/aviationmaintenance and r/avionics, subject to approval. External AI processing is disabled by default; no data is used for model training.

This is not a production deployment: complete pagination, OAuth refresh, deletion synchronization and live Mac/iMessage verification remain outstanding. Required safeguards must be completed before live collection. The Python standard-library implementation has no paid dependencies; optional third-party AI is independently billed.

Repository contents exclude registration records, application correspondence, credentials, runtime databases and real forum content. Test events are fictional. See the implementation in `radar.py` and the setup and limitations below.

---

# 论坛雷达 · 本地验证版 v0.1

为 Mac Studio 准备的轻量个人工具。Python 标准库实现，不需要 pip/npm、云主机或订阅。

**这是可以运行的首版验证包，不是已经接通三个论坛的生产应用。Reddit API 批准及本机部署需由使用者自行完成。**

## 启动

1. 把解压后的整个 `forum-radar` 文件夹放到 `~/Applications/ForumRadar`。
2. Mac 需已有 Python 3.10 或更高版本。终端执行 `python3 --version`。没有时请从 https://www.python.org/downloads/macos/ 安装；程序不会自动安装第三方软件。
3. 在终端进入该文件夹，运行：

```bash
python3 radar.py
```

4. 用浏览器打开 **http://127.0.0.1:8765**。先启动程序，再打开网页。也可双击 `Start.command`，若浏览器先于服务启动，刷新一次即可。

程序只在本机开放，不提供公网访问。默认没有关注项、没有论坛请求、AI 关闭、通知只做预览。

## 按你的选择建立关注

“添加关注”填写一个具体目标：用户 / 帖子 / 版块 / 标签，可继续限定版块、作者、关键词和排除词。各组条件之间为“且”，同组多个词为“或”。用户名和标签精确匹配、不区分大小写。没有从关注项自动扩展的功能。

新关注默认暂停。启用后的第一次数据只建立基线，不通知；后续新增或修改才进入摘要。暂停和停止都会清除该关注的待通知项，并使含该关注的未发送预览失效。恢复时重新建立基线，不追赶暂停期间的更新。停止不能直接恢复，需重新新建。到期日期当天结束后停止。

当前不支持修改既有关注；可停止原关注后创建新的。定时摘要默认 09:00、19:00，时区初始为 Asia/Seoul，可修改。定时窗口允许延后 60 分钟；更长停机恢复后等待下一窗口汇总。UTC 用于每日用量限额，不影响通知的本地时区。

## 先用离线样本验证

`tests` 使用的都是虚构数据。创建：

- 来源：PoA；类型：用户；目标：Alice；限定版块：maintenance-bay.8；接入：手动导入。
- 若需要看片段，可以勾选本地正文处理（样本不是真实论坛内容）。
- 启用关注，先导入 `docs/sample-baseline.json` 建立基线。
- 再导入 `docs/sample-update.json`，点击“生成本次汇总”。
- 暂停该关注，先前未发送预览会变为 cancelled。

导入必须是 JSON 数组，每条有 `id, thread, author, board, title, url`，可带 `body, tags, parent, posted`。导入范围需与所选关注一致。导入不代表软件已经连通该网站。

## 三个论坛

**Reddit**：请注册自己的账号并按官方要求申请 API 访问批准。获批后才能勾选批准项。适配器读取环境变量 `RADAR_REDDIT_TOKEN`，必须是官方 OAuth access token，不是账号密码。当前不自动刷新，过期会停止并报告。不提供转成网页抓取的后备路径。

帖子选择填帖子 URL 或 ID；用户填用户名；版块填 subreddit；标签填 flair，并填写版块。用户在特定版块的内容通过 user overview 后本地过滤；未匹配的其他版块内容不会入库。版块/标签模式当前仅看新帖，不自动收集所有新回复。指定帖子可解析返回的回复树，但未展开 more。始终标记部分覆盖。

**PoA**：具体帖子可使用实验性单页适配器，填写完整帖子 URL。需先确认允许该访问方式；不登录、不处理验证码、不绕过限制。作者/版块/标签的自动发现目前需使用已经验证的站内 RSS，或手动导入。单页模式不保证获得所有新增回复。

**BeechTalk**：默认关闭自动正文获取。其条款限制会员内容在社区外复制，需先确认本工具用途的允许范围。注册使用真实姓名且每人一个账号。未确认正文处理时可导入链接级事件，但不会保存正文或原帖标题。不要仅因为拥有账号就勾选内容处理已获准。

正文处理和 AI 外部处理权限是分开的配置项。正式采集前还应补齐来源要求的删除同步和分页处理。

## iMessage

在你的 Mac“快捷指令”中手动创建 **ForumRadarSend**：

1. 接收快捷指令输入，必要时先从输入文件获取文本。
2. 添加“发送信息”，消息设为上述文本。
3. 收件人固定为你希望接收通知的 iMessage 地址，不由论坛内容决定。
4. 在该 Mac 上运行一次，处理系统授权，并按你的系统版本允许无交互运行。

先在终端验证快捷指令接受文本文件，再在软件“摘要与通知”中手动发一条摘要，并确认 iPhone 真正收到且弹出通知。发给同一 Apple 账户是否出现提醒需要实测；此工具不会宣称命令返回成功就代表手机送达。

确认锁屏、后台、重启恢复都正常后，再把“通知方式”改成 iMessage。没有配置前保持预览。

若状态是 unknown，请先核对 Mac Messages，程序不会自动重发，避免重复。当前没有 unknown 状态的强制重发按钮；确认未发送后可重新生成选定事件的新摘要。

## 可选 AI：第三方或你自己安装的本地模型

默认完全不调用。规则汇总只拼合新增数量、作者、片段和链接，不宣称理解观点或判断共识。

支持 OpenAI 兼容的 `/chat/completions`：在设置中填 Base URL 和模型 ID，例如你自己的服务商 API；本地兼容服务可填 `http://127.0.0.1:11434/v1`。安装本地模型服务是独立可选步骤，此包不自动下载模型。

第三方 API 密钥通过环境变量配置，不放进聊天、不写到关注配置或网页：

```bash
read -s -p "AI API Key: " RADAR_AI_KEY
echo
export RADAR_AI_KEY
python3 radar.py
```

程序同时要求：全局 AI 开启、该关注允许正文处理、该关注允许 AI 处理。达到每日调用上限或 API 错误时退回免费片段汇总。Base URL 必须是可信服务商，密钥只发给配置的 API，不自动跟随重定向。不同厂商的专有协议暂不支持。

限制调用次数不等于金额上限。想保持零费用，请保持 AI 关闭，或自行部署无付费接口的本地模型。第三方模式请同时在服务商账户设置账单限额。

## 登录后后台常驻（可选）

先关闭终端里的前台实例，再执行：

```bash
python3 mac/install_launchagent.py
```

后台依赖你的 Mac 用户已登录（锁屏可实测；注销后不运行）。创建在你自己的 LaunchAgents 下，不修改系统服务。你的 Mac 需保持联网并避免系统自动睡眠；此包不会替你改电源设置。

LaunchAgent 不继承终端里 export 的密钥。需要后台 AI/API 时，可在你本机编辑生成的 `~/Library/LaunchAgents/com.lanyx.forum-radar.plist`，加入 `EnvironmentVariables`，然后重新加载。该文件权限设为 600，但仍是本机明文配置；如不接受该存储方式，保持 AI 关闭或在前台终端运行。包中不含任何真实密钥。

停止后台：

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.lanyx.forum-radar.plist"
```

卸载后台：停止后移走上面的 plist。保留整个应用文件夹及 `data` 即可保留数据；应用文件夹删除前可自行备份。后台日志在 `~/Library/Logs/ForumRadar`。

## 测试及交付限制

```bash
python3 -m unittest discover -s tests -v
```

已做离线逻辑测试；不代表真实账号、API、完整论坛正文、Mac 通知已验收。没有付费依赖，也没有产生任何真实论坛消息或回帖。
