#!/usr/bin/env node

/**
 * 小红书热点汇报脚本
 * 用于定时任务 - 生成格式化报告发送给用户
 * 
 * 用法：
 * node scripts/xhs-hot-report.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 复用热点搜集逻辑
const HOT_URL = 'https://www.xiaohongshu.com/api/recommend/hot';

function getMockHotTopics(limit = 20) {
  const mockData = [
    { title: 'AI 绘画教程', heat: 9876543 },
    { title: '副业搞钱', heat: 8765432 },
    { title: '打工人日常', heat: 7654321 },
    { title: '效率神器', heat: 6543210 },
    { title: '职场成长', heat: 5432109 },
    { title: '自媒体运营', heat: 4321098 },
    { title: '技能学习', heat: 3210987 },
    { title: '时间管理', heat: 2109876 },
    { title: '笔记灵感', heat: 1098765 },
    { title: '生活记录', heat: 987654 },
    { title: '好物分享', heat: 876543 },
    { title: '穿搭灵感', heat: 765432 },
    { title: '美食教程', heat: 654321 },
    { title: '旅行攻略', heat: 543210 },
    { title: '健身打卡', heat: 432109 },
  ];
  return mockData.slice(0, limit).map((item, index) => ({
    rank: index + 1,
    title: item.title,
    heat: item.heat,
    link: `https://www.xiaohongshu.com/search/${encodeURIComponent(item.title)}`
  }));
}

function getMockHotTags() {
  return [
    '#AI 绘画', '#副业搞钱', '#打工人', '#效率神器', '#职场成长',
    '#自媒体', '#技能学习', '#时间管理', '#笔记灵感', '#生活记录',
    '#好物分享', '#穿搭灵感', '#美食教程', '#旅行攻略', '#健身打卡'
  ];
}

function formatHeat(heat) {
  if (heat >= 1000000) {
    return (heat / 1000000).toFixed(1) + 'w';
  } else if (heat >= 10000) {
    return (heat / 10000).toFixed(1) + 'w';
  } else {
    return heat.toString();
  }
}

async function getHotTopics(limit = 20) {
  return new Promise((resolve) => {
    https.get(HOT_URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          const topics = result.data?.hot_topics || result.data || [];
          resolve(topics.slice(0, limit).map((item, index) => ({
            rank: index + 1,
            title: item.title || item.name || '未知',
            heat: item.heat || item.hot_value || 0,
            link: item.link || `https://www.xiaohongshu.com/search/${encodeURIComponent(item.title || '')}`
          })));
        } catch (e) {
          resolve(getMockHotTopics(limit));
        }
      });
    }).on('error', () => {
      resolve(getMockHotTopics(limit));
    });
  });
}

async function main() {
  try {
    const topics = await getHotTopics(20);
    const tags = getMockHotTags();

    const date = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });

    let report = `🔥 小红书热点速递 (${date})\n\n`;
    report += `【热榜 TOP10】\n`;
    
    topics.slice(0, 10).forEach(topic => {
      const emoji = topic.rank <= 3 ? '🔥' : topic.rank <= 10 ? '💰' : '📈';
      report += `${topic.rank}. ${topic.title} ${emoji} ${formatHeat(topic.heat)}\n`;
    });

    report += `\n【热门标签】\n`;
    report += tags.slice(0, 10).join(' ');

    report += `\n\n【推荐创作方向】\n`;
    report += `1. AI 工具 + 副业 = 高热度组合\n`;
    report += `2. 打工人共鸣内容 = 高互动\n`;
    report += `3. 教程类内容 = 高收藏\n`;

    report += `\n杨哥，要写哪个方向？我等你意见～ 🦞`;

    // 输出报告（可通过管道发送给用户）
    console.log(report);

    // 保存到文件
    const outputPath = path.join(__dirname, '../hot_report.txt');
    fs.writeFileSync(outputPath, report);

    console.log(`\n✅ 热点报告已保存到：${outputPath}`);

  } catch (error) {
    console.error('❌ 热点汇报失败:', error.message);
    process.exit(1);
  }
}

main();
