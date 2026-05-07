# 汇率数据服务

每天 09:30 北京时间自动从中国外汇交易中心拉取美元/人民币中间价。

## 数据接口

`https://<你的用户名>.github.io/<仓库名>/rate.json`

返回格式：
```json
{
  "date": "2026-05-07",
  "rate": 6.8487,
  "source": "chinamoney.com.cn",
  "updated_at": "2026-05-07T01:30:00Z"
}
```

## 手动触发更新

进入 GitHub 仓库 → Actions 页 → "每日更新汇率" → "Run workflow"
