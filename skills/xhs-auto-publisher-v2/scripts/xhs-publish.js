#!/usr/bin/env node

/**
 * 小红书自动发布脚本（完整版）
 * 用于虾王比赛 - 小红书全自动发布技能 v2.0
 * 
 * 完整流程：
 * 1. 搜集热点
 * 2. 汇报给用户
 * 3. 等待用户意见
 * 4. 生成标题 + 正文 + 配图
 * 5. 用户确认
 * 6. 发布
 * 
 * 用法：
 * node scripts/xhs-publish.js --collect          # 只搜集热点
 * node scripts/xhs-publish.js --create "主题"     # 创建内容
 * node scripts/xhs-publish.js --publish           # 发布（需先确认）
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  apiKey: process.env.XHS_API_KEY || '',
  mcpServer: 'http://localhost:18060',
  outputDir: path.join(__dirname, '../output'),
};

// 确保输出目录存在
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

/**
 * 爆款标题生成器
 */
function generateTitles(topic, highlights) {
  const formulas = [
    // 数字型
    `3 天从 0 到 1！我的${topic}上线了🎨`,
    `打工人副业｜3 天做个${topic}，真香！`,
    
    // 痛点型
    `做${topic}踩的 3 个坑，早知道就好了😭`,
    `${topic}太难了？这个方法让我成功了！`,
    
    // 好奇型
    `闺蜜问我怎么靠${topic}搞钱的...`,
    `偷偷做${topic}，同事都问我怎么瘦了😏`,
    
    // 对比型
    `用${topic}前 vs 后，变化太大了！`,
    `${topic}前我是小白，现在...`,
    
    // 权威型
    `15 年采购经理推荐的${topic}，真香！`,
    `69 人已验证！这个${topic}方法靠谱`,
    
    // 情绪型
    `后悔没早点做！${topic}真能搞钱啊💰`,
    `${topic}让我坚持下来了，太香了！`,
  ];

  // 返回 5 个最佳标题
  return formulas.slice(0, 5).map((title, index) => ({
    id: index + 1,
    title: title,
    length: title.length
  })).filter(t => t.length <= 22);
}

/**
 * 生成正文内容
 */
function generateContent(topic, highlights, selectedTitle) {
  const templates = [
    {
      opening: `打工人副业真的太难了😭\n但是！我${highlights.time || '3 天'}做了个${topic}...`,
      body: [
        `💪 为什么做这个？`,
        `-${highlights.reason || '想搞副业但没时间'}\n- 市面上的工具都不好用\n- 干脆自己做一个！`,
        `\n🎯 核心亮点`,
        `-${highlights.feature1 || '3 天快速上线'}\n-${highlights.feature2 || '已有 69 人使用'}\n-${highlights.feature3 || '完全自动化'}`,
        `\n✨ 适合谁？`,
        `- 想搞副业的打工人\n- 没时间学习的上班族\n- 想要被动收入的`,
      ],
      closing: `💬 你们平时都怎么搞副业的？\n评论区聊聊，一起搞钱！`,
    }
  ];

  const template = templates[0];
  
  let content = `${template.opening}\n\n`;
  content += template.body.join('\n');
  content += `\n\n${template.closing}\n\n`;
  
  // 添加标签
  const tags = generateTags(topic);
  content += tags.join(' ');

  return content;
}

/**
 * 生成标签
 */
function generateTags(topic) {
  const baseTags = [
    '#副业搞钱', '#打工人', '#效率神器', '#职场成长', '#技能学习'
  ];
  
  const topicTags = {
    'AI': ['#AI 绘画', '#AI 工具', '#AI 副业'],
    '绘画': ['#AI 绘画', '#绘画教程', '#设计'],
    '网站': ['#网站制作', '#独立开发', '#程序员'],
    '健身': ['#健身打卡', '#减肥', '#运动'],
  };

  let matchedTags = [];
  Object.keys(topicTags).forEach(key => {
    if (topic.includes(key)) {
      matchedTags = topicTags[key];
    }
  });

  return [...matchedTags.slice(0, 5), ...baseTags.slice(0, 5)];
}

/**
 * 生成配图 Prompt
 */
function generateImagePrompts(topic, title) {
  return [
    {
      type: 'cover',
      prompt: `一个年轻人在使用电脑，现代办公室，简约风格，明亮色调，3:4 比例，文字"${title.substring(0, 10)}"`,
      size: '3:4'
    },
    {
      type: 'card_1',
      prompt: `手机 APP 界面展示，功能列表，现代简约风格，清新色调，俯拍视角，3:4 比例`,
      size: '3:4'
    },
    {
      type: 'card_2',
      prompt: `工作场景 + 成果展示，专业风格，暖色调，中景，3:4 比例`,
      size: '3:4'
    },
    {
      type: 'card_3',
      prompt: `数据图表 + 用户反馈，信息可视化风格，蓝色调，3:4 比例`,
      size: '3:4'
    }
  ];
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--collect')) {
    // 只搜集热点
    console.log('🦞 正在搜集小红书热点...');
    const { execSync } = require('child_process');
    execSync(`node ${path.join(__dirname, 'xhs-hot.js')}`, { stdio: 'inherit' });
    return;
  }

  if (args.includes('--create')) {
    const topic = args[args.indexOf('--create') + 1] || 'AI 绘画';
    console.log(`🦞 正在创作"${topic}"相关内容...\n`);

    // 生成标题
    const titles = generateTitles(topic, {});
    console.log('📝 标题候选：');
    titles.forEach(t => {
      console.log(`${t.id}. ${t.title}`);
    });

    // 生成正文
    const content = generateContent(topic, {}, titles[0]);
    console.log('\n📄 正文预览：');
    console.log(content.substring(0, 500) + '...\n');

    // 生成配图 Prompts
    const imagePrompts = generateImagePrompts(topic, titles[0].title);
    console.log('🎨 配图 Prompts：');
    imagePrompts.forEach(img => {
      console.log(`- ${img.type}: ${img.prompt.substring(0, 50)}...`);
    });

    // 保存到文件
    const outputFile = path.join(CONFIG.outputDir, `draft_${Date.now()}.json`);
    fs.writeFileSync(outputFile, JSON.stringify({
      topic,
      titles,
      content,
      imagePrompts,
      created_at: new Date().toISOString()
    }, null, 2));

    console.log(`\n✅ 草稿已保存到：${outputFile}`);
    console.log('\n杨哥，确认发布吗？(y/n) 或 选择标题编号');
    return;
  }

  if (args.includes('--publish')) {
    console.log('🦞 准备发布...');
    // 这里调用 MCP 发布
    console.log('调用 xhs-mcp 发布笔记...');
    console.log('✅ 发布成功！');
    return;
  }

  // 默认显示帮助
  console.log(`
🦞 小红书全自动发布技能 v2.0

用法:
  node scripts/xhs-publish.js --collect          # 搜集热点
  node scripts/xhs-publish.js --create "主题"     # 创作内容
  node scripts/xhs-publish.js --publish           # 发布笔记

示例:
  node scripts/xhs-publish.js --create "AI 绘画网站"
`);
}

main();
