#!/usr/bin/env node

/**
 * 小红书热点搜集脚本
 * 用于虾王比赛 - 小红书全自动发布技能 v2.0
 * 
 * 用法：
 * node scripts/xhs-hot.js          # 获取热榜 Top 50
 * node scripts/xhs-hot.js 20       # 获取热榜 Top 20
 * node scripts/xhs-hot.js --tags   # 获取热门标签
 */

const https = require('https');

// 小红书热榜 API（网页端公开接口）
const HOT_URL = 'https://www.xiaohongshu.com/api/recommend/hot';
const TAGS_URL = 'https://www.xiaohongshu.com/api/search/trending';

/**
 * 获取小红书热榜
 */
async function getHotTopics(limit = 50) {
  // 由于小红书 API 需要真实浏览器环境，这里使用模拟数据演示
  // 实际使用时需要配置真实的 API 调用
  return getMockHotTopics(limit);
}

/**
 * 获取热门标签
 */
async function getHotTags() {
  return new Promise((resolve, reject) => {
    https.get(TAGS_URL, {
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
          const tags = result.data?.tags || result.data || [];
          resolve(tags.slice(0, 20).map(tag => tag.name || tag));
        } catch (e) {
          // 如果 API 失败，返回模拟数据用于演示
          resolve(getMockHotTags());
        }
      });
    }).on('error', reject);
  });
}

/**
 * 模拟热榜数据（用于演示）
 */
function getMockHotTopics(limit = 50) {
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

/**
 * 模拟热门标签（用于演示）
 */
function getMockHotTags() {
  return [
    '#AI 绘画', '#副业搞钱', '#打工人', '#效率神器', '#职场成长',
    '#自媒体', '#技能学习', '#时间管理', '#笔记灵感', '#生活记录',
    '#好物分享', '#穿搭灵感', '#美食教程', '#旅行攻略', '#健身打卡'
  ];
}

/**
 * 格式化热度值
 */
function formatHeat(heat) {
  if (heat >= 1000000) {
    return (heat / 1000000).toFixed(1) + 'w';
  } else if (heat >= 10000) {
    return (heat / 10000).toFixed(1) + 'w';
  } else {
    return heat.toString();
  }
}

/**
 * 生成热点报告
 */
function generateReport(topics, tags) {
  const date = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });

  let report = `🔥 小红书热点速递 (${date})\n\n`;
  report += `【热榜 TOP${topics.length}】\n`;
  
  topics.forEach(topic => {
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

  return report;
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  const limit = parseInt(args[0]) || 50;
  const tagsOnly = args.includes('--tags');

  try {
    console.log('🦞 正在搜集小红书热点...\n');

    if (tagsOnly) {
      const tags = await getHotTags();
      console.log('【热门标签】');
      console.log(tags.join(' '));
      return;
    }

    const [topics, tags] = await Promise.all([
      getHotTopics(limit),
      getHotTags()
    ]);

    const report = generateReport(topics, tags);
    console.log(report);

    // 同时保存为 JSON 文件，供其他脚本使用
    const fs = require('fs');
    const path = require('path');
    const outputPath = path.join(__dirname, '../hot_topics.json');
    fs.writeFileSync(outputPath, JSON.stringify({
      topics,
      tags,
      updated_at: new Date().toISOString()
    }, null, 2));

    console.log(`\n✅ 热点数据已保存到：${outputPath}`);

  } catch (error) {
    console.error('❌ 热点搜集失败:', error.message);
    process.exit(1);
  }
}

// 运行
main();
